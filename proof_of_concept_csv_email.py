import argparse, csv, datetime,  io, json, logging, os, pprint, sys
import email


logging.basicConfig(
    # filename=zzz,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.debug( 'logging ready' )


def manage_email( email_address: str ) -> None:
    ## load source-data
    data: dict = load_source_data()  # keeps manager function neat

    ## extract necessary data
    title = data['bib_data']['title']
    mmsid = data['bib_data']['mms_id']
    holding_id = data['holding_data']['holding_id']
    item_pid = data['item_data']['pid']
    library_info = data['item_data']['library']  # for this proof-of-concept, we don't need library, location, status, and process-type; this just documents accessing those
    location_info = data['item_data']['location']
    base_status_info: str = data['item_data']['base_status']
    process_type_info = data['item_data']['process_type']
    extracted_data: dict = {  
        'title': title,
        'mmsid': mmsid,
        'holding_id': holding_id,
        'item_pid': item_pid,
        'library_info': library_info,
        'location_info': location_info,
        'base_status_info': base_status_info,
        'process_type_info': process_type_info, }
    log.debug( f'extracted_data, ``{pprint.pformat(extracted_data)}``' )

    ## experimentation ----------------------------------------------
    test_data = [ 
        [ 'first_name', 'last_name' ],  # header-row
        [ 'f-aaa', 'l-aaa' ],
        [ 'f-b"b"b', "l-b'b'b" ],
        [ 'f-bbb_iñtërnâtiønàlĭzætiФn', 'l-ccc' ],
        [ 123, '456' ]
     ]
    file_like_handler = io.StringIO()

    # csv.writer( file_like_handler ).writerows( test_data )
    # csv.writer( file_like_handler, dialect='unix' ).writerows( test_data )
    # csv.writer( file_like_handler, dialect='excel' ).writerows( test_data )

    # csv.register_dialect( 'dialect_test', delimiter=':', quoting=csv.QUOTE_ALL )
    # csv.writer( file_like_handler, dialect='dialect_test' ).writerows( test_data )

    # csv.writer( file_like_handler, delimiter=',', quoting=csv.QUOTE_ALL ).writerows( test_data )
    csv.writer( file_like_handler, delimiter=',', quoting=csv.QUOTE_NONNUMERIC, doublequote=False, escapechar='\\' ).writerows( test_data )
    # csv.writer( file_like_handler, delimiter=',', quoting=csv.QUOTE_NONE ).writerows( test_data )
    
    # log.debug( f'csv, ``{csv}``' )
    # log.debug( f'file_like_handler, ``{file_like_handler}``' )
    file_like_handler.seek( 0 )
    data_string = file_like_handler.read()
    log.debug( f'data_string, ``{data_string}``' )



    return


def load_source_data():
    """ Just returns the dict; only purpose is to keep the manager-code readable.
        Called by manage_email() """
    source_dct = {'bib_data': {'author': 'Satō, Kōji,',
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
    'title': 'Nihon no dentō zen no seikatsu = The life of Zen /'},
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
    'link': 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/991036133439706966/holdings/22271456270006966/items/23271456250006966'}
    return source_dct


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
