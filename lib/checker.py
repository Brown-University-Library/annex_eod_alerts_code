import logging, os, pprint, time
import requests

log = logging.getLogger(__name__)


def initialize_results_dct():
    """ Creates structure to hold check-data.
        Called by manages_check_barcodes() """
    results_dct = {
        'non_hay_accessions': {
            'count_barcodes': 0,
            'count_problematic_barcodes': 0,
            'list_of_barcodes_not_found_in_alma': []
        },
        'non_hay_refiles__NOT_YET_IMPLEMENTED': {
            'count_barcodes': 0,
            'count_problematic_barcodes': 0,
            'list_of_barcodes_not_found_in_alma': []
        },
        'hay_accessions': {
            'count_barcodes': 0,
            'count_problematic_barcodes': 0,
            'list_of_barcodes_not_found_in_alma': []
        },
        'hay_refiles__NOT_YET_IMPLEMENTED': {
            'count_barcodes': 0,
            'count_problematic_barcodes': 0,
            'list_of_barcodes_not_found_in_alma': []
        },
    }
    log.debug( f'initialized results_dct, ``{pprint.pformat(results_dct)}``' )
    return results_dct


def check_non_hay_accessions( new_file_paths, results_dct ):
    """ Manages check of non-hay accessions and updates results_dct.
        Called by controller.process_new_files() """
    err = None
    try:
        target_file_path = select_path( new_file_paths, 'QSACS' )
        barcode_list = load_barcodes( target_file_path )
        results_dct['non_hay_accessions']['count_barcodes'] = len( barcode_list )
        for barcode in barcode_list:
            log.debug( f'barcode, ``{barcode}``' )
            ( err, alma_api_data_dct ) = check_alma_api( barcode )
            time.sleep( .5 )
            try:
                if alma_api_data_dct['item_data']['barcode'] != barcode:
                    log.debug( 'barcode found; continuing' )
                    pass
            except Exception as e:
                log.exception( repr(e) )
                results_dct['non_hay_accessions']['count_problematic_barcodes'] += 1
                results_dct['non_hay_accessions']['list_of_barcodes_not_found_in_alma'].append( barcode )
        log.debug( f'updated results_dct, ``{pprint.pformat(results_dct)}``' )
    except Exception as e:
        err = repr(e)
    return err


def check_hay_accessions( new_file_paths, results_dct ):
    """ Manages check of non-hay accessions and updates results_dct.
        Called by controller.process_new_files() """
    err = None
    try:
        target_file_path = select_path( new_file_paths, 'QHACS' )
        barcode_list = load_barcodes( target_file_path )
        results_dct['hay_accessions']['count_barcodes'] = len( barcode_list )
        for barcode in barcode_list:
            log.debug( f'barcode, ``{barcode}``' )
            ( err, alma_api_data_dct ) = check_alma_api( barcode )
            time.sleep( .5 )
            try:
                if alma_api_data_dct['item_data']['barcode'] != barcode:
                    log.debug( 'barcode found; continuing' )
                    pass
            except Exception as e:
                log.exception( repr(e) )
                results_dct['hay_accessions']['count_problematic_barcodes'] += 1
                results_dct['hay_accessions']['list_of_barcodes_not_found_in_alma'].append( barcode )
        log.debug( f'updated results_dct, ``{pprint.pformat(results_dct)}``' )
    except Exception as e:
        err = repr(e)
    return err


def select_path( new_file_paths, selector ):
    """ Returns proper path from paths-list.
        Called by check_non_hay_accessions() and others """
    assert type(new_file_paths) == list
    assert type(selector) == str
    target_file_path = ''
    for file_path in new_file_paths:
        if selector in file_path:
            target_file_path = file_path
            break
    log.debug( f'target_file_path, ``{target_file_path}``' )
    return target_file_path


def load_barcodes( file_path ):
    """ Opens file; loads barcods into list.
        Called by check_non_hay_accessions() and others. """
    log.debug( 'starting load_barcodes()' )
    log.debug( f'file_path, ``{file_path}``' )
    try:
        barcodes = []
        with open( file_path, 'rb') as fp:
            for line in fp:
                log.debug( f'line, ``{line}``' )
                barcode = line.decode('utf8').strip()
                barcodes.append( barcode )
    except Exception as e:
        log.exception( 'Problem preparing barcode list.' )
    log.debug( f'barcodes, ``{barcodes}``' )
    return barcodes


def check_alma_api( barcode ):
    """ Checks alma-api with barcode and returns data.
        Called by check_non_hay_accessions() and others. """
    ( err, alma_api_data_dct ) = ( None, {} )
    try:
        URL_ROOT = os.environ['ANXEODALERTS__ITEM_API_ROOT']
        API_KEY = os.environ['ANXEODALERTS__ITEM_API_KEY']
        headers = {'Accept': 'application/json'}
        url = "%s?item_barcode={barcode}&apikey=%s" % ( URL_ROOT, API_KEY )
        log.debug( f'url, ``{url}``' )
        full_url = url.format(barcode=barcode)
        log.debug( f'full_url, ``{full_url}``' )
        req = requests.get(full_url, headers=headers,)
        alma_api_data_dct = req.json()
        log.debug( f'alma_api_data_dct, ``{pprint.pformat(alma_api_data_dct)}``' )
        log.debug( f'keys, ``{alma_api_data_dct.keys()}``' )
    except Exception as e:
        log.exception( 'Problem accessing alma-api with barcode, ``{barcode}``' )
        err = repr(e)
        raise Exception( err )
    log.debug( f'alma_api_data_dct, ``{alma_api_data_dct}``' )
    return ( err, alma_api_data_dct )


def check_whether_to_send_email( results_dct ):
    ( err, send_email_result ) = ( None, False )
    try:
        assert type(results_dct) == dict
        if ( results_dct['non_hay_accessions']['count_problematic_barcodes'] > 1 ):
            send_email_result = True
        elif ( results_dct['non_hay_refiles']['count_problematic_barcodes'] > 1 ):
            send_email_result = True
        elif ( results_dct['hay_accessions']['count_problematic_barcodes'] > 1 ):
            send_email_result = True
        elif ( results_dct['hay_refiles']['count_problematic_barcodes'] > 1 ):
            send_email_result = True
    except Exception as e:
        err = repr(e)
    log.debug( f'send_email_result, ``{send_email_result}``' )
    return ( err, send_email_result )
