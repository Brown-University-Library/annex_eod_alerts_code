'''
This script:
- Takes a date, a source-directory-path, and a destination-file-path
- Finds all barcode-files for the given month (ignores 'day')
- Combines the barcodes into one file and outputs it to the destination

Usage...
- assumes:
    - four environmental-variables are set (see below, after logging config)
- % cd ./annex_eod_alerts_code
- % source ../env/bin/activate
- % python3 ./lib/script_create_monthly_file.py --date 2022-10-01 --source_dir_path /path/to/dir --output_dir_path /path/to/dir
'''

import argparse, datetime, logging, os, pathlib, pprint, time


logging.basicConfig(
    # filename=zzz,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.debug( 'logging ready' )


def manage_monthly_file_creation( date_str: str, source_dir_path: str, output_dir_path: str ) -> None:
    """ Manages file combining. """
    ## get files for the month --------------------------------------
    target_files: list = get_target_files( date_str, source_dir_path)
    ## populate counts for different file-types ---------------------
    ( qhacs_bucket, qhref_bucket, qsacs_bucket, qsref_bucket ) = ( [], [], [], [] )
    update_buckets( target_files, qhacs_bucket, qhref_bucket, qsacs_bucket, qsref_bucket )
    log.debug( f'len(qhacs_bucket), ``{len(qhacs_bucket)}``' )
    log.debug( f'len(qhref_bucket), ``{len(qhref_bucket)}``' )
    log.debug( f'len(qsacs_bucket), ``{len(qsacs_bucket)}``' )
    log.debug( f'len(qsref_bucket), ``{len(qsref_bucket)}``' )
    ## write out different file-types -------------------------------
    date_obj_from_arg  = datetime.datetime.strptime( date_str, '%Y-%m-%d' ).date()
    buckets = [ qhacs_bucket, qhref_bucket, qsacs_bucket, qsref_bucket ]
    for i, file_type in enumerate( ['QHACS', 'QHREF', 'QSACS', 'QSREF'] ):
        output_filename = f'COMBINED_{date_obj_from_arg.year}-{date_obj_from_arg.month}_{file_type}_BARCODES.txt'
        log.debug( f'output_filename, ``{output_filename}``' )
        output_filepath = f'{output_dir_path}/{output_filename}'
        log.debug( f'output_filepath, ``{output_filepath}``' )
        write_data( output_filepath, buckets[i]  )
    return

    ## end def manage_monthly_file_creation()


def get_target_files( date_str: str, source_dir_path: str ) -> list:
    """ Returns list of file_paths that meet the date-specification. 
        Called by manage_monthly_file_creation() """
    all_files: list = list( pathlib.Path(source_dir_path).iterdir() )
    filtered_files = [ f for f in all_files if pathlib.Path(f).is_file()  ]  # ignores folders
    # log.debug( f'filtered_files, ``{pprint.pformat(filtered_files)}``' )
    date_obj_from_arg  = datetime.datetime.strptime( date_str, '%Y-%m-%d' ).date()
    target_files: list = []
    for path_obj in filtered_files:
        file_name = path_obj.name
        parts = file_name.split( '_' )  # files are in the format: `ORIG_QHACS_2021-10-01T08-30-05.dat`
        if parts[0] != 'ORIG':
            continue
        if parts[1] not in [ 'QHACS', 'QHREF', 'QSACS', 'QSREF' ]:
            continue
        file_date_string_and_extension = parts[2]
        file_date_str = file_date_string_and_extension.split('T')[0]  # gets date; ignores time
        date_obj_from_file_name  = datetime.datetime.strptime( file_date_str, '%Y-%m-%d' ).date()
        if date_obj_from_file_name.year == date_obj_from_arg.year and date_obj_from_file_name.month == date_obj_from_arg.month:
            target_files.append( path_obj )
        else:
            continue
    log.debug( f'target_files, ``{pprint.pformat(target_files)}``' )
    return target_files

    ## end def get_target_files()


def update_buckets( target_files: list, qhacs_bucket: list, qhref_bucket: list, qsacs_bucket: list, qsref_bucket: list ) -> None:
    """ Adds _new_ barcodes to the appropriate bucket-reference.
        Doesn't 'return' anything, but the bucket references in manage_monthly_file_creation() are updated.
        Called by manage_monthly_file_creation() """
    for path_obj in target_files:
        contents = []
        with open( path_obj, 'r' ) as file_handler:
            contents = file_handler.readlines()
        if 'qhacs' in path_obj.name.lower():
            bucket: list = qhacs_bucket
            output_file_name = f''
        elif 'qhref' in path_obj.name.lower():
            bucket: list = qhref_bucket
        elif 'qsacs' in path_obj.name.lower():
            bucket: list = qsacs_bucket
        else:
            bucket: list = qsref_bucket
        for barcode in contents:
            # barcode = entry.strip()  # no; works if we keep the newline; but TODO- consider stripping and adding the newline as necessary on the write; it'd be more explicit/reliable.
            if barcode not in bucket:
                bucket.append( barcode)
            else:
                log.debug( f'not adding barcode, ``{barcode}`` it already exists in the target bucket' )
    return

    ## end def update_buckets()


def write_data( output_filepath: str, bucket: list ) -> None:
    """ Writes barcodes to given path. 
        Called by manage_monthly_file_creation() """
    log.debug( f'output_filepath, ``{output_filepath}``' )
    with open( output_filepath, 'w' ) as filehandler:
        filehandler.writelines( bucket )
    return


def parse_args() -> dict:
    """ Parses arguments when module called via __main__ """
    parser = argparse.ArgumentParser( description='Required: email.' )
    parser.add_argument( '--date', '-d', help='date required in the form of 2022-10-01', required=True )
    parser.add_argument( '--source_dir_path', '-s', help='source directory-path required', required=True )
    parser.add_argument( '--output_dir_path', '-o', help='output directory-path required', required=True )
    args: dict = vars( parser.parse_args() )
    return args


if __name__ == '__main__':
    args: dict = parse_args()
    log.debug( f'args, ```{args}```' )
    date_str: str = args['date']
    source_dir_path: str = args['source_dir_path']
    output_file_path: str = args['output_dir_path']
    manage_monthly_file_creation( date_str, source_dir_path, output_file_path )
