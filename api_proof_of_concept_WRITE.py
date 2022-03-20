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
import requests


logging.basicConfig(
    # filename=zzz,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)


ITEM_GET_URL_ROOT: str = os.environ['ANXEODALERTS__ITEM_API_ROOT']
ITEM_PUT_URL_ROOT: str = os.environ['ANXEODALERTS__ITEM_PUT_API_ROOT']
API_KEY_WRITE: str = os.environ['ANXEODALERTS__ITEM_API_KEY_WRITE']


def manage_update( barcode: str ) -> None:
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
