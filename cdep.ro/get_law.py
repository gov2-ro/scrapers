import requests
from bs4 import BeautifulSoup
import sqlite3
import json
from urllib.parse import parse_qs, urlparse
import logging



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# set up the SQLite database connection
conn = sqlite3.connect('example.db')
c = conn.cursor()


def hrefs_json1(input_soup):
    xjson_data = {}
    for a_tag in input_soup.find_all('a'):
        idm = a_tag['href'].split('idm=')[1].split('&')[0]
        leg = a_tag['href'].split('leg=')[1].split('&')[0]
        cam = a_tag['href'].split('cam=')[1]
        key = int(leg + cam + idm)
        value = a_tag.text
        xjson_data[key] = value
    return json.dumps(xjson_data)

def table_initiatori(inner_table):
    json_data = {}
    rows = inner_table.find_all('tr')
    for row in rows:
        print('-row--')
        subcells = row.find_all('td')
        if len(subcells) >= 2:
            subkey = subcells[0].text.replace(":", "").replace(" - ", " ").strip()
            print(subkey)
            # subvalue = subcells[1].text.strip()
            zilist = subcells[1]
            ll = hrefs_json1(zilist)
            try:               
                json_data[subkey] = ll 
            except Exception as e:
                logger.error('err: '+ str(e))
                breakpoint()

def table_consultanti(inner_table):
    json_data = {}
    rows = inner_table.find_all('tr')
    for row in rows:
        print('-row--')
        subcells = row.find_all('td')
        if len(subcells) >= 2:
            # 2nd td has value name
            # 1st td has link
            # subkey = subcells[0].text.replace(":", "").replace(" - ", " ").strip()
            subkey = subcells[1].text.strip()
            hrefz = ''
            for a_tag in subcells[0].find_all('a'):
                hrefz = a_tag['href']
            json_data[subkey] = hrefz
    return(json_data)

def hrefs2(input_soup):
    xjson_data = {}
    for a_tag in input_soup.find_all('a'):
        hrefz = a_tag['href']

# create a table for the scraped data
c.execute('''CREATE TABLE IF NOT EXISTS initiatives
             (title TEXT, descriere TEXT, nr_inregistrare TEXT, cdep TEXT,
              senat TEXT, guvern TEXT, proc_leg TEXT, camera_decizionala TEXT,
              termen_adoptare TEXT, tip_initiativa TEXT, caracter TEXT, p_urgenta TEXT,
              stadiu TEXT, initiator TEXT, initiatori TEXT, consultanti TEXT, caseta_lista TEXT)''')

# set the URL to scrape
url = 'https://www.cdep.ro/pls/proiecte/upl_pck2015.proiect?cam=2&idp=10730'

# scrape the webpage using requests and BeautifulSoup
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# scrape the title and description
title = soup.select_one('div.boxTitle h1').text
descriere = soup.select_one('div.detalii-initiativa h4').text
print(title + ' --> ' + descriere)
# scrape the table data
detalii_initiativa_rows = soup.select('div.detalii-initiativa table tr')
data = {}
for row in detalii_initiativa_rows:
    tds = row.find_all('td')
    if len(tds) >= 2:
        key = tds[0].text.strip()
        value = tds[1].text.strip()

        # detect the variable name based on the substring found in the first column
        if 'Nr. înregistrare' in key:
            data['nr_inregistrare'] = value
        elif 'Camera Deputatilor' in key:
            data['cdep'] = value
        elif 'Senat' in key:
            data['senat'] = value
        elif 'Guvern' in key:
            data['guvern'] = value
        elif 'Procedura legislativa' in key:
            data['proc_leg'] = value
        elif 'Camera decizionala' in key:
            data['camera_decizionala'] = value
        elif 'Termen adoptare' in key:
            data['termen_adoptare'] = value
        elif 'Tip initiativa' in key:
            data['tip_initiativa'] = value
        elif 'Caracter' in key:
            data['caracter'] = value
        elif 'Procedura de urgenta' in key:
            data['p_urgenta'] = value
        elif 'Stadiu' in key:
            data['stadiu'] = value
        elif 'Initiator' in key:
            # check if there is an inner table in the second td
            # TODO: see if text outside table
            inner_table = tds[1].find('table')
            if inner_table:
                # data['initiatori'] = json.dumps(json_data)
                data['initiatori'] = table_initiatori(inner_table)
            else:
                data['initiator'] = value
            # 
    
        elif 'Consultati' in key:
            # check if there is an inner table in the second td
            inner_table = tds[1].find('table')
            if inner_table:
                # data['initiatori'] = json.dumps(json_data)
                data['consultanti'] = table_consultanti(inner_table)
            else:
                data['consultanti'] = value
        

# breakpoint()