import sqlite3, json, requests, sys, os, time, random
import logging

sys.path.append("../utils/")
from common import base_headers

""" 
fetches part3 - p5 
page by page until end-page?

first get jsonp to figure out number of pages?
or initial html and then from jquery script get gid.php, THEN number of pages?

or guess number of pages until failure?

""" 

url ="https://monitoruloficial.ro/ramo_customs/emonitor/showmo/services/view.php?doc=0520231800&format=pdf&subfolder=5/2023/&page=1"
url ="https://monitoruloficial.ro/ramo_customs/emonitor/showmo/services/view.php?doc=0720230067&format=jsonp&subfolder=7/2023/&page=10&callback=jQuery172022840606989828727_1682000224373"


try:
    response = requests.get(url, headers=base_headers('headers2'))
except Exception as e:
    logging.error(f'Error processing URL {url}: {e}')

# save pdf
try:
    # with open(output_folder + date + '.pdf', 'wb') as f:
    with open('test.json', 'wb') as f:
        f.write(response.content)
        
except Exception as e:
    logging.error(f'Error saving PDF URL : {e}')