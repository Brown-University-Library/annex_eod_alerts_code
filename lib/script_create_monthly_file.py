'''
This script:
- Takes a date, a source-directory-path, and a destination-file-path
- Finds all barcode-files for the given month
- Combines the barcodes into one file and outputs it to the destination

Usage...
- assumes:
    - four environmental-variables are set (see below, after logging config)
- % cd ./annex_eod_alerts_code
- % source ../env/bin/activate
- % python3 ./lib/script_create_monthly_file.py --date 2022-10-01 --source_dir_path /path/to/dir --output_file_path /path/to/file.txt
'''

import argparse, logging
from datetime import date


logging.basicConfig(
    # filename=zzz,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.debug( 'logging ready' )


def manage_monthly_file_creation( date_str: str, sourc_dir_path: str, output_file_path: str ):
    pass



def parse_args() -> dict:
    """ Parses arguments when module called via __main__ """
    parser = argparse.ArgumentParser( description='Required: email.' )
    parser.add_argument( '--date', '-d', help='date required in the form of 2022-10-01', required=True )
    parser.add_argument( '--source_dir_path', '-s', help='source directory-path required', required=True )
    parser.add_argument( '--output_file_path', '-o', help='output file-path required', required=True )
    args: dict = vars( parser.parse_args() )
    return args


if __name__ == '__main__':
    args: dict = parse_args()
    log.debug( f'args, ```{args}```' )
    date_str: str = args['date']
    source_dir_path: str = args['source_dir_path']
    output_file_path: str = args['output_file_path']
    manage_monthly_file_creation( date_str, source_dir_path, output_file_path )
