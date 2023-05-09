import requests, sqlite3, sys, json, logging
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse
from datetime import datetime
sys.path.append("../utils/")
from common import readfile, writefile
from json_from_html import html2obj


""" 
## TODOs

- [x] consultanți
- [x] inițiatori
- [ ] caseta electronica a deputatului
- [ ] Derularea procedurii legislative
- [ ] create function
- [ ] check for updates - if no new data skip, if new data, store new version

# TODO: get downloads inside derulare procedura

 """

db_filename = '../../data/cdep/cdep.db'
table = 'laws'

ignore_keys = ['width', 'cellspacing', 'cellpadding', 'border', 'style', 'valign', 'height', 'colspan', 'align', 'nowrap', 'bgcolor']
inputfile ='../../data/cdep/sample/Pl-x nr. 8_2010.html'
outputfile ='../../data/cdep/sample/Pl-x nr. 8_2010.json'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        # xrint('-row--')
        subcells = row.find_all('td')
        if len(subcells) >= 2:
            # breakpoint()
            subkey = subcells[0].text.replace(':','')
            # xrint(subkey)
            # subvalue = subcells[1].text.strip()
            zilist = subcells[1]
            ll = hrefs_json1(zilist)
            try:               
                json_data[subkey] = json.loads(ll) 
            except Exception as e:
                logger.error('err: '+ str(e))
                breakpoint()
    return(json_data)

def table_consultanti(inner_table):
    json_data = {}
    rows = inner_table.find_all('tr')
    for row in rows:
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

def table_derulare_procedura(inner_table):
    # first 5 rows to be ignored
    # starts at first <tr valign="top"><td align="center" bgcolor="#fff0d8">
    # only  <tr valign="top"> are relevant
    # detect date on the left, concatenate strings on the right (see <td colspan="2"> - can have subtable ), until next date or end
    # <dd><table> has downloads or html links 
    

    json_data = {}
    # rows = inner_table.find_all('tr')
    # tbody = inner_table.find('tbody')
    # breakpoint()
    rows = inner_table.children #so only immediate rows
    for row in rows:
        if row.name != 'tr':
            continue
        if (not row.has_attr("valign")) or row["valign"] != "top":
            continue
        # subcells = row.find_all('td')
        subcells = row.children #only the immediate tds
        lx = 0
        for td in subcells:
 
            if td.name != 'td':
                continue
            
            if lx == 0:
                subkey = td.text.strip()
                if subkey != '':
                    datekey = subkey
            if lx == 2:
                # TODO: get html not td.text
                # if it has dd , table etc

                if datekey not in json_data:
                    json_data[datekey] = []
                    json_data[datekey].append(html2obj(td, ignore_keys))
                else:                    
                    json_data[datekey].append(html2obj(td, ignore_keys))
            lx += 1
    return json_data

def derulare_proc(td_soup):
    # break into pieces
    obj = {}
    ii = 0
    for node in td_soup.contents:
        ii +=1
        if node.name is None:
            # print(node)  # Text-only node
            # obj[ii]=node.text
            # obj[ii]=str(node)
            obj[ii]=node #is already str?
        else:
            # Tag node 
            # TODO: ook for:
            #   dd > table td  a (check if a doc or pdf and if siblings, get name from adjacent td - which can be text or link)
            #   div#obs - can have text and inner links
  


            print(str(node))  

def hrefs2(input_soup):
    xjson_data = {}
    for a_tag in input_soup.find_all('a'):
        hrefz = a_tag['href']

def doTables(input_soup):
    filtered_html = ''
    for tag in input_soup.recursiveChildGenerator():
        # if tag.name == 'a' or tag.name == 'img':
        if tag.name == 'a':
            filtered_html += tag.decode_contents().replace('\n', '')
        elif not tag.name:
            filtered_html += tag.replace('\n', '')
    return filtered_html


url = 'https://www.cdep.ro/pls/proiecte/upl_pck2015.proiect?cam=2&idp=10730'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# meat = readfile(inputfile) #TODO: hardcoded, to remove
# soup = BeautifulSoup(meat, 'html.parser')

