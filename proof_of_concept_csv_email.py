'''
Proof-of-concept showing how to build a CSV from (hard-coded) Alma-API data -- and then send it.

Usage...
- assumes:
    - two environmental-variables are set (see below, after logging config)
- % cd ./annex_eod_alerts_code
- % source ../env/bin/activate
- % python3 ./proof_of_concept_csv_email.py --email the-email-address

Steps...
- extract necessary/convenient data from Alma item-api responses
- build a CSV using a file-like-object, instead of reading/writing to an actual file-system file
- build the email, attaching the CSV, and send
'''

import argparse, csv, io, logging, os, pprint, smtplib

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


logging.basicConfig(
    # filename=zzz,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.debug( 'logging ready' )


ENVAR_SMTP_SERVER: str = os.environ[ 'ANXEODALERTS__TEST_EMAIL_SMTP_SERVER' ]
ENVAR_SMTP_PORT: str = os.environ[ 'ANXEODALERTS__TEST_EMAIL_SMTP_PORT' ]


def manage_csv_email( email_address: str ) -> None:
    """ Manages creation and sending of CSV file.
        Called by __main__ """
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
        extracted_results.append( extracted_data )  # type: ignore
    log.debug( f'extracted_results, ``{pprint.pformat(extracted_results)}``' )
    ## build csv ----------------------------------------------------
    file_like_handler = io.StringIO()
    csv.writer( file_like_handler, dialect='excel' ).writerows( extracted_results )
    # csv.writer( file_like_handler, delimiter=',', quoting=csv.QUOTE_ALL, doublequote=False, escapechar='\\' ).writerows( extracted_results )
    # file_like_handler.seek( 0 )
    # rows: list = file_like_handler.readlines()
    # for row in rows:
    #     log.debug( f'row, ``{row}``' )
    ## build and send email -----------------------------------------
    send_mail( file_like_handler, email_address )
    return

    ## end def manage_csv_email()


def stringify_data( data ) -> str:
    """ Ensures data (in this example sometimes a dict) is returned as a string.
        Called by manage_csv_email() """
    if type( data ) != str:
        data = repr( data )
    return data


def send_mail( file_like_handler, email_address: str ):
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
    SMTP_SERVER: str = ENVAR_SMTP_SERVER
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


def load_source_data() -> list:
    """ Just returns list of item-response dicts; only purpose is to keep the manager-code readable.
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
    manage_csv_email( email_address )
