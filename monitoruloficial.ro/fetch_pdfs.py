""" 
default script worked but waits forever for large pdf, this shows pbar per each file
"""

db_filename = '../../data/mo/mo.db'
table_name = 'dates_lists'
output_folder = '../../data/mo/pdfs/'
url_base = 'https://monitoruloficial.ro'
shy_parts = ["III-a", "IV-a", "VI-a", "VII-a"]
logfile='../../data/mo/fetch_pdfs.log'
    
import sqlite3, json, requests, sys, os, time, random
import logging
from tqdm import tqdm
from urllib.parse import urlparse

sys.path.append("../utils/")
from common import base_headers

logging.basicConfig(
    # level=logging.DEBUG,
    # level=logging.INFO,
    level=logging.CRITICAL,
    
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logfile),
        logging.StreamHandler()
    ]
)

def log_request_details(response):
    """Log detailed information about the request and response"""
    # logging.debug("----- Request Details -----")
    logging.debug(f"URL: {response.url}")
    logging.debug(f"Status Code: {response.status_code}")
    logging.debug(f"Reason: {response.reason}")
    logging.debug("----- Response Headers -----")
    for header, value in response.headers.items():
        logging.debug(f"{header}: {value}")
    logging.debug("-------------------------")

def fetch_pdf(url_base, url, output_path, headers):
    """Fetch single PDF with detailed connection logging"""
    full_url = url_base + url
    parsed_url = urlparse(full_url)
    
    logging.info(f"Attempting to download: {full_url}")
    logging.debug(f"Using headers: {headers}")
    
    try:
        session = requests.Session()
        
        # First make a HEAD request to check the response headers
        head_response = session.head(full_url, headers=headers, timeout=30)
        log_request_details(head_response)
        
        if head_response.status_code == 403:
            logging.error("Access forbidden - possible rate limiting or authentication required")
            return False
            
        if head_response.status_code != 200:
            logging.error(f"Unexpected status code: {head_response.status_code}")
            return False
        
        # If head request successful, proceed with GET request
        logging.debug(f"Making GET request to {parsed_url.netloc}")
        response = session.get(full_url, headers=headers, timeout=30, stream=True)
        log_request_details(response)
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'application/pdf' not in content_type.lower():
                logging.warning(f"Unexpected content type: {content_type}")
            
            total_size = int(response.headers.get('content-length', 0))
            block_size = 8192
            
            with open(output_path, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc=os.path.basename(output_path)) as pbar:
                    for data in response.iter_content(block_size):
                        f.write(data)
                        pbar.update(len(data))
            
            logging.info(f"Successfully saved: {output_path}")
            return True
        else:
            logging.error(f"Failed to download: Status code {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        logging.error(f"Timeout downloading {full_url}")
        return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed for {full_url}: {str(e)}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error saving {full_url}: {str(e)}")
        return False

def main():
   
    os.makedirs(output_folder, exist_ok=True)
    
    try:
        conn = sqlite3.connect(db_filename)
        c = conn.cursor()
        c.execute('SELECT * FROM ' + table_name + ' ORDER BY date DESC')
        rows = c.fetchall()
        
        logging.info(f"Found {len(rows)} days in the database")
        
        for row in tqdm(rows, desc='days'):
            date, json_str = row
            try:
                json_dict = json.loads(json_str)
                
                for sectiune, parti in tqdm(json_dict.items(), desc='părți', leave=False):
                    if any(part in sectiune for part in shy_parts):
                        continue
                    
                    for nr, url in tqdm(parti.items(), desc='pdfs', leave=False):
                        filename = os.path.splitext(url[1:])[0]
                        urlparts = filename.split('--')
                        year = urlparts[-1]
                        
                        if not year.isdigit() or len(year) != 4:
                            logging.error(f"Invalid year format: {year} in URL: {url}")
                            continue
                        
                        year_dir = os.path.join(output_folder, str(year))
                        os.makedirs(year_dir, exist_ok=True)
                        output_path = os.path.join(year_dir, f"{filename}.pdf")
                        
                        if os.path.isfile(output_path):
                            logging.debug(f"File exists, skipping: {output_path}")
                            continue
                        
                        # Try to fetch the PDF
                        if fetch_pdf(url_base, url, output_path, base_headers('headers2')):
                            # Add a random delay between successful downloads
                            time.sleep(random.uniform(2.0, 4.0))
                        else:
                            # Add a longer delay after failed attempts
                            time.sleep(random.uniform(5.0, 8.0))
                
            except json.JSONDecodeError as e:
                logging.error(f"JSON decode error for date {date}: {str(e)}")
                continue
            except Exception as e:
                logging.error(f"Error processing date {date}: {str(e)}")
                continue
            
    except sqlite3.Error as e:
        logging.error(f"Database error: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()