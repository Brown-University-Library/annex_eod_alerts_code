import argparse, datetime, logging, os, pathlib, pprint


logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)

# log.debug( 'test' )



def main( file_path ):
    """ Returns file create-date. """
    assert type(file_path) == str
    log.debug( f'file_path, ``{file_path}``' )

    ## verify path
    path_obj = pathlib.Path( file_path )
    assert type(path_obj) == pathlib.PosixPath, type(path_obj)
    assert path_obj.exists(), f'file-path, ``{file_path}`` does not exist'
    assert path_obj.is_file(), f'file-path, ``{file_path}`` is not a file'
    log.debug( 'path verified' )

    ## get create-datetime
    file_info = path_obj.stat()
    assert type(file_info) == os.stat_result, type(file_info)
    log.debug( f'file_info, ``{pprint.pformat(file_info)}``' )
    create_timestamp = file_info.st_ctime
    assert repr(type(create_timestamp)) == "<class 'float'>", repr(type(create_timestamp))
    # assert repr(create_timestamp) == 'foo', repr(create_timestamp)
    log.debug( f'create_timestamp, ``{create_timestamp}``' )
    datetime_obj = datetime.datetime.fromtimestamp( create_timestamp )
    assert type(datetime_obj) == datetime.datetime, type(datetime_obj)
    log.debug( f'datetime_obj, ``{datetime_obj}``' )
    formatted_time = datetime_obj.strftime( '%Y-%m-%dT%H-%M-%S' )
    assert type(formatted_time) == str
    log.debug( f'formatted_time, ``{formatted_time}``' )
    return


def parse_args():
    """ Parses arguments when module called via __main__ """
    parser = argparse.ArgumentParser( description='Required: /path/to/file' )       # text shown on `-h`
    parser.add_argument( '--path', '-p', help='file_path required', required=True ) # text shown on `-h`
    args_dict = vars( parser.parse_args() )
    log.debug( f'args_dict, ``{args_dict}``' )
    return args_dict


if __name__ == '__main__':
    args_dict = parse_args()
    assert type(args_dict) == dict
    path = args_dict['path']
    main( path )
