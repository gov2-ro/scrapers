import requests, json, sys, os, time, sqlite3,random, argparse, logging
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from tqdm import tqdm
sys.path.append("../utils/")
from common import generate_dates, base_headers


""" 
generate dates starting from 2000-01-04 (cu/fara weekends?)
scrape

[div#contentem div#showmo]
//*[@id="showmo"]

foreach [div.card-body]
    [ol li a].text → text sectiune
    > a → href + nr

save cache htmls
record to SQLite
check if files / rows already save, overwrite

 """

db_filename    =  '../../data/mo/mo.db'
table_name     =  'dates_lists'
cache_dir      =  '../../data/mo/html_cache/'
start_date     =  datetime.today() - timedelta(days=15)
end_date       =  datetime.today() 
save_to_cache  =  True
save_to_db     =  True
overwrite      =  False           # if True, don't check if date exists
pause_at       =  31              # days
pause          =  7              # seconds
verbose        =  False
url            =  'https://monitoruloficial.ro/ramo_customs/emonitor/get_mo.php'

# - - - - - - - - - - - - - - - - - - - - -  

parser = argparse.ArgumentParser(description='looks for dates and return lists of parti MO')
parser.add_argument('-start', '--start_date', help='start date')
parser.add_argument('-end', '--end_date', help='end date')
parser.add_argument('--overwrite', help='True / False - if False, check if date exists, if it does, don\'t overwrite')
parser.add_argument('-m', '--mode', help='mode: l-<x> - last <x> days, all - from the beginning to today ')
args = parser.parse_args()
if args.start_date:
    start_date = args.start_date
if args.end_date:
    end_date = args.end_date
if args.overwrite:
    overwrite = args.overwrite
if args.mode:
    mode = args.mode
    if mode == 'all':
        # end_date = datetime.today().strftime('%Y-%m-%d')
        end_date = datetime.today()
 
zidates = generate_dates(start_date, end_date, '%Y-%m-%d')
pbar = tqdm(len(zidates))
ii = 0

conn = sqlite3.connect(db_filename)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS ''' + table_name + '''
            ("date"	TEXT,
            "json"	TEXT,
            PRIMARY KEY("date"))''')

tqdm.write(' -- dates in between: ' + start_date.strftime('%Y-%m-%d') + ' and ' + end_date.strftime('%Y-%m-%d'));
if overwrite: 
    tqdm.write(' -- overwriting previously saved dates')
else:
    tqdm.write(' -- skipping previously saved dates')

if overwrite is False:
    # exclude zidates that are already in the database
    c.execute("SELECT date from dates_lists WHERE date BETWEEN '" + start_date.strftime('%Y-%m-%d') + "' AND '" + end_date.strftime('%Y-%m-%d') + "';")
    sqlite_dates = [row[0] for row in c.fetchall()]
    if len(sqlite_dates):
        tqdm.write(' -- skipping ' + str(len(sqlite_dates)) + ' days found in the db')
    zidates = set(zidates) - set(sqlite_dates)
    zidates = list(zidates)
tqdm.write(' -- going through ' + str(len(zidates)) + ' days')

for oneday in tqdm(zidates):
    rows_to_insert = [] #db rows
    data = {'today': oneday, 'rand': random.random() }

    try:
        response = requests.post(url, headers=base_headers('headers1'), data=data)
    except Exception as e:
        logger.error('eRrx: '+ str(e))
    soup = BeautifulSoup(response.content, 'html.parser')
    json_data = {}
    for div in soup.find_all('div', class_='card-body'):
        ol = div.find('ol', class_='breadcrumb')
        key = ol.text.strip()
        # TODO: encode keys ex: Partea I -> PI, Partea II-a -> PII, Partea I Maghiară -> PIM
        value = {a.text: a['href'] for a in div.find_all('a', class_='btn')}
        json_data[key] = value
    json_result = json.dumps(json_data, ensure_ascii=False)
    rows_to_insert.append((oneday, json_result))

    # save the HTML content to a file
    if save_to_cache:
        with open(cache_dir + str(oneday)+ ".html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())
            if verbose:
               tqdm.write('written to ' + cache_dir + str(oneday)+ ".html") 

    if save_to_db:
        sql = '''INSERT INTO {} (date, json) VALUES (?, ?)
                ON CONFLICT(date) DO NOTHING'''.format(table_name)
        c.executemany(sql, rows_to_insert)
        conn.commit() 

    ii+=1
    # pbar.update(1)
    time.sleep(random.random()*2)
    if round(ii/pause_at) == ii/pause_at:
        time.sleep(pause)
        # os.system('say -v ioana "piiua " -r 250')

conn.close()
tqdm.write(str(ii) + ' days saved to db')
os.system('say -v ioana "în sfârșit, am gătat ' +  str(ii) + ' zile " -r 250')
