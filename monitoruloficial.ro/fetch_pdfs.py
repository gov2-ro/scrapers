import sqlite3, json, requests, sys, os, time, random
import logging
from tqdm import tqdm

sys.path.append("../utils/")
from common import base_headers

""" 
read each json
download pdfs
check if exists, mode overwrite, mode update
# TODO: write log to db? checksum?
 """

db_filename     =   '../../data/mo/mo.db'
table_name      =   'dates_lists'
output_folder   =   '../../data/mo/pdfs/'
verbose         =   False
overwrite       =   False   # if false check if file exists, don't fetch again
pause_at        =   30      # days
pause           =   10      # seconds
url_base        =   'https://monitoruloficial.ro'
shy_parts       =   ["III-a", "IV-a", "VI-a", "VII-a"] # ascunse după10 zile
#  - - - - - - - - - - - - - - - - - - - - -  

conn = sqlite3.connect(db_filename)
c = conn.cursor()
c.execute('SELECT * FROM ' + table_name + ' ORDER BY date DESC')
rows = c.fetchall()
 
nrows = len(rows)
tqdm.write(' > ' + str(nrows) + ' days in the db')
all_files = 0
files_found = new_files_found = 0
prev_year = 1000

for row in tqdm(rows, desc='days'):
# Iterate over the rows and convert the JSON string to a dictionary
    date, json_str = row
    json_dict = json.loads(json_str)
    ii = 0
    for sectiune, parti in tqdm(json_dict.items(), desc='părți', leave=False):
        # check if parte > 3, don't bother.
        if any(part in sectiune for part in shy_parts):
            continue

        for nr, url in tqdm(parti.items(), desc='pdfs', leave=False):
            jj = 0
            # download pdf
            filename = os.path.splitext(url[1:])[0]
            urlparts = filename.split('--')

            year=urlparts[-1]
            if len(year) != 4:
                tqdm.write('err: ' + str(year))
            
            if str(year) != str(prev_year):
                tqdm.write(f" -- current year: " + str(year) + " -", end="\r")
                # check if folder exists, cread if not, print.
                if not os.path.exists(output_folder + str(year) ):
                    os.makedirs(output_folder + str(year))
                    # tqdm.write(f"created " + str(year) + " folder", end="\r")
                    tqdm.write("created " + str(year) + " folder")

            prev_year = year

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
                # os.system('say -v ioana "piiua " -r 250')
                if (new_files_found != files_found): 
                    tqdm.write("Files found: " + str(files_found))
                    new_files_found = files_found
            # tqdm.write('   - >  ' + str(ii) + '/' + str(nrows) + ' ' + str(ii+jj) + ' ' + str(jj))
    ii+=1
    
    # time.sleep(random.random()*1.75)

conn.close()
tqdm.write(' -- done ' + str(len(rows)) + ' days ' + str(ii) + ' secțiuni ' + str(all_files) + ' saved pdfs')
os.system('say -v ioana "în sfârșit, am gătat ' +  str(all_files) + ' fișiere " -r 250')