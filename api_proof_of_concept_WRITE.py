'''
Proof-of-concept showing results of updating an item via the alma items-api.

Usage...
- % cd ./annex_eod_alerts_code
- % source ../env/bin/activate
- % python3 ./api_proof_of_concept_WRITE.py --mmsid 123 --holding-id 456 --item-pid 789

Steps...
- parse barcode argument
- hit barcode url
- pull out mmsid, holdings_id, and item_pid
- construct payload
- hit item-put url
- confirm response
'''

import argparse, json, logging, os, pprint
from socket import timeout
import requests


logging.basicConfig(
    # filename=zzz,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.debug( 'logging ready' )


ITEM_GET_URL_ROOT: str = os.environ['ANXEODALERTS__ITEM_API_ROOT']
ITEM_PUT_URL_ROOT: str = os.environ['ANXEODALERTS__ITEM_PUT_API_ROOT']
API_KEY_WRITE: str = os.environ['ANXEODALERTS__ITEM_API_KEY_WRITE']


def manage_update( barcode: str ) -> None:
    ## call item-get api --------------------------------------------
    log.debug( f'ITEM_GET_URL_ROOT, ``{ITEM_GET_URL_ROOT}``' )
    get_url: str = f'{ITEM_GET_URL_ROOT}?item_barcode={barcode}&apikey={API_KEY_WRITE}'
    # log.debug( f'get_url, ``{get_url}``' )
    r = requests.get( get_url, headers={'Accept': 'application/json'}, timeout=10 )
    ## inspect result -----------------------------------------------
    log.debug( f'item-get r.status_code, ``{r.status_code}``' )
    # log.debug( f' r.content, ``{r.content}``')
    data: dict = r.json()
    log.debug( f'original data, ``{pprint.pformat(data)}``' )
    ## extract data -------------------------------------------------
    internal_note_1 = data['item_data']['internal_note_1']
    library_info = data['item_data']['library']
    location_info = data['item_data']['location']
    base_status_info: str = data['item_data']['base_status']
    process_type_info = data['item_data']['process_type']
    # 
    extracted_data: dict = {
        'internal_note_1': internal_note_1,
        'library_info': library_info,
        'location_info': location_info,
        'base_status_info': base_status_info,
        'process_type_info': process_type_info, }
    log.debug( f'extracted_data, ``{pprint.pformat(extracted_data)}``' )
    ## change data --------------------------------------------------
    
    ## call item-put api

    ## inspect response
    
    return


def parse_args() -> dict:
    """ Parses arguments when module called via __main__ """
    parser = argparse.ArgumentParser( description='Required: barcode.' )
    parser.add_argument( '--barcode', '-b', help='barcode required', required=True )
    args: dict = vars( parser.parse_args() )
    return args


if __name__ == '__main__':
    args: dict = parse_args()
    log.debug( f'args, ```{args}```' )
    barcode: str = args['barcode']
    manage_update( barcode )
