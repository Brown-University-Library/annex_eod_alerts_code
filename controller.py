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
- ? Save alerts and data-holders?
- Email alert and data-holders as attachments.
"""

import logging, os, sys

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
from annex_eod_alerts_code.lib import file_handler


class Controller(object):
    """ Manages steps. """

    def __init__( self ):
        self.source_directory = os.environ['ANXEODALERTS__POC_BARCODES_SOURCE_FILEPATH']

    def process_files( self ):
        """ Manages calls to functions.
            Called by ``if __name__ == '__main__':`` """

        ## validate source-directory existence ------------
        ( err, exists) = file_handler.check_source_directory_exists( self.source_directory )
        if err:
            raise Exception( f'Problem finding source directory, ``{err}``' )
        elif exists == False:
            raise Exception( f'Problem finding source directory' )

        ## -- check for new file ----------------
        pass

    ## end Controller()


if __name__ == '__main__':
    log.debug( '\n\nstarting processing...' )
    c = Controller()
    c.process_files()
    log.debug( 'processing complete' )
