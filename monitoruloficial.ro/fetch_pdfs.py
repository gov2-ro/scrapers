import sqlite3, json, requests, sys, os, time, random
import logging
from tqdm import tqdm

sys.path.append("../utils/")
from common import base_headers

""" 
read each json
download pdfs
check if exists, mode overwrite, mode update
 """

db_filename     =   '../../data/mo/mo.db'
table_name      =   'dates_lists'
output_folder   =   '../../data/mo/pdfs/'
verbose         =   False
overwrite       =   False   # if false check if file exists, don't fetch again
pause_at        =   30      # days
pause           =   10      # seconds
url_base        =   'https://monitoruloficial.ro'

#  - - - - - - - - - - - - - - - - - - - - -  

conn = sqlite3.connect(db_filename)
c = conn.cursor()
c.execute('SELECT * FROM ' + table_name)
rows = c.fetchall()

pbar = tqdm(len(rows))
nrows = len(rows)
tqdm.write('zz ' + str(nrows))
# Iterate over the rows and convert the JSON string to a dictionary
all_files = 0
for row in tqdm(rows):
    date, json_str = row
    json_dict = json.loads(json_str)
    ii = 0
    files_found = 0
    for sectiuni, parti in json_dict.items():
        for nr, url in parti.items():
            jj = 0
            # download pdf
            filename = os.path.splitext(url[1:])[0]
            urlparts = filename.split('--')

            year=urlparts[-1]
            if len(year) != 4:
                tqdm.write('err: ' + str(year))

            if verbose:
                tqdm.write('>> ' + url_base + url)

            if overwrite is False and os.path.isfile(output_folder + str(year) + '/' + filename + '.pdf'):
                files_found += 1
                if verbose:
                    tqdm.write('skipping ' + filename + '.pdf');
                continue #if overwrite = False and file exists, continue
               
            try:
                response = requests.get(url_base + url, headers=base_headers('headers2'))
            except Exception as e:
                logging.error(f'Error processing URL {url_base + url}: {e}')
            
            # save pdf
            try:
                # with open(output_folder + date + '.pdf', 'wb') as f:
                with open(output_folder + year + '/' +  filename + '.pdf', 'wb') as f:
                    f.write(response.content)
                    all_files += 1
                    time.sleep(random.random()*1.25)
                if verbose:
                    tqdm.write(' > > ' + filename + 'pdf')
            except Exception as e:
                logging.error(f'Error saving PDF URL {url_base + url}: {e}')
            
            jj+=1
            if round(all_files/pause_at) == all_files/pause_at:
                time.sleep(pause)
                os.system('say -v ioana "piiua " -r 250')
            # tqdm.write('   - >  ' + str(ii) + '/' + str(nrows) + ' ' + str(ii+jj) + ' ' + str(jj))
    ii+=1
    
    time.sleep(random.random()*1.75)
# Close the database connection
conn.close()
tqdm.write('done ' + str(len(rows)) + ' days ' + str(ii) + 'secțiuni' + str(jj) + 'saved pdfs')

os.system('say -v ioana "în sfârșit, am gătat ' +  str(all_files) + ' fișiere " -r 250')