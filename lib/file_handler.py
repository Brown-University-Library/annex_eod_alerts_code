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
        Called by controller.process_files()
        TODO- get list sorted reverse-chronologically for faster subsequent processing. """
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


def get_new_files( prefix_list, dir_files ):
    """ Returns target new-files in from dir_files.
        Called by controller.process_files()
        TODO: go through dir_files instead, and break when I have four files. """
    log.debug( 'starting get_new_files()' )
    ( err, new_file_list ) = ( None, None )
    try:
        assert type(prefix_list) == list
        assert type(dir_files) == list
        new_file_list = []
        for prefix in prefix_list:
            for file_name in dir_files:
                position_of_prefix = str.find( file_name, prefix )   # haystack, needle. Will be -1 if not found.
                position_of_count_ndicator = str.find(file_name, '.cnt')
                if ( (position_of_prefix != -1) & (position_of_count_ndicator == -1) ):  # if (prefixes exist AND '.cnt' substring doesn't)
                    new_file_list.append(file_name)
        new_file_list.sort()  # don't need to do this for the production code, but it makes testing easier.
        if len( new_file_list ) > 0:
            log.info( f'new legit files, ``{new_file_list}``' )
        else:
            log.debug( f'new legit files, ``{new_file_list}``' )
    except Exception as e:
        err = repr(e)
        log.exception( f'Problem checking for new-files, ``{err}``' )
    return ( err, new_file_list )



