'''
Proof-of-concept showing results of accessing the alma items-api.

Usage...
- % cd ./annex_eod_alerts_code
- % source ../env/bin/activate
- % python3 ./api_proof_of_concept_READ.py
'''

import json, os, pprint
import requests

URL_ROOT = os.environ['ANXEODALERTS__ITEM_API_ROOT']
API_KEY = os.environ['ANXEODALERTS__ITEM_API_KEY']
POC_BARCODES_SOURCE = os.environ['ANXEODALERTS__POC_BARCODES_SOURCE_FILEPATH']
POC_OUTPUT = os.environ['ANXEODALERTS__POC_BARCODES_OUTPUT_FILEPATH']

headers = {'Accept': 'application/json'}
url = "%s?item_barcode={barcode}&apikey=%s" % ( URL_ROOT, API_KEY )
print( f'url, ``{url}``' )

tfp = [ 'BARCODE, LIBRARY, LOCATION, BASE_STATUS, PROCESS_TYPE\n' ]  # heading-row

with open( POC_BARCODES_SOURCE, 'rb') as fp:
    for line in fp:
        barcode=line.decode('utf8').strip()
        full_url = url.format(barcode=barcode)
        print( f'full_ulr, ``{full_url}``' )
        req = requests.get(full_url, headers=headers, timeout=10 )
        data = req.json()
        print( f'data, ``{pprint.pformat(data)}``' )

        ## k, i took these out of the append(), cuz one was failing and I couldn't tell which (was process_type)
        barcode_info = data['item_data'].get('barcode', 'barcode_unavailable')
        library_info = data['item_data']['library'].get('value', 'library_unavailable')
        location_info = data['item_data']['location'].get('desc', 'location_unavailable')
        base_status_info = data['item_data']['base_status'].get('desc', 'base_status_description_unavailable')
        process_type_info = data['item_data']['process_type'].get('desc', 'process_type_description_unavailable')
        if process_type_info is None:
            process_type_info = 'process_type_description_unavailable'

        print( f'barcode_info, ``{barcode_info}``' )
        print( f'library_info, ``{library_info}``' )
        print( f'location_info, ``{location_info}``' )
        print( f'base_status_info, ``{base_status_info}``' )
        print( f'process_type_info, ``{process_type_info}``' )

        tfp.append(barcode_info + ', ' +
                   library_info + ', ' +
                   location_info + ', ' +
                   base_status_info + ', ' +
                   process_type_info +
                   '\n')
        with open( POC_OUTPUT, 'w', encoding="utf-8") as txt:
            txt.writelines(tfp)
