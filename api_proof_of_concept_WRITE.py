'''
Proof-of-concept showing results of updating an item via the Alma API.
This will take a barcode, and update the item's 'internal_note_1' field with a new date-stamp, 
    - if the field is empty, or
    - if the field contains the string `api_test`

Usage...
- assumes:
    - `requests` is in python-environment
    - three environmental-variables are set (see below, after logging config)
- % cd ./annex_eod_alerts_code
- % source ../env/bin/activate
- % python3 ./api_proof_of_concept_WRITE.py --barcode 12345678

Steps...
- parse barcode argument
- call the GET api url to get necessary mmsid, holding_id, and item_pid data
- extract any desired info
- construct the PUT payload by copying the data returned from the GET, and changing a note
- call the PUT api url with the payload
- confirm the response contains the changed note
'''

import argparse, datetime,  json, logging, os, pprint, sys
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
    # log.debug( f'item-get r.status_code, ``{r.status_code}``' )
    # log.debug( f' r.content, ``{r.content}``')
    data: dict = r.json()
    log.debug( f'original data, ``{pprint.pformat(data)}``' )
    ## extract data -------------------------------------------------
    mmsid = data['bib_data']['mms_id']
    holding_id = data['holding_data']['holding_id']
    item_pid = data['item_data']['pid']
    internal_note_1 = data['item_data']['internal_note_1']
    library_info = data['item_data']['library']  # for this proof-of-concept, we don't need library, location, status, and process-type; this just documents accessing those
    location_info = data['item_data']['location']
    base_status_info: str = data['item_data']['base_status']
    process_type_info = data['item_data']['process_type']
    extracted_data: dict = {  
        'mmsid': mmsid,
        'holding_id': holding_id,
        'item_pid': item_pid,
        'internal_note_1': internal_note_1,
        'library_info': library_info,
        'location_info': location_info,
        'base_status_info': base_status_info,
        'process_type_info': process_type_info, }
    log.debug( f'extracted_data, ``{pprint.pformat(extracted_data)}``' )
    ## evaluate data ------------------------------------------------
    new_note = 'init'
    if internal_note_1 == '' or 'api_test' in internal_note_1:
        dt_str: str = datetime.datetime.now().isoformat()
        new_note = f'api_test__{dt_str}'
    else:
        log.warning( 'not updating note; it already contains data' )
        sys.exit()
    ## change data --------------------------------------------------
    payload_dct: dict = data.copy()  # copy of GET response
    payload_dct['item_data']['internal_note_1'] = new_note
    ## call item-put api --------------------------------------------
    put_url_base = ITEM_PUT_URL_ROOT.replace( '{MMSID}', mmsid ).replace( '{HOLDING_ID}', holding_id ).replace( '{ITEM_PID}', item_pid )
    put_url = f'{put_url_base}?generate_description=false&apikey={API_KEY_WRITE}'
    # log.debug( f'put_url, ``{put_url}``' )
    header_dct = {'Accept': 'application/json', 'Content-Type': 'application/json'}  # 'Content-Type' not needed for GET
    r = requests.put( put_url, json=payload_dct, headers=header_dct, timeout=10 )
    ## inspect result -----------------------------------------------
    # log.debug( f' r.content, ``{r.content}``')
    post_put_data: dict = r.json()
    log.debug( f'post_put_data, ``{pprint.pformat(post_put_data)}``' )
    assert post_put_data['item_data']['internal_note_1'] == new_note
    log.info( 'success!' )
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
