import json, logging, os, pathlib, pprint, shutil, time

log = logging.getLogger(__name__)


def check_directories( dir_paths ):
    """ Checks that directories exists.
        Called by controller.manage_processing() """
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
        Called by controller.manage_processing()
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


def load_recent_file_list( tracker_path ):
    """ Loads tracker file of recently processed files.
        Called by controller.manage_processing() """
    log.debug( 'loading recently processed files' )
    ( err, recently_processed_files ) = ( None, [] )
    try:
        with open( tracker_path ) as fh:
            recently_processed_files = json.loads( fh.read() )
    except Exception as e:
        err = repr(e)
        log.exception( 'Problem opening tracker file' )
    log.debug( f'err, ``{err}``' )
    log.debug( f'recently_processed_files, ``{pprint.pformat(recently_processed_files)}``' )
    return ( err, recently_processed_files )


def get_new_files( prefix_list, dir_files, recent_files ):
    """ Returns target new-files in from dir_files.
        Called by controller.manage_processing()
        TODO: go through dir_files instead, and break when I have four files. """
    log.debug( 'starting get_new_files()' )
    ( err, new_file_list ) = ( None, None )
    try:
        assert type(prefix_list) == list
        assert type(dir_files) == list
        assert type(recent_files) == list
        new_file_list = []
        for file_name in dir_files:
            if file_name[0:5] in prefix_list:
                if file_name not in recent_files:
                    new_file_list.append( file_name )
        new_file_list.sort()  # don't need to do this for the production code, but it makes testing easier.
        if len( new_file_list ) > 0:
            log.info( f'new legit files, ``{new_file_list}``' )
        else:
            log.debug( f'new legit files, ``{new_file_list}``' )
    except Exception as e:
        err = repr(e)
        log.exception( f'Problem checking for new-files, ``{err}``' )
    return ( err, new_file_list )


def archive_new_files( new_file_names, source_dir, archive_dir ):
    """ Archives files and returns paths-dict.
        Called by controller.manage_processing() """
    ( err, paths_dct ) = ( None, {} )
    try:
        paths_dct = {
            'non_hay_accessions_archive_path': '',
            'hay_accessions_archive_path': '',
            'non_hay_refiles_archive_path': '',
            'hay_refiles_archive_path': '' }
        datestamp = make_datestamp()
        for file_name in new_file_names:
            source_path = f'{source_dir}/{file_name}'
            log.debug( f'source_path, ``{source_path}``' )
            if file_name[0:5] == 'QSACS':
                archive_file_name = f'{"QSACS"}_{datestamp}.txt'
                archive_path = f'{archive_dir}/{archive_file_name}'
                paths_dct['non_hay_accessions_archive_path'] = archive_path
            elif file_name[0:5] == 'QHACS':
                archive_file_name = f'{"QHACS"}_{datestamp}.txt'
                archive_path = f'{archive_dir}/{archive_file_name}'
                paths_dct['hay_accessions_archive_path'] = archive_path
            elif file_name[0:5] == 'QSREF':
                archive_file_name = f'{"QSREF"}_{datestamp}.txt'
                archive_path = f'{archive_dir}/{archive_file_name}'
                paths_dct['non_hay_refiles_archive_path'] = archive_path
            elif file_name[0:5] == 'QHREF':
                archive_file_name = f'{"QHREF"}_{datestamp}.txt'
                archive_path = f'{archive_dir}/{archive_file_name}'
                paths_dct['hay_refiles_archive_path'] = archive_path
            shutil.copyfile( source_path, archive_path )
            time.sleep( .25 )
            path_test = pathlib.Path( archive_path )
            assert path_test.is_file()
    except Exception as e:
        err = repr(e)
        log.exception( 'Problem archiving new files, ``{err}``')
    log.debug( f'err, ``{err}``' )
    log.debug( f'paths_dct, ``{pprint.pformat(paths_dct)}``' )
    return ( err, paths_dct )


def make_datestamp( time_obj=None ):
    """ Returns datestamp_string for archived files.
        The 'time_to_format_tuple' is for testing.
        Called by archive_new_files() """
    types = ["<class 'time.struct_time'>", "<class 'NoneType'>"]
    assert repr( type(time_obj) ) in types
    if time_obj == None:
        time_obj = time.localtime()
    formatted_time = time.strftime("%Y-%m-%dT%H-%M-%S", time_obj)
    assert type(formatted_time) == str
    log.debug( f'formatted_time, ``{formatted_time}``' )
    return formatted_time


def delete_processed_files( new_files, source_dir ):
    """ Deletes processed files.
        Called by controller.manage_processing() """
    err = None
    try:
        assert type(new_files) == list
        assert type(source_dir) == str
        log.debug( f'new_files, ``{pprint.pformat(new_files)}``' )
        for file_name in new_files:
            log.debug( f'about to delte processed file, ``{file_name}``' )
            file_path = f'{source_dir}/{file_name}'
            os.remove( file_path )
            path_test = pathlib.Path( file_path )
            assert( path_test.is_file() == False )
        log.debug( 'delete_processed_files() complete' )
    except Exception as e:
        log.exception( 'Problem deleting processed files.' )
        err = repr(e)
    return err
