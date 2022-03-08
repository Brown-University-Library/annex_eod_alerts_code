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

import json, logging, os, pprint, sys

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
from annex_eod_alerts_code.lib import checker, emailer, file_handler


class Controller(object):
    """ Manages steps. """

    def __init__( self ):
        self.source_directory = os.environ['ANXEODALERTS__SOURCE_DIR']
        self.prefix_list = json.loads( os.environ['ANXEODALERTS__PREFIX_LIST_JSON'] )
        self.tracker_path = os.environ['ANXEODALERTS__TRACKER_FILE_PATH']

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

        (err, recent_files) = file_handler.load_recent_file_list( self.tracker_path )
        if err:
            raise Exception( f'Problem loading recent file-list, ``{err}``' )

        (err, new_files) = file_handler.get_new_files( self.prefix_list, dir_files, recent_files )
        if err:
            raise Exception( f'Problem checking for new files, ``{err}``' )
        ## process new files ----------------------------------------
        if new_files:
            ## archive new files
            pass
            ## process new files
            new_file_paths = []
            for file_name in new_files:
                new_file_path = f'{self.source_directory}/{file_name}'
                new_file_paths.append( new_file_path )
            log.debug( f'new_file_paths, ``{pprint.pformat(new_file_paths)}``' )
            barcode_check_results = self.process_new_files( new_file_paths )
            if err:
                raise Exception( f'Problem processing new files, ``{err}``' )
            ## determine whether to send email ----------------------
            ( err, email_check ) = checker.check_whether_to_send_email( barcode_check_results )
            if err:
                raise Exception( f'Problem determining whether to send email, ``{err}``' )
            ## send email if necessary ------------------------------
            if email_check:
                err = emailer.send_mail( barcode_check_results )
                if err:
                    raise Exception( f'Problem sending email, ``{err}``' )

        else:
            log.info( 'no new files found' )

    def process_new_files( self, new_file_paths ):
        """ Manages calls to functions for found new files.
            Called by process_files()
            TODO- this will be vastly expanded with other checks and api-updates. """
        ## initialize holder dict -----------------------------------
        results_dct = checker.initialize_results_dct()
        ## check non-hay-accessions ---------------------------------
        checker.check_non_hay_accessions( new_file_paths, results_dct, self.tracker_path )
        ## check hay-accessions -------------------------------------
        checker.check_hay_accessions( new_file_paths, results_dct, self.tracker_path )
        ## check non-hay-refiles ------------------------------------
        checker.check_non_hay_refiles( new_file_paths, results_dct, self.tracker_path )
        ## check hay-refiles ----------------------------------------
        checker.check_hay_refiles( new_file_paths, results_dct, self.tracker_path )
        return results_dct

    ## end Controller()



if __name__ == '__main__':
    log.debug( '\n\nstarting processing...' )
    c = Controller()
    c.process_files()
    log.debug( 'processing complete' )
