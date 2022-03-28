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

import argparse, datetime, logging, os, pathlib, pprint, time


logging.basicConfig(
    # filename=zzz,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.debug( 'logging ready' )


def manage_monthly_file_creation( date_str: str, source_dir_path: str, output_file_path: str ) -> None:
    """ Manages file combining. """
    ## get files in source-dir
    target_files: list = get_target_files( date_str, source_dir_path)
    qhacs_bucket = []
    qhref_bucket = []
    qsacs_bucket = []
    qsref_bucket = []
    for path_obj in target_files:
        contents = []
        # bucket: list = []
        with open( path_obj, 'r' ) as file_handler:
            contents = file_handler.readlines()
        if 'qhacs' in path_obj.name.lower():
            bucket: list = qhacs_bucket
        elif 'qhref' in path_obj.name.lower():
            bucket: list = qhref_bucket
        elif 'qsacs' in path_obj.name.lower():
            bucket: list = qsacs_bucket
        else:
            bucket: list = qsref_bucket
        for entry in contents:
            barcode = entry.strip()
            if barcode not in bucket:
                bucket.append( barcode)
            else:
                log.debug( f'not adding barcode, ``{barcode}`` it already exists in the target bucket' )
    log.debug( f'len(qhacs_bucket), ``{len(qhacs_bucket)}``' )
    log.debug( f'len(qhref_bucket), ``{len(qhref_bucket)}``' )
    log.debug( f'len(qsacs_bucket), ``{len(qsacs_bucket)}``' )
    log.debug( f'len(qsref_bucket), ``{len(qsref_bucket)}``' )

    return
    
    ## end def manage_monthly_file_creation()


def get_target_files( date_str: str, source_dir_path: str ) -> list:
    """ Returns list of file_paths that meet the date-specification. 
        Called by manage_monthly_file_creation() """
    all_files: list = list( pathlib.Path(source_dir_path).iterdir() )
    filtered_files = [ f for f in all_files if pathlib.Path(f).is_file()  ]  # ignores folders
    # log.debug( f'filtered_files, ``{pprint.pformat(filtered_files)}``' )
    date_obj_from_arg  = datetime.datetime.strptime( date_str, '%Y-%m-%d' ).date()
    year_arg = date_obj_from_arg.year
    # log.debug( f'year_arg, ``{year_arg}``' )
    month_arg = date_obj_from_arg.month
    # log.debug( f'month_arg, ``{month_arg}``' )
    target_files: list = []
    for path_obj in filtered_files:
        file_name = path_obj.name
        parts = file_name.split( '_' )
        if parts[0] != 'ORIG':
            continue
        # log.debug( 'HERE-A' )
        if parts[1] not in [ 'QHACS', 'QHREF', 'QSACS', 'QSREF' ]:
            continue
        # log.debug( 'HERE-B' )
        file_date_string_and_extension = parts[2]
        # log.debug( f'file_date_string_and_extension, ``{file_date_string_and_extension}``' )
        file_date_str = file_date_string_and_extension.split('T')[0]
        # log.debug( f'file_date_str, ``{file_date_str}``' )
        date_obj_from_file_name  = datetime.datetime.strptime( file_date_str, '%Y-%m-%d' ).date()
        if date_obj_from_file_name.year == date_obj_from_arg.year and date_obj_from_file_name.month == date_obj_from_arg.month:
            target_files.append( path_obj )
        else:
            continue
    log.debug( f'target_files, ``{pprint.pformat(target_files)}``' )
    return target_files

    ## end def get_target_files()


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
