import requests, json, sys, time, sqlite3
from bs4 import BeautifulSoup
import random
import logging
sys.path.append("../utils/")
from common import generate_dates

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

 """

db_filename = '../data/mo/mo.db'
table_name = 'dates_lists'
cache_dir = '../data/mo/cache/'
url = 'https://monitoruloficial.ro/ramo_customs/emonitor/get_mo.php'
start_date = '2000-01-04'
end_date = '2023-04-18'
start_date = '2017-07-15'
end_date = '2017-07-21'

zidates = generate_dates(start_date, end_date, '%Y-%m-%d')

headers = {
    'authority': 'monitoruloficial.ro',
    'accept': '*/*',
    'accept-language': 'en-GB,en;q=0.5',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'cookie': 'PHPSESSID=f2a8g1t1f8oldgi3pntsopgpjk',
    'origin': 'https://monitoruloficial.ro',
    'referer': 'https://monitoruloficial.ro/e-monitor/',
    'sec-ch-ua': '"Chromium";v="112", "Brave";v="112", "Not:A-Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest'
}
ii = 1
for oneday in zidates:
    rows_to_insert = []
    data = {
        'today': oneday,
        'rand': random.random()
    }

    try:
        response = requests.post(url, headers=headers, data=data)
    except Exception as e:
        logger.error('eRrx: '+ str(e))
    soup = BeautifulSoup(response.content, 'html.parser')
    json_data = {}
    for div in soup.find_all('div', class_='card-body'):
        ol = div.find('ol', class_='breadcrumb')
        key = ol.text.strip()
        value = {a.text: a['href'] for a in div.find_all('a', class_='btn')}
        json_data[key] = value
    json_result = json.dumps(json_data, ensure_ascii=False)
    # print(json_result)
    rows_to_insert.append((oneday, json_result))

    # save to file
    # save the HTML content to a file
    with open(cache_dir + str(oneday)+ ".html", "w", encoding="utf-8") as f:
        f.write(soup.prettify())
        print ('written to ' + cache_dir + str(oneday)+ ".html") 

    time.sleep(random.random()*3)
    
    # Connect to the database
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()

    # Create the laws_index table
    c.execute('''CREATE TABLE IF NOT EXISTS ''' + table_name + '''
                ("date"	TEXT,
                "json"	TEXT,
                PRIMARY KEY("date"))''')

    # c.executemany('''INSERT INTO ''' + table_name + ''' (date, json)
    #                 VALUES (?, ?)''', rows_to_insert)
    sql = '''INSERT INTO {} (date, json) VALUES (?, ?)
            ON CONFLICT(date) DO NOTHING'''.format(table_name)

    # Insert the rows into the table
    c.executemany(sql, rows_to_insert)
    conn.commit()  # Commit the changes for this row
    ii+=1

conn.close()
print(str(ii) + ' saved to db')
 