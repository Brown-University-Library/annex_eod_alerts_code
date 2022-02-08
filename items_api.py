import requests
import json



headers = {'Accept': 'application/json'}
url = URL_PATTERN

tfp = []


with open( SOURCE_BARCODES_FILE_PATH, 'rb') as fp:
    for line in fp:
        barcode=line.decode('utf8').strip()
        req = requests.get(url.format(barcode=barcode), headers=headers,)
        data = req.json()
       

        tfp.append(data['item_data'].get('barcode') + ', ' + 
                   data['item_data']['library'].get('value') + ', ' + 
                   data['item_data']['location'].get('desc') + ', ' + 
                   data['item_data']['base_status'].get('desc') + ', ' + 
                   data['item_data']['process_type'].get('desc') +
                   '\n')
        with open( OUTPUT_FILE_PATH, 'w', encoding="utf-8") as txt:
            txt.writelines(tfp)
