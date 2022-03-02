import logging, pprint

log = logging.getLogger(__name__)


def manage_check_barcodes( new_files ):
    """ Manages the process of checking barcodes and assembling results.
        Called by controller.process_new_files() """
    ## initialize holder dict ---------------------------------------
    results_dct = initialize_results_dct()
    ## check non-hay-accessions -------------------------------------
    err = check_non_hay_accessions( new_files, results_dct )
    if err:
        raise Exception( f'Problem checking non-hay accessions, ``{err}``' )
    ## check non-hay-refiles
    ## check hay-accessions
    ## check hay-refiles

    return ( err, results_dct )


def initialize_results_dct():
    """ Creates structure to hold check-data.
        Called by manages_check_barcodes() """
    results_dct = {
        'non_hay_accessions': {
            'count_barcodes': 0,
            'count_problemmatic_barcodes': 0,
            'list_of_barcodes_not_found_in_alma': 'init'
        },
        'non_hay_refiles': {
            'count_barcodes': 0,
            'count_problemmatic_barcodes': 0,
            'list_of_barcodes_not_found_in_alma': 'init'
        },
        'hay_accessions': {
            'count_barcodes': 0,
            'count_problemmatic_barcodes': 0,
            'list_of_barcodes_not_found_in_alma': 'init'
        },
        'hay_refiles': {
            'count_barcodes': 0,
            'count_problemmatic_barcodes': 0,
            'list_of_barcodes_not_found_in_alma': 'init'
        },
    }
    log.debug( f'initialized results_dct, ``{pprint.pformat(results_dct)}``' )
    return results_dct


def check_non_hay_accessions( new_files, results_dct ):
    """ Manages check of non-hay accessions and updates results_dct.
        Called by manage_check_barcodes() """
    err = None
    return err


def check_whether_to_send_email( results_dct ):
    ( err, check_result ) = ( None, False )
    return ( err, check_result )
