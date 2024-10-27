dataqRoot = '../../data/mo/'
db_filename = dataqRoot + 'mo-x.db'
table_name = '[mo-index2]'
output_folder = dataqRoot + 'pdfs/'
verbose = False
overwrite = False
pause_at = 30
pause = 10
url_base = 'https://monitoruloficial.ro'
shy_parts = ["III-a", "IV-a", "VI-a", "VII-a"]



import sqlite3, json, requests, sys, os, time, random
import logging
from tqdm import tqdm

def format_size(size_bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:3.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} GB"

sys.path.append("../utils/")
from common import base_headers


conn = sqlite3.connect(db_filename)
c = conn.cursor()
c.execute('SELECT * FROM ' + table_name + ' ORDER BY date DESC')
rows = c.fetchall()

nrows = len(rows)
tqdm.write(' > ' + str(nrows) + ' days in the db')
all_files = 0
files_found = new_files_found = 0
prev_year = 1000

for row in tqdm(rows, desc='days', bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {desc}]'):
    date, json_str = row
    json_dict = json.loads(json_str)
    tqdm.write(f"\ndate: {date}")
    
    for sectiune, parti in tqdm(json_dict.items(), 
                               desc=f'părți ({date})', 
                               leave=False):
        if any(part in sectiune for part in shy_parts):
            continue

        for nr, url in tqdm(parti.items(), 
                           desc=f'pdfs ({sectiune})', 
                           leave=False,
                           bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}] {desc}'):
            filename = os.path.splitext(url[1:])[0]
            urlparts = filename.split('--')
            year = urlparts[-1]
            
            if len(year) != 4:
                tqdm.write('err: ' + str(year))
            
            if str(year) != str(prev_year):
                tqdm.write(f" -- current year: {year} --")
                if not os.path.exists(output_folder + str(year)):
                    os.makedirs(output_folder + str(year))
                    tqdm.write(f"created {year} folder")
            
            prev_year = year
            current_file = f"{filename}.pdf"
            output_path = output_folder + year + '/' + current_file

            if overwrite is False and os.path.isfile(output_path):
                file_size = os.path.getsize(output_path)
                files_found += 1
                if verbose:
                    tqdm.write(f'skipping {current_file} ({format_size(file_size)})')
                continue

            try:
                # First make a HEAD request to get content length
                head_response = requests.head(url_base + url, headers=base_headers('headers2'))
                expected_size = int(head_response.headers.get('content-length', 0))
                # tqdm.write(f" -: {current_file} (expected size: {format_size(expected_size)})")

                # Then get the actual file
                response = requests.get(url_base + url, headers=base_headers('headers2'))
                actual_size = len(response.content)
                
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                    all_files += 1
                    time.sleep(random.random()*1.25)
                
                # Get the saved file size to verify
                saved_size = os.path.getsize(output_path)
                tqdm.write(f' >> {current_file} ({format_size(saved_size)})')
                
                # Verify sizes match
                if saved_size != actual_size:
                    tqdm.write(f' !! Warning: Size mismatch for {current_file}')
                    tqdm.write(f' !! Expected: {format_size(expected_size)}, Got: {format_size(saved_size)}')
                
            except Exception as e:
                logging.error(f'Error processing {current_file}: {e}')
            
            if round(all_files/pause_at) == all_files/pause_at:
                time.sleep(pause)
                if (new_files_found != files_found):
                    tqdm.write(f"Files found: {files_found}")
                    new_files_found = files_found

conn.close()
tqdm.write(f' -- done {len(rows)} days, {all_files} saved pdfs')
os.system(f'say -v ioana "în sfârșit, am gătat {all_files} fișiere " -r 250')