# scrape the title and description
title = soup.select_one('div.boxTitle h1').text
descriere = soup.select_one('div.detalii-initiativa h4').text
vezi_operatiuni = soup.find('a', string='vezi si operatiile de la Senat')
if vezi_operatiuni is not None:
    vezi_operatiuni_url = vezi_operatiuni['href']
else:
    vezi_operatiuni_url = ''

# xrint(title + ' --> ' + descriere)

# scrape the table data
detalii_initiativa_rows = soup.select('div.detalii-initiativa table tr')
data = {}
data ={
    "nr_inregistrare":"",
    "cdep":"",
    "senat":"",
    "guvern":"",
    "proc_leg":"",
    "camera_decizionala":"",
    "termen_adoptare":"",
    "tip_initiativa":"",
    "caracter":"",
    "p_urgenta":"",
    "stadiu":""
}
# data = {"nr_inregistrare":"","cdep":"","senat":"","guvern":"","proc_leg":"","camera_decizionala":"","termen_adoptare":"","tip_initiativa":"","caracter":"","p_urgenta":"","stadiu:"}
for row in detalii_initiativa_rows:
    tds = row.find_all('td')
    if len(tds) >= 2:
        key = tds[0].text.strip()
        value = tds[1].text.strip()

        # detect the variable name based on the substring found in the first column
        if 'B.P.I' in key:
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
                data['initiatori'] = json.dumps(table_initiatori(inner_table), ensure_ascii=False)
            else:
                data['initiator'] = value
    

        elif 'Consultati' in key:
            # check if there is an inner table in the second td
            # TODO: also get `caseta electronica a deputatului`
            inner_table = tds[1].find('table')
            if inner_table:
                # data['initiatori'] = json.dumps(json_data)
                data['consultanti'] = json.dumps(table_consultanti(inner_table), ensure_ascii=False) 
            else:
                data['consultanti'] = value

# Derularea procedurii legislative
derulare_procedura = soup.find("div", {"id": "olddiv"}).find("table", recursive=False)
# data['derulare_procedura'] = table_derulare_procedura(derulare_procedura)
data['derulare_procedura'] = json.dumps(table_derulare_procedura(derulare_procedura), ensure_ascii=False)

print(data['derulare_procedura'])
sys.exit()
# TODO: check if exists
# write to db

conn = sqlite3.connect(db_filename)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS laws
             (title text, descriere text, nr_inregistrare text, cdep text, senat text,
              guvern text, proc_leg text, camera_decizionala text, termen_adoptare text,
              tip_initiativa text, caracter text, p_urgenta text, stadiu text,
              initiator text, initiatori text, consultanti text, derulare_procedura, caseta_lista text, vezi_senat, fetch_date text
              , PRIMARY KEY("nr_inregistrare")
              )''')
# FIXME: if nr inregistrare primay key can't overwrite 
 
#  TODO: check if exists, later add new version only if different data
qxx = "INSERT INTO " + table + " (title, descriere, nr_inregistrare, cdep, senat, guvern, proc_leg, camera_decizionala, termen_adoptare, tip_initiativa, caracter, p_urgenta, stadiu, consultanti, initiatori, derulare_procedura, vezi_senat, fetch_date) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
 
# breakpoint()
try:
    c.execute(qxx, (title  , descriere , data['nr_inregistrare'], data['cdep'], data['senat'], data['guvern'], data['proc_leg'], data['camera_decizionala'], data['termen_adoptare'], data['tip_initiativa'], data['caracter'], data['p_urgenta'], data['stadiu'] , data['consultanti'], data['initiatori'], data['derulare_procedura'], vezi_operatiuni_url, datetime.today().strftime('%y%m%d')))
except Exception as e:
    logger.error('eRrx: '+ str(e) + "\n\r" + qxx )
    breakpoint()
 
conn.commit()
conn.close()

print(f'Data written to {db_filename}')