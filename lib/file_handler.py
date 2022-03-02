import logging, os, pprint

log = logging.getLogger(__name__)


def check_directories( dir_paths ):
    """ Checks that directories exists.
        Called by controller.process_files() """
    log.debug( 'starting check_directories()' )
    err = None
    try:
        for dir_path in dir_paths:
            log.debug( f'path, ``{dir_path}``' )
            assert type(dir_path) == str
            exists = os.path.exists( dir_path )
            if exists == False:
                err = f'dir_path, ``{dir_path}`` not found.'
            elif os.path.isdir( dir_path ) == False:
                err = f'dir_path, ``{dir_path}`` not a directory.'
            if err:
                log.warning( err )
                break
    except Exception as e:
        err = repr(e)
        log.exception( f'Problem finding a directory, ``{err}``' )
    return err


def scan_directory( dir_path ):
    """ Returns file-paths in directory.
        Called by controller.process_files() """
    log.debug( 'starting scan_directory' )
    ( err, new_file_list ) = ( None, None )
    try:
        assert type(dir_path) == str
        if (dir_path.endswith('/') == False):
            directory = dir_path + '/'
        else:
            directory = dir_path
        log.debug( f'scanned-directory, ``{directory}``' )
        file_list = os.listdir(directory)
        log.debug( f'file_list, ``{pprint.pformat(file_list)}``' )
        ## 1) eliminate .DS_Store & 2) eliminate directories
        new_file_list = []
        for file_name in file_list:
            if file_name == '.DS_Store':
                pass
            else:
                sub_dir_name = dir_path + file_name
                if os.path.isdir( sub_dir_name ):
                    pass
                else:
                    new_file_list.append( file_name )
        log.debug( f'pruned file-list, ``{new_file_list}``' )
    except Exception as e:
        err = repr(e)
        log.exception( f'Problem scanning directory, ``{err}``' )
    return ( err, new_file_list )

