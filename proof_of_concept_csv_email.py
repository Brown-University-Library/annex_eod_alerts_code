import argparse, csv, datetime,  io, json, logging, os, pprint, sys
# import email

from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import smtplib


logging.basicConfig(
    # filename=zzz,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.debug( 'logging ready' )


def manage_email( email_address: str ) -> None:
    ## load source-data ---------------------------------------------
    results: list = load_source_data()  # keeps manager function neat
    ## extract necessary data ---------------------------------------
    header_row = ['title', 'mmsid', 'holding_id', 'item_pid', 'library_info', 'location_info', 'base_status_info', 'process_type_info', 'bruknow_url'] 
    assert len( header_row ) == 9
    extracted_results: list = [ header_row ]
    for data in results:
        assert type(data) == dict
        title: str = data['bib_data']['title']  # accessing elements separately so if there's an error, the traceback will show where it occurred
        if len(title) > 30:
            title = f'{title[0:27]}...'
        mmsid: str = stringify_data( data['bib_data']['mms_id'] ) 
        holding_id: str = stringify_data( data['holding_data']['holding_id'] )
        item_pid: str = stringify_data( data['item_data']['pid'] )
        library_info: str = stringify_data( data['item_data']['library'] )
        location_info: str = stringify_data( data['item_data']['location'] )
        base_status_info: str = stringify_data( data['item_data']['base_status'] )
        process_type_info: str = stringify_data( data['item_data']['process_type'] )
        bruknow_url: str = f'<https://bruknow.library.brown.edu/discovery/fulldisplay?docid=alma{mmsid}&vid=01BU_INST:BROWN>'
        extracted_data: list = [
            title, mmsid, holding_id, item_pid, library_info, location_info, base_status_info, process_type_info, bruknow_url ] 
        assert len( extracted_data ) == 9
        extracted_results.append( extracted_data )
    log.debug( f'extracted_results, ``{pprint.pformat(extracted_results)}``' )

    ## build csv ----------------------------------------------------
    file_like_handler = io.StringIO()
    # csv.writer( file_like_handler ).writerows( extracted_results )
    csv.writer( file_like_handler, delimiter=',', quoting=csv.QUOTE_ALL, doublequote=False, escapechar='\\' ).writerows( extracted_results )
    file_like_handler.seek( 0 )
    rows: list = file_like_handler.readlines()
    # log.debug( f'type(rows), ``{type(rows)}``' )
    # log.debug( f'rows, ``{rows}``' )
    for row in rows:
        log.debug( f'row, ``{row}``' )

    ## build email --------------------------------------------------
    send_mail( file_like_handler )
    return


def stringify_data( data ) -> str:
    if type( data ) != str:
        data = repr( data )
    return data


def send_mail( file_like_handler ):

    # ITEM_GET_URL_ROOT: str = os.environ['ANXEODALERTS__ITEM_API_ROOT']

    EMAIL_SUBJECT = 'The Subject'
    EMAIL_FROM = os.environ[ 'ANXEODALERTS__TEST_EMAIL_FROM' ]
    EMAIL_TO = os.environ[ 'ANXEODALERTS__TEST_EMAIL_TO_STRING' ]
    MESSAGE_BODY = 'The message body.'
    # PATH_TO_CSV_FILE = Path to the zip file
    FILE_NAME = 'test.csv'
    SMTP_SERVER = os.environ[ 'ANXEODALERTS__TEST_EMAIL_SMTP_SERVER' ]
    SMTP_PORT = os.environ[ 'ANXEODALERTS__TEST_EMAIL_SMTP_PORT' ]
    # SMTP_USERNAME = Username for SMTP
    # SMTP_PASSWORD = SMTP password

    # Create a multipart message
    msg = MIMEMultipart()
    body_part = MIMEText(MESSAGE_BODY, 'plain')
    msg['Subject'] = EMAIL_SUBJECT
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    # Add body to email
    msg.attach(body_part)

    # # open and read the CSV file in binary
    # with open(PATH_TO_CSV_FILE,'rb') as file:
    # # Attach the file with filename to the email
    #     msg.attach(MIMEApplication(file.read(), Name=FILE_NAME))

    msg.attach( MIMEApplication(file_like_handler.read(), Name=FILE_NAME) )

    # Create SMTP object
    smtp_obj = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    # Login to the server
    # smtp_obj.login(SMTP_USERNAME, SMTP_PASSWORD)

    # Convert the message to a string and send it
    smtp_obj.sendmail(msg['From'], msg['To'], msg.as_string())
    smtp_obj.quit()


def load_source_data() -> list:
    """ Just returns the dict; only purpose is to keep the manager-code readable.
        Called by manage_email() """
    source_lst = [
 {'bib_data': {'author': 'Satō, Kōji,',
   'bib_suppress_from_publishing': 'false',
   'complete_edition': '',
   'date_of_publication': 'Shōwa 41 [1966]',
   'isbn': None,
   'issn': None,
   'link': 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/991036133439706966',
   'mms_id': '991036133439706966',
   'network_number': ['(OCoLC)ocm23041861', '(RPB)b3387895x-01bu_inst'],
   'place_of_publication': 'Kyōto :',
   'publisher_const': 'Tankō Shinsha',
   'title': 'Nihon "test" no dentō zen no seikatsu = The life of Zen /'},
  'holding_data': {'accession_number': '',
   'call_number': 'BQ9265.4 S28x 1966',
   'call_number_type': {'desc': 'Library of Congress classification',
    'value': '0'},
   'copy_id': '',
   'holding_id': '22271456270006966',
   'holding_suppress_from_publishing': 'false',
   'in_temp_location': False,
   'link': 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/991036133439706966/holdings/22271456270006966',
   'permanent_call_number': 'BQ9265.4 S28x 1966',
   'permanent_call_number_type': {'desc': 'Library of Congress classification',
    'value': '0'},
   'temp_call_number': '',
   'temp_call_number_source': '',
   'temp_call_number_type': {'desc': None, 'value': ''},
   'temp_library': {'desc': None, 'value': None},
   'temp_location': {'desc': None, 'value': None},
   'temp_policy': {'desc': None, 'value': ''}},
  'item_data': {'alternative_call_number': '',
   'alternative_call_number_type': {'desc': None, 'value': ''},
   'arrival_date': '2003-08-15Z',
   'awaiting_reshelving': False,
   'barcode': '31236017160014',
   'base_status': {'desc': 'Item in place', 'value': '1'},
   'break_indicator': {'desc': None, 'value': ''},
   'chronology_i': '',
   'chronology_j': '',
   'chronology_k': '',
   'chronology_l': '',
   'chronology_m': '',
   'creation_date': '2021-08-04Z',
   'description': '',
   'edition': None,
   'enumeration_a': '',
   'enumeration_b': '',
   'enumeration_c': '',
   'enumeration_d': '',
   'enumeration_e': '',
   'enumeration_f': '',
   'enumeration_g': '',
   'enumeration_h': '',
   'fulfillment_note': '',
   'imprint': None,
   'internal_note_1': 'api_test__2022-03-21T08:27:25.883491',
   'internal_note_2': 'NON_PUBLIC_NOTE_2_NOTE(ITEM): accessioned at Annex 11/7/2011',
   'internal_note_3': 'NON_PUBLIC_NOTE_3_DONOR: Prof. Eric Sackheim',
   'inventory_number': '',
   'inventory_price': '',
   'is_magnetic': False,
   'language': None,
   'library': {'desc': 'Rockefeller Library', 'value': 'ROCK'},
   'linking_number': '',
   'location': {'desc': 'Annex Storage', 'value': 'RKSTORAGE'},
   'modification_date': '2022-03-21Z',
   'pages': '',
   'pattern_type': {'desc': None, 'value': ''},
   'physical_condition': {'desc': None, 'value': None},
   'physical_material_type': {'desc': 'Book', 'value': 'BOOK'},
   'pid': '23271456250006966',
   'pieces': '',
   'po_line': '',
   'policy': {'desc': 'Circ Regular', 'value': 'CIRCREG'},
   'process_type': {'desc': None, 'value': ''},
   'provenance': {'desc': None, 'value': ''},
   'public_note': '',
   'receiving_operator': 'import',
   'requested': False,
   'statistics_note_1': '',
   'statistics_note_2': '',
   'statistics_note_3': '',
   'storage_location_id': '',
   'type_of_unit': '',
   'year_of_issue': ''},
  'link': 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/991036133439706966/holdings/22271456270006966/items/23271456250006966'},
 {'bib_data': {'author': 'Fisher, W. B.',
   'bib_suppress_from_publishing': 'false',
   'complete_edition': '',
   'date_of_publication': '1968-1991.',
   'isbn': None,
   'issn': None,
   'link': 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/991008041299706966',
   'mms_id': '991008041299706966',
   'network_number': ['RIBG83-B18483',
    '(OCoLC)ocm00745412',
    '(RPB)b11660314-01bu_inst'],
   'place_of_publication': 'Cambridge,',
   'publisher_const': 'University Press',
   'title': 'The Cambridge history of Iran.'},
  'holding_data': {'accession_number': '',
   'call_number': 'DS272 .C34',
   'call_number_type': {'desc': 'Library of Congress classification',
    'value': '0'},
   'copy_id': '1',
   'holding_id': '22308210420006966',
   'holding_suppress_from_publishing': 'false',
   'in_temp_location': False,
   'link': 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/991008041299706966/holdings/22308210420006966',
   'permanent_call_number': 'DS272 .C34',
   'permanent_call_number_type': {'desc': 'Library of Congress classification',
    'value': '0'},
   'temp_call_number': '',
   'temp_call_number_source': '',
   'temp_call_number_type': {'desc': None, 'value': ''},
   'temp_library': {'desc': None, 'value': None},
   'temp_location': {'desc': None, 'value': None},
   'temp_policy': {'desc': None, 'value': ''}},
  'item_data': {'alternative_call_number': '',
   'alternative_call_number_type': {'desc': None, 'value': ''},
   'arrival_date': '1995-03-16Z',
   'awaiting_reshelving': False,
   'barcode': '31236001750465',
   'base_status': {'desc': 'Item in place', 'value': '1'},
   'break_indicator': {'desc': None, 'value': ''},
   'chronology_i': '',
   'chronology_j': '',
   'chronology_k': '',
   'chronology_l': '',
   'chronology_m': '',
   'creation_date': '2021-08-04Z',
   'description': 'v.4',
   'edition': None,
   'enumeration_a': '',
   'enumeration_b': '',
   'enumeration_c': '',
   'enumeration_d': '',
   'enumeration_e': '',
   'enumeration_f': '',
   'enumeration_g': '',
   'enumeration_h': '',
   'fulfillment_note': '',
   'imprint': None,
   'internal_note_1': 'api_test__2022-03-22T09:06:09.051566',
   'internal_note_2': '',
   'internal_note_3': '',
   'inventory_number': '',
   'inventory_price': '',
   'is_magnetic': False,
   'language': None,
   'library': {'desc': 'Rockefeller Library', 'value': 'ROCK'},
   'linking_number': '',
   'location': {'desc': 'Stacks', 'value': 'STACKS'},
   'modification_date': '2022-03-22Z',
   'pages': '',
   'pattern_type': {'desc': None, 'value': ''},
   'physical_condition': {'desc': None, 'value': None},
   'physical_material_type': {'desc': 'Book', 'value': 'BOOK'},
   'pid': '23308210350006966',
   'pieces': '',
   'po_line': '',
   'policy': {'desc': 'Circ Regular', 'value': 'CIRCREG'},
   'process_type': {'desc': None, 'value': ''},
   'provenance': {'desc': None, 'value': ''},
   'public_note': '',
   'receiving_operator': 'import',
   'requested': None,
   'statistics_note_1': 'STAT_NOTE_1_ACCESSION #: LA',
   'statistics_note_2': '',
   'statistics_note_3': '',
   'storage_location_id': '',
   'type_of_unit': '',
   'year_of_issue': ''},
  'link': 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/991008041299706966/holdings/22308210420006966/items/23308210350006966'}
  ]
    return source_lst


def parse_args() -> dict:
    """ Parses arguments when module called via __main__ """
    parser = argparse.ArgumentParser( description='Required: email.' )
    parser.add_argument( '--email', '-e', help='email required', required=True )
    args: dict = vars( parser.parse_args() )
    return args


if __name__ == '__main__':
    args: dict = parse_args()
    log.debug( f'args, ```{args}```' )
    email_address: str = args['email']
    manage_email( email_address )
