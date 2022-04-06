'''
This script:
- Takes a filepath and email address
- Loads up the barcodes, and for each barcode...
    - Performs a GET lookup and stores the original data
    - Executes a PUT change and stores the resulting data
- Constructs a CSV with results
- Emails the CSV as en attachment

Usage...
- assumes:
    - five required environmental-variables are set (see below, after logging config)
- % cd ./annex_eod_alerts_code
- % source ../env/bin/activate
- % python3 ./lib/script_file_path_to_csv.py --email the-email-address --file_path /the/path.txt
'''

import argparse, copy, csv, io, logging, os, pathlib, pprint, smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests


logging.basicConfig(
    # filename=zzz,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.debug( 'logging ready' )


ENVAR_SMTP_HOST: str = os.environ[ 'ANXEODALERTS__EMAIL_HOST' ]
ENVAR_SMTP_PORT: str = os.environ[ 'ANXEODALERTS__EMAIL_PORT' ]
ENVAR_ITEM_GET_URL_ROOT: str = os.environ['ANXEODALERTS__ITEM_API_ROOT']
ENVAR_ITEM_PUT_URL_ROOT: str = os.environ['ANXEODALERTS__ITEM_PUT_API_ROOT']
ENVAR_API_KEY: str = os.environ['ANXEODALERTS__ITEM_API_KEY_WRITE']


def manage_barcode_processing( file_path: str, emails: list ) -> None:

    ## get filename -------------------------------------------------
    path_obj = pathlib.Path( file_path )
    file_name: str = path_obj.name
    log.debug( f'file_name, ``{file_name}``' )

    ## get file_type ------------------------------------------------
    file_type: str = determine_file_type( file_name )  # used when evaluating GET data

    ## read barcodes ------------------------------------------------
    barcodes: list = []
    with open( file_path, 'r' ) as fh:
        barcodes = fh.readlines()
    log.debug( f'``{len(barcodes)}`` barcodes perceived' )

    ## clean barcodes -----------------------------------------------
    cleaned_barcodes: list = []  # removes newlines and possible empty line
    for barcode in barcodes:
        barcode = barcode.strip()
        if barcode:
            cleaned_barcodes.append( barcode )
    barcodes = cleaned_barcodes
    
    ## iterate through barcodes
    all_extracted_data: list = [
        ['title', 'barcode', 'birkin_note', 'library_before', 'library_todo', 'library_after', 'location_before', 'location_todo', 'location_after', 'base_status_before', 'base_status_todo', 'base_status_after', 'process_type_before', 'process_type_todo', 'process_type_after', 'bruknow_url']
    ] 
    assert len( all_extracted_data[0] ) == 16
    for barcode in barcodes:

        ## call api -------------------------------------------------
        url_data: dict = prepare_api_url( barcode )
        item_data: dict = {}
        try:
            r = requests.get( url_data['api_url'], headers=url_data['headers'], timeout=20 )
            item_data = r.json()
            log.debug( f'returned-get-api data, ``{pprint.pformat(item_data)}``' )
        except Exception as e:
            log.exception( 'problem accessing barcode, ``{barcode}``')

        ## evaluate data --------------------------------------------
        payload_data: dict = evaluate_data( file_type, item_data )

        ## try update if needed -------------------------------------
        updated_item_data: dict = {}
        if payload_data:
            updated_item_data = try_update( payload_data )

        ## extract data elements ------------------------------------
        extracted_data: list = extract_data( barcode, item_data, updated_item_data )

        all_extracted_data.append( extracted_data )  # type: ignore
        log.debug( f'all_extracted_data (in-process), ``{pprint.pformat(all_extracted_data)}``' )

    ## create csv from extracted_data
    log.debug( f'all_extracted_data (FINAL), ``{pprint.pformat(all_extracted_data)}``' )
    file_like_handler = io.StringIO()
    csv.writer( file_like_handler, dialect='excel' ).writerows( all_extracted_data )

    ## email csv
    send_mail( file_like_handler, file_name, emails )

    return

    ## end def manage_barcode_processing()


# -------------------------------------------------------------------
# helper functions
# -------------------------------------------------------------------


def try_update( payload_data: dict ) -> dict:
    """ Will try update here.
        Called by manage_barcode_processing() """
    log.debug( 'about to try PUT...' )
    log.debug( f'payload_data, ``{pprint.pformat(payload_data)}``' )
    ## setup --------------------------------------------------------
    mmsid: str = stringify_data( payload_data['bib_data']['mms_id'] ) 
    holding_id: str = stringify_data( payload_data['holding_data']['holding_id'] )
    item_pid: str = stringify_data( payload_data['item_data']['pid'] )
    ## call item-put api --------------------------------------------
    put_url_base = ENVAR_ITEM_PUT_URL_ROOT.replace( '{MMSID}', mmsid ).replace( '{HOLDING_ID}', holding_id ).replace( '{ITEM_PID}', item_pid )
    put_url = f'{put_url_base}?generate_description=false&apikey={ENVAR_API_KEY}'
    # log.debug( f'put_url, ``{put_url}``' )
    header_dct = {'Accept': 'application/json', 'Content-Type': 'application/json'}  # 'Content-Type' not needed for GET
    returned_put_data: dict = {}
    try:
        r = requests.put( put_url, json=payload_data, headers=header_dct, timeout=20 )
        ## inspect result -----------------------------------------------
        # log.debug( f' r.content, ``{r.content}``')
        returned_put_data: dict = r.json()
    except Exception as e:
        log.exception( f'Problem on PUT, ``{repr(e)}``' )
    log.debug( f'returned_put_data, ``{pprint.pformat(returned_put_data)}``' )
    return returned_put_data


def evaluate_data( file_type: str, item_data: dict ) -> dict:
    """ Evaluates existing item_data, updates item_data REFERENCE, for CSV, _and_ returns update payload-dict. 
        Called by manage_barcode_processing() 
        Based on March 25, 2022 email logic. """
    log.debug( f'item_data at beginning of evaluate, ``{pprint.pformat(item_data)}``' )
    ## check for no-barcode-found -----------------------------------

    if 'errorList' in item_data.keys():
        # log.debug( 'hereA' )
        if 'error' in item_data['errorList']:
            # log.debug( 'hereB' )
            errors: list = item_data['errorList']['error']
            for error in errors:
                # log.debug( 'hereC' )
                if 'errorMessage' in error.keys():
                    # log.debug( 'hereD' )
                    # if error['errorMessage'] == 'no items found for barcode'.lower():
                    if 'no items found for barcode' in error['errorMessage'].lower():
                        # log.debug( 'hereE' )
                        return {}
                        
    ## setup --------------------------------------------------------
    # payload_data: dict = item_data.copy()  # copy of GET response
    # payload_data_reference: dict = item_data.copy()  # to see if there are any updates to perform
    payload_data: dict = copy.deepcopy( item_data )
    payload_data_reference: dict = copy.deepcopy( item_data )
    assert payload_data == payload_data_reference
    item_data['item_data']['library_eval'] = 'no-change'
    item_data['item_data']['location_eval'] = 'no-change'
    item_data['item_data']['base_status_eval'] = 'no-change'
    item_data['item_data']['process_type_eval'] = 'no-change'    
    ## handle process_type ------------------------------------------
    continue_after_process_type_flag: bool = False
    process_type: dict = item_data['item_data']['process_type']
    log.debug( f'process_type for evaluation, ``{process_type}``' )
    if process_type == {'desc': 'Technical - Migration', 'value': 'TECHNICAL' }:
        log.debug( 'found "technical" process_type info' )
        payload_data['item_data']['process_type'] = {'desc': None, 'value': ''}
        item_data['item_data']['process_type_eval'] = "should change to ``{'desc': None, 'value': ''}``"
        continue_after_process_type_flag = True
    elif process_type == {'desc': None, 'value': '' }:
        log.debug( 'found None process_type info, so continuing' )
        continue_after_process_type_flag = True
    if continue_after_process_type_flag == True:
        ## handle base_status ---------------------------------------
        base_status_ideal: dict = {'desc': 'Item in place', 'value': '1'}
        if item_data['item_data']['base_status'] != base_status_ideal:
            payload_data['item_data']['base_status'] = base_status_ideal
            item_data['item_data']['base_status_eval'] = f'should change to ``{base_status_ideal}``'
        ## handle library ------------------------------------------
        library_ideal: dict = {}
        if file_type == 'QHACS' or file_type == 'QHREF':
            library_ideal: dict = {'desc': 'John Hay Library', 'value': 'HAY'}
        elif file_type == 'QSACS' or file_type == 'QSREF':
            library_ideal: dict = {'desc': 'Rockefeller Library', 'value': 'ROCK'}
        if item_data['item_data']['library'] != library_ideal:
            payload_data['item_data']['library'] = library_ideal
            item_data['item_data']['library_eval'] = f'should change to ``{library_ideal}``'
        ## handle location ------------------------------------------
        location_ideal: dict = {}
        if file_type == 'QHACS' or file_type == 'QHREF':
            location_ideal: dict = {'desc': 'Annex Hay', 'value': 'HAYSTOR'}
        elif file_type == 'QSACS' or file_type == 'QSREF':
            location_ideal: dict = { 'desc': 'Annex Storage', 'value': 'RKSTORAGE' }
        if item_data['item_data']['location'] != location_ideal:
            payload_data['item_data']['location'] = location_ideal
            item_data['item_data']['location_eval'] = f'should change to ``{location_ideal}``'
    ## see if payload_data has been updated -------------------------
    if payload_data == payload_data_reference:  # no change, so let's return a form of None
        log.debug( 'no changes made, so returning empty payload' )
        payload_data = {}
    else:
        log.debug( 'payload updated' )
    log.debug( f'item_data at END of evaluate, ``{pprint.pformat(item_data)}``' )
    return payload_data


def determine_file_type( file_name: str ) -> str:
    """ Returns the file_type from inspecting the file-name. 
        Called by: manage_barcode_processing() """
    file_type: str = 'init'
    for type in [ 'QHACS', 'QHREF', 'QSACS', 'QSREF' ]:
        if type in file_name:
            file_type = type
            break
    log.debug( f'file_type, ``{file_type}``' )
    return file_type


def prepare_api_url( barcode: str ) -> dict:
    headers = {}
    api_url: str = f'{ENVAR_ITEM_GET_URL_ROOT}?item_barcode={barcode}&apikey={ENVAR_API_KEY}'
    headers: dict = {'Accept': 'application/json'}
    url_data: dict = {
        'headers': headers, 'api_url': api_url }
    log.debug( 'api url_data prepared' )
    return url_data


def extract_data( barcode: str, item_data: dict, updated_item_data: dict ) -> list:
    """ Returns data-elements for the CSV from either:
        - populated api item_data
        - or, on unsuccessful api-call, just the barcode and note
        """
    try:
        ## initialize vars
        ( title, barcode, birkin_note, library_before, library_todo, library_after, location_before, location_todo, location_after, base_status_before, base_status_todo, base_status_after, process_type_before, process_type_todo, process_type_after, bruknow_url ) = ( '', barcode, '', '', '', '', '', '', '', '', '', '', '', '', '', '' )
        if item_data == {}:
            log.debug( 'item_data is {}' )
            birkin_note: str = 'could not query barcode'
        elif 'errorsExist' in item_data.keys():
            log.debug( 'errors exist in item_data' )
            birkin_note: str = 'error in query response'
            if 'errorList' in item_data.keys():
                # log.debug( 'hereA' )
                if 'error' in item_data['errorList']:
                    # log.debug( 'hereB' )
                    errors: list = item_data['errorList']['error']
                    for error in errors:
                        # log.debug( 'hereC' )
                        if 'errorMessage' in error.keys():
                            # log.debug( 'hereD' )
                            # if error['errorMessage'] == 'no items found for barcode'.lower():
                            if 'no items found for barcode' in error['errorMessage'].lower():
                                # log.debug( 'hereE' )
                                birkin_note = 'no match found for barcode'
                                break
                            else:
                                err_msg: str = error['errorMessage']
                                birkin_note = f'update-error-response, ``{err_msg}``' 
                                break
            log.info( f'item_data on extraction-problem, ``{pprint.pformat(item_data)}``' )
        elif 'errorsExist' in updated_item_data.keys():
            birkin_note: str = f'update error-response, ``{repr(updated_item_data)}``'
        else:  ## all should be good
            title: str = item_data['bib_data']['title']  # accessing elements separately so if there's an error, the traceback will show where it occurred
            if len(title) > 30:
                title = f'{title[0:27]}...'
            mmsid: str = stringify_data( item_data['bib_data']['mms_id'] ) 
            holding_id: str = stringify_data( item_data['holding_data']['holding_id'] )
            item_pid: str = stringify_data( item_data['item_data']['pid'] )
            ##
            library_before: str = stringify_data( item_data['item_data']['library'] )
            library_todo: str = item_data['item_data']['library_eval']
            library_after: str = 'no-change-made'
            if updated_item_data:
                if updated_item_data['item_data']['library'] != item_data['item_data']['library']:
                    library_after = stringify_data( updated_item_data['item_data']['library'] )
            ##
            location_before: str = stringify_data( item_data['item_data']['location'] )
            location_todo: str = item_data['item_data']['location_eval']
            location_after: str = 'no-change-made'
            if updated_item_data:
                if updated_item_data['item_data']['location'] != item_data['item_data']['location']:
                    location_after = stringify_data( updated_item_data['item_data']['location'] )
            ##
            base_status_before: str = stringify_data( item_data['item_data']['base_status'] )
            base_status_todo: str = item_data['item_data']['base_status_eval']
            base_status_after: str = 'no-change-made'
            if updated_item_data:
                if updated_item_data['item_data']['base_status'] != item_data['item_data']['base_status']:
                    base_status_after = stringify_data( updated_item_data['item_data']['base_status'] )
            ##
            process_type_before: str = stringify_data( item_data['item_data']['process_type'] )
            process_type_todo: str = item_data['item_data']['process_type_eval']
            process_type_after: str = 'no-change-made'
            if updated_item_data:
                if updated_item_data['item_data']['process_type'] != item_data['item_data']['process_type']:
                    process_type_after = stringify_data( updated_item_data['item_data']['process_type'] )
            ##
            bruknow_url: str = f'<https://bruknow.library.brown.edu/discovery/fulldisplay?docid=alma{mmsid}&vid=01BU_INST:BROWN>'
        extracted_data = [ title, barcode, birkin_note, library_before, library_todo, library_after, location_before, location_todo, location_after, base_status_before, base_status_todo, base_status_after, process_type_before, process_type_todo, process_type_after, bruknow_url ]
    except Exception as e:
        log.exception( f'problem extracting data from item_data, ``{pprint.pformat(item_data)}``' )
        raise Exception( 'problem extracting data; see logs' )
    log.debug( f'extracted_data, ``{pprint.pformat(extracted_data)}``' )
    assert len(extracted_data) == 16
    return extracted_data

    ## end def extract_data()


# def extract_data( barcode: str, item_data: dict, updated_item_data: dict ) -> list:
#     """ Returns data-elements for the CSV from either:
#         - populated api item_data
#         - or, on unsuccessful api-call, just the barcode and note
#         """
#     try:
#         ## initialize vars
#         ( title, barcode, birkin_note, library_before, library_todo, library_after, location_before, location_todo, location_after, base_status_before, base_status_todo, base_status_after, process_type_before, process_type_todo, process_type_after, bruknow_url ) = ( '', barcode, '', '', '', '', '', '', '', '', '', '', '', '', '', '' )
#         if item_data == {}:
#             birkin_note: str = 'could not query barcode'
#         elif 'errorsExist' in item_data.keys():
#             birkin_note: str = 'error in query response'
#             if 'errorList' in item_data.keys():
#                 # log.debug( 'hereA' )
#                 if 'error' in item_data['errorList']:
#                     # log.debug( 'hereB' )
#                     errors: list = item_data['errorList']['error']
#                     for error in errors:
#                         # log.debug( 'hereC' )
#                         if 'errorMessage' in error.keys():
#                             # log.debug( 'hereD' )
#                             # if error['errorMessage'] == 'no items found for barcode'.lower():
#                             if 'no items found for barcode' in error['errorMessage'].lower():
#                                 # log.debug( 'hereE' )
#                                 birkin_note = 'no match found for barcode'
#                                 break
#             log.info( f'item_data on extraction-problem, ``{pprint.pformat(item_data)}``' )
#         else:
#             title: str = item_data['bib_data']['title']  # accessing elements separately so if there's an error, the traceback will show where it occurred
#             if len(title) > 30:
#                 title = f'{title[0:27]}...'
#             mmsid: str = stringify_data( item_data['bib_data']['mms_id'] ) 
#             holding_id: str = stringify_data( item_data['holding_data']['holding_id'] )
#             item_pid: str = stringify_data( item_data['item_data']['pid'] )
#             ##
#             library_before: str = stringify_data( item_data['item_data']['library'] )
#             library_todo: str = item_data['item_data']['library_eval']
#             library_after: str = stringify_data( updated_item_data['item_data']['library'] ) if updated_item_data else 'no-change-made'
#             ##
#             location_before: str = stringify_data( item_data['item_data']['location'] )
#             location_todo: str = item_data['item_data']['location_eval']
#             location_after: str = stringify_data( updated_item_data['item_data']['location'] ) if updated_item_data else 'no-change-made'
#             ##
#             base_status_before: str = stringify_data( item_data['item_data']['base_status'] )
#             base_status_todo: str = item_data['item_data']['base_status_eval']
#             base_status_after: str = stringify_data( updated_item_data['item_data']['base_status'] ) if updated_item_data else 'no-change-made'
#             ##
#             process_type_before: str = stringify_data( item_data['item_data']['process_type'] )
#             process_type_todo: str = item_data['item_data']['process_type_eval']
#             process_type_after: str = stringify_data( updated_item_data['item_data']['process_type'] ) if updated_item_data else 'no-change-made'
#             ##
#             bruknow_url: str = f'<https://bruknow.library.brown.edu/discovery/fulldisplay?docid=alma{mmsid}&vid=01BU_INST:BROWN>'
#         extracted_data = [ title, barcode, birkin_note, library_before, library_todo, library_after, location_before, location_todo, location_after, base_status_before, base_status_todo, base_status_after, process_type_before, process_type_todo, process_type_after, bruknow_url ]
#     except Exception as e:
#         log.exception( f'problem extracting data from item_data, ``{pprint.pformat(item_data)}``' )
#         raise Exception( 'problem extracting data; see logs' )
#     log.debug( f'extracted_data, ``{pprint.pformat(extracted_data)}``' )
#     assert len(extracted_data) == 16
#     return extracted_data

#     ## end def extract_data()
    

def stringify_data( data ) -> str:
    """ Ensures data (in this example sometimes a dict) is returned as a string.
        Called by extract_data() """
    if type( data ) != str:
        data = repr( data )
    return data


def send_mail( file_like_handler, file_name: str, emails: list ) -> None:
    """ Tests build of email with a CSV attachment.
        Called by manage_csv_email() 
        TODO test multiple attachments. """
    ## setup --------------------------------------------------------
    EMAIL_SUBJECT: str = 'The Subject'
    EMAIL_FROM: str = 'donotreply_annex-end-of-day-reports@brown.edu'
    # EMAIL_TO: str = email_address
    EMAIL_TO: str = ','.join( emails )  # 'apparent' email-to
    MESSAGE_BODY: str = 'The message body.'
    if '.' in file_name:
        name_parts: list = file_name.split( '.' )
        file_name = f'{name_parts[0]}.csv'
    else:
        file_name = f'{file_name}.csv'
    FILE_NAME: str = file_name
    SMTP_SERVER: str = ENVAR_SMTP_HOST
    SMTP_PORT: int = int( ENVAR_SMTP_PORT )
    ## create multipart message -------------------------------------
    msg = MIMEMultipart()
    body_part = MIMEText(MESSAGE_BODY, _subtype='plain', _charset='utf-8' )
    # body_part = MIMEText(MESSAGE_BODY, _subtype='plain', _charset='ascii' )
    msg['Subject'] = EMAIL_SUBJECT
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    ## add body to email --------------------------------------------
    msg.attach(body_part)
    ## add CSV ------------------------------------------------------
    file_like_handler.seek( 0 )
    msg.attach( MIMEApplication(file_like_handler.read(), Name=FILE_NAME) )
    ## create SMTP object -------------------------------------------
    smtp_obj = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    ## send mail ----------------------------------------------------
    # smtp_obj.sendmail( msg['From'], msg['To'], msg.as_string() )
    smtp_obj.sendmail( msg['From'], emails, msg.as_string() )
    smtp_obj.quit()
    return

    ## end def send_mail()


def parse_args() -> dict:
    """ Parses arguments when module called via __main__ """
    parser = argparse.ArgumentParser( description='Required: file_path and email (comma-separated if multiple).' )
    parser.add_argument( '--file_path', '-f', help='file_path required', required=True )
    parser.add_argument( '--email', '-e', help='email (comma-separated if multiple) required', required=True )
    args: dict = vars( parser.parse_args() )
    return args


if __name__ == '__main__':
    args: dict = parse_args()
    log.debug( f'args, ```{args}```' )
    file_path: str = args['file_path']
    email_str: str = args['email']
    emails: list = email_str.split( ',' )
    log.debug( f'emails, ``{emails}``' )
    manage_barcode_processing( file_path, emails )



