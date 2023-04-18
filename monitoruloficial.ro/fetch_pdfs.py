import sqlite3, json, requests, sys, os, time, random
import logging
from tqdm import tqdm
sys.path.append("../utils/")
from common import base_headers

""" 
read each json
download pdfs
 """

db_filename = '../data/mo/mo.db'
table_name = 'dates_lists'
output_folder = '../data/mo/pdfs/'
url_base = 'https://monitoruloficial.ro'
verbose = False

# Connect to the SQLite database
conn = sqlite3.connect(db_filename)
c = conn.cursor()

# Fetch all rows from the "dates_lists" table
c.execute('SELECT * FROM ' + table_name)
rows = c.fetchall()
 

pbar = tqdm(len(rows))
tqdm.write('zz ' + str(len(rows)))
# Iterate over the rows and convert the JSON string to a dictionary
for row in rows:
    date, json_str = row
    json_dict = json.loads(json_str)
    # print(f"Date: {date}, JSON dictionary: {json_dict}")
    # breakpoint()
    ii = jj = 0
    pbar.update(1)
    for sectiuni, parti in json_dict.items():
        for nr, url in parti.items():
            # download pdf
            # filename = url[1:]
            filename = os.path.splitext(url[1:])[0]

            urlparts = url.split('--')
            # print(date + ' [' + urlparts[1] + '] ' + sectiuni + ' : ' + str(nr) + ' ' + url)
            # tqdm.write(date + ' [' + urlparts[1] + '] ' + str(nr) + '  - - -  ' + url)
            # TODO: save to log
            if verbose:
                tqdm.write('>> ' + url_base + url)
            try:
                response = requests.get(url_base + url, headers=base_headers('headers2'))
            except Exception as e:
                logging.error(f'Error processing URL {url_base + url}: {e}')
            
            # save pdf
            try:
                # with open(output_folder + date + '.pdf', 'wb') as f:
                with open(output_folder + filename + '.pdf', 'wb') as f:
                    f.write(response.content)
                if verbose:
                    tqdm.write(' > > ' + filename + 'pdf')
            except Exception as e:
                logging.error(f'Error saving PDF URL {url_base + url}: {e}')
            time.sleep(random.random()*1.75)
            jj+=1
    ii+=1
    
    time.sleep(random.random()*1.75)
# Close the database connection
conn.close()
tqdm.write('done ' + str(len(rows)) + ' days ' + str(ii) + 'secțiuni' + str(jj) + 'saved pdfs')
