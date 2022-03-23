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
ENVAR_SMTP_PORT: str = os.environ[ 'ANXEODALERTS_EMAIL_PORT' ]


def manage_barcode_processing( file_path: str, email_address: str ) -> None:

    ## get filename -------------------------------------------------
    path_obj = pathlib.Path( file_path )
    file_name: str = path_obj.name
    log.debug( f'file_name, ``{file_name}``' )

    ## read barcodes ------------------------------------------------
    barcodes: list = []
    with open( file_path, 'r' ) as fh:
        barcodes = fh.readlines()
    log.debug( f'``{len(barcodes)}`` barcodes perceived' )
    
    ## iterate through barcodes
    all_extracted_data: list = ['title', 'barcode', 'birkin_note', 'mmsid', 'holding_id', 'item_pid', 'library_info', 'location_info', 'base_status_info', 'process_type_info', 'bruknow_url'] 
    assert len(all_extracted_data) == 11
    for barcode in barcodes:

        ## call api
        url_data: dict = prepare_api_url( barcode )
        item_data: dict = {}
        try:
            r = requests.get( url_data['api_url'], headers=url_data['headers'] )
            item_data = r.json()
        except Exception as e:
            log.exception( 'problem accessing barcode, ``{barcode}``')

        ## extract data elements
        extracted_data: list = extract_data( barcode, item_data )
        all_extracted_data.append( extracted_data )  # type: ignore

    ## create csv from extracted_data
    file_like_handler = io.StringIO()
    csv.writer( file_like_handler, dialect='excel' ).writerows( all_extracted_data )

    ## email csv
    send_mail( file_like_handler, email_address )

    return

    ## end def manage_barcode_processing()


def send_mail( file_like_handler, email_address: str ) -> None:
    """ Tests build of email with a CSV attachment.
        Called by manage_csv_email() 
        TODO test multiple attachments. """
    ## setup
    EMAIL_SUBJECT: str = 'The Subject'
    # EMAIL_FROM: str = os.environ[ 'ANXEODALERTS__TEST_EMAIL_FROM' ]
    EMAIL_FROM: str = 'donotreply_annex-end-of-day-reports@brown.edu'
    # EMAIL_TO = os.environ[ 'ANXEODALERTS__TEST_EMAIL_TO_STRING' ]
    EMAIL_TO: str = email_address
    MESSAGE_BODY: str = 'The message body.'
    FILE_NAME: str = 'test.csv'  # this could be the name of the file-processed; TODO: multiple files!
    SMTP_SERVER: str = ENVAR_SMTP_HOST
    SMTP_PORT: int = int( ENVAR_SMTP_PORT )
    ## create multipart message
    msg = MIMEMultipart()
    body_part = MIMEText(MESSAGE_BODY, _subtype='plain', _charset='utf-8' )
    # body_part = MIMEText(MESSAGE_BODY, _subtype='plain', _charset='ascii' )
    msg['Subject'] = EMAIL_SUBJECT
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    ## add body to email
    msg.attach(body_part)
    ## add CSV
    file_like_handler.seek( 0 )
    msg.attach( MIMEApplication(file_like_handler.read(), Name=FILE_NAME) )
    ## create SMTP object
    smtp_obj = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    ## send mail
    smtp_obj.sendmail( msg['From'], msg['To'], msg.as_string() )
    smtp_obj.quit()
    return

    ## end def send_mail()


def extract_data( barcode: str, item_data: dict ) -> list:
    """ Returns data-elements for the CSV from either:
        - populated api item_data
        - or, on unsuccessful api-call, just the barcode and note
        """
    ## initialize vars
    ( title, barcode, birkin_note, mmsid, holding_id, item_pid, library_info, location_info, base_status_info, process_type_info, bruknow_url ) = ( '', barcode, '', '', '', '', '', '', '', '', '' )
    if item_data == {}:
        birkin_note = 'unable to query barcode'
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
    log.debug( f'extracted_data, ``{pprint.pformat(extracted_data)}``' )
    assert len(extracted_data) == 11
    return extracted_data
    

def stringify_data( data ) -> str:
    """ Ensures data (in this example sometimes a dict) is returned as a string.
        Called by extract_data() """
    if type( data ) != str:
        data = repr( data )
    return data


def prepare_api_url( barcode: str ) -> dict:
    headers = {}
    api_url = ''
    url_data: dict = {
        'headers': headers, 'api_url': api_url }
    log.debug( 'api url_data prepared' )
    return url_data


def parse_args() -> dict:
    """ Parses arguments when module called via __main__ """
    parser = argparse.ArgumentParser( description='Required: email.' )
    parser.add_argument( '--file_path', '-f', help='file_path required', required=True )
    parser.add_argument( '--email', '-e', help='email required', required=True )
    args: dict = vars( parser.parse_args() )
    return args


if __name__ == '__main__':
    args: dict = parse_args()
    log.debug( f'args, ```{args}```' )
    file_path: str = args['file_path']
    email_address: str = args['email']
    manage_barcode_processing( file_path, email_address )
