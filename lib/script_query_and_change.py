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

import argparse, csv, io, logging, os, pathlib, pprint, smtplib
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
ITEM_PUT_URL_ROOT: str = os.environ['ANXEODALERTS__ITEM_PUT_API_ROOT']
ENVAR_API_KEY: str = os.environ['ANXEODALERTS__ITEM_API_KEY_WRITE']


def manage_barcode_processing( file_path: str, emails: list ) -> None:

    ## get filename -------------------------------------------------
    path_obj = pathlib.Path( file_path )
    file_name: str = path_obj.name
    log.debug( f'file_name, ``{file_name}``' )

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
        ['title', 'barcode', 'birkin_note', 'mmsid', 'holding_id', 'item_pid', 'library_info', 'location_info', 'base_status_info', 'process_type_info', 'bruknow_url']
    ] 
    assert len( all_extracted_data[0] ) == 11
    for barcode in barcodes:

        ## call api
        url_data: dict = prepare_api_url( barcode )
        item_data: dict = {}
        try:
            r = requests.get( url_data['api_url'], headers=url_data['headers'] )
            item_data = r.json()
            # log.debug( f'item_data, ``{pprint.pformat(item_data)}``' )
        except Exception as e:
            log.exception( 'problem accessing barcode, ``{barcode}``')

        ## extract data elements
        extracted_data: list = extract_data( barcode, item_data )
        all_extracted_data.append( extracted_data )  # type: ignore
        # log.debug( f'all_extracted_data (in-process), ``{pprint.pformat(all_extracted_data)}``' )

    ## create csv from extracted_data
    # log.debug( f'all_extracted_data (FINAL), ``{pprint.pformat(all_extracted_data)}``' )
    file_like_handler = io.StringIO()
    csv.writer( file_like_handler, dialect='excel' ).writerows( all_extracted_data )

    ## email csv
    send_mail( file_like_handler, file_name, emails )

    return

    ## end def manage_barcode_processing()


def prepare_api_url( barcode: str ) -> dict:
    headers = {}
    api_url: str = f'{ENVAR_ITEM_GET_URL_ROOT}?item_barcode={barcode}&apikey={ENVAR_API_KEY}'
    headers: dict = {'Accept': 'application/json'}
    url_data: dict = {
        'headers': headers, 'api_url': api_url }
    log.debug( 'api url_data prepared' )
    return url_data


def extract_data( barcode: str, item_data: dict ) -> list:
    """ Returns data-elements for the CSV from either:
        - populated api item_data
        - or, on unsuccessful api-call, just the barcode and note
        """
    try:
        ## initialize vars
        ( title, barcode, birkin_note, mmsid, holding_id, item_pid, library_info, location_info, base_status_info, process_type_info, bruknow_url ) = ( '', barcode, '', '', '', '', '', '', '', '', '' )
        # if item_data == {}:
        #     birkin_note = 'unable to query barcode'
        if 'errorsExist' in item_data.keys():
            birkin_note: str = 'unable to query barcode'
            log.info( f'item_data on extraction-problem, ``{pprint.pformat(item_data)}``' )
        else:
            title: str = item_data['bib_data']['title']  # accessing elements separately so if there's an error, the traceback will show where it occurred
            if len(title) > 30:
                title = f'{title[0:27]}...'
            mmsid: str = stringify_data( item_data['bib_data']['mms_id'] ) 
            holding_id: str = stringify_data( item_data['holding_data']['holding_id'] )
            item_pid: str = stringify_data( item_data['item_data']['pid'] )
            library_info: str = stringify_data( item_data['item_data']['library'] )
            location_info: str = stringify_data( item_data['item_data']['location'] )
            base_status_info: str = stringify_data( item_data['item_data']['base_status'] )
            process_type_info: str = stringify_data( item_data['item_data']['process_type'] )
            bruknow_url: str = f'<https://bruknow.library.brown.edu/discovery/fulldisplay?docid=alma{mmsid}&vid=01BU_INST:BROWN>'
        extracted_data = [ title, barcode, birkin_note, mmsid, holding_id, item_pid, library_info, location_info, base_status_info, process_type_info, bruknow_url ]
    except Exception as e:
        log.exception( f'problem extracting data from item_data, ``{pprint.pformat(item_data)}``' )
        raise Exception( 'problem extracting data; see logs' )
    log.debug( f'extracted_data, ``{pprint.pformat(extracted_data)}``' )
    assert len(extracted_data) == 11
    return extracted_data
    

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
    ## setup
    EMAIL_SUBJECT: str = 'The Subject'
    EMAIL_FROM: str = 'donotreply_annex-end-of-day-reports@brown.edu'
    # EMAIL_TO: str = email_address
    MESSAGE_BODY: str = 'The message body.'
    if '.' in file_name:
        name_parts: list = file_name.split( '.' )
        file_name = f'{name_parts[0]}.csv'
    else:
        file_name = f'{file_name}.csv'
    FILE_NAME: str = file_name
    SMTP_SERVER: str = ENVAR_SMTP_HOST
    SMTP_PORT: int = int( ENVAR_SMTP_PORT )
    ## create multipart message
    msg = MIMEMultipart()
    body_part = MIMEText(MESSAGE_BODY, _subtype='plain', _charset='utf-8' )
    # body_part = MIMEText(MESSAGE_BODY, _subtype='plain', _charset='ascii' )
    msg['Subject'] = EMAIL_SUBJECT
    msg['From'] = EMAIL_FROM
    # msg['To'] = EMAIL_TO
    ## add body to email
    msg.attach(body_part)
    ## add CSV
    file_like_handler.seek( 0 )
    msg.attach( MIMEApplication(file_like_handler.read(), Name=FILE_NAME) )
    ## create SMTP object
    smtp_obj = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    ## send mail
    # smtp_obj.sendmail( msg['From'], msg['To'], msg.as_string() )
    smtp_obj.sendmail( msg['From'], emails, msg.as_string() )
    smtp_obj.quit()
    return

    ## end def send_mail()


# def temp__send_mail( emails: list ) -> None:
#     """ Tests build of email with a CSV attachment.
#         Called by manage_csv_email() 
#         TODO test multiple attachments. """
#     ## setup
#     EMAIL_SUBJECT: str = 'The Subject'
#     # EMAIL_FROM: str = os.environ[ 'ANXEODALERTS__TEST_EMAIL_FROM' ]
#     EMAIL_FROM: str = 'donotreply_annex-end-of-day-reports@brown.edu'
#     # EMAIL_TO = os.environ[ 'ANXEODALERTS__TEST_EMAIL_TO_STRING' ]
#     emails_str: str = ','.join( emails )
#     EMAIL_TO: str = emails_str
#     # EMAIL_TO: list = emails
#     MESSAGE_BODY: str = 'The message body.'
  
#     SMTP_SERVER: str = ENVAR_SMTP_HOST
#     SMTP_PORT: int = int( ENVAR_SMTP_PORT )
#     ## create multipart message
#     msg = MIMEMultipart()
#     # body_part = MIMEText(MESSAGE_BODY, _subtype='plain', _charset='utf-8' )
#     # body_part = MIMEText(MESSAGE_BODY, _subtype='plain', _charset='ascii' )
#     msg['Subject'] = EMAIL_SUBJECT
#     msg['From'] = EMAIL_FROM
#     msg['To'] = EMAIL_TO
#     ## add body to email
#     # msg.attach(body_part)
#     ## create SMTP object
#     smtp_obj = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
#     ## send mail
#     smtp_obj.sendmail( msg['From'], emails, msg.as_string() )
#     smtp_obj.quit()
#     return

#     ## end def temp__send_mail()


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



