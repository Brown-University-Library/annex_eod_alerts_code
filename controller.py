"""
Manages processing.

Called by cron-job which calls controller.py

Steps (roughly)...
- Determine if there are new files to process. Assuming there are...
- Archive each of the files (with timestamp in filename).
    - Alert folk if there are file-name issues.
- set up alerts-holder and four data-holders
- Process each file...
    - barcode check
    - process-type, location, status-check
    - build alert-list and store it
    - build data-summary and store it
- ? Save alerts and data-holders ?
- Email alert and data-holders as attachments.
"""

import json, logging, os, sys

lvl_dct = { 'DEBUG': logging.DEBUG, 'INFO': logging.INFO }
lvl = os.environ['ANXEODALERTS__LOG_LEVEL']
logging.basicConfig(
    filename=os.environ['ANXEODALERTS__LOG_PATH'],
    level=lvl,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S',
    )
log = logging.getLogger(__name__)

sys.path.append( os.environ['ANXEODALERTS__ENCLOSING_PROJECT_PATH'] )
from annex_eod_alerts_code.lib import checker, file_handler


class Controller(object):
    """ Manages steps. """

    def __init__( self ):
        self.source_directory = os.environ['ANXEODALERTS__SOURCE_DIR']
        self.prefix_list = json.loads( os.environ['ANXEODALERTS__PREFIX_LIST_JSON'] )

    def process_files( self ):
        """ Manages calls to functions.
            Called by ``if __name__ == '__main__':`` """
        ## ensure directories exist ---------------------------------
        err = file_handler.check_directories( [self.source_directory] )
        if err:
            raise Exception( f'Problem finding a directory, ``{err}``' )
        ## check for new files --------------------------------------
        (err, dir_files) = file_handler.scan_directory( self.source_directory )
        if err:
            raise Exception( f'Problem scanning source-directory, ``{err}``' )
        (err, new_files) = file_handler.get_new_files( self.prefix_list, dir_files )
        if err:
            raise Exception( f'Problem checking for new files, ``{err}``' )
        ## process new files ----------------------------------------
        if new_files:
            err = self.process_new_files( new_files )
        if err:
            raise Exception( f'Problem processing new files, ``{err}``' )

    def process_new_files( self, new_files ):
        """ Manages calls to functions for found new files.
            Called by process_files()
            TODO- this will be vastly expanded. """
        ## check barcodes against alma ------------------------------
        ( err, barcode_check_results ) = checker.manage_check_barcodes( new_files )
        if err:
            raise Exception( f'Problem checking barcodes, ``{err}``' )
        ## determine whether to send email --------------------------
        ( err, email_check ) = checker.check_whether_to_send_email( barcode_check_results )
        if err:
            raise Exception( f'Problem determining whether to send email, ``{err}``' )
        ## send email if necessary ----------------------------------
        if email_check:
            err = emailer.send_email( barcode_check_results )
            if err:
                raise Exception( f'Problem sending email, ``{err}``' )

    ## end Controller()



if __name__ == '__main__':
    log.debug( '\n\nstarting processing...' )
    c = Controller()
    c.process_files()
    log.debug( 'processing complete' )
