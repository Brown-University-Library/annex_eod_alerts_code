import logging, os

log = logging.getLogger(__name__)


def check_source_directory_exists( dir_path ):
    """ Checks that source directory exists.
        Called by controller.process_files() """
    log.debug( 'starting check_source_directory_exists()' )
    ( err, exists ) = ( None, False )
    exists = False
    try:
        assert type( dir_path ) == str
        exists = os.path.exists( dir_path )
    except Exception as e:
        err = repr(e)
        log.exception( f'Problem finding source directory, ``{err}``' )
    log.debug( f'err, ``{err}``; exists, ``{exists}``' )
    return ( err, exists )
