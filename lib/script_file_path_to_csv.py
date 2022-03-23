import argparse, logging, pathlib
import requests


logging.basicConfig(
    # filename=zzz,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.debug( 'logging ready' )


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
    extracted_data: list = ['title', 'barcode', 'birkin_note', 'mmsid', 'holding_id', 'item_pid', 'library_info', 'location_info', 'base_status_info', 'process_type_info', 'bruknow_url'] 
    assert len(extracted_data) == 11
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

    ## create csv from extracted_data

    ## email csv

    pass
    return


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
        pass
    extracted_data = [ title, barcode, birkin_note, mmsid, holding_id, item_pid, library_info, location_info, base_status_info, process_type_info, bruknow_url ]
    return extracted_data
    
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
