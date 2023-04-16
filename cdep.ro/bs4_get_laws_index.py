import sqlite3, time
import requests
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, filename='scraping.log')

# Connect to the database
conn = sqlite3.connect('../data/cdep/cdep.db')
c = conn.cursor()

# Create the laws_index table
c.execute('''CREATE TABLE IF NOT EXISTS laws_index
             (nrcrt INTEGER PRIMARY KEY,
              id_lege TEXT,
              titlu TEXT,
              stadiu TEXT,
              url TEXT,
              src_id TEXT)''')

# Loop through rows in the src_years table
select_query = 'SELECT * FROM src_years'
rows = c.execute(select_query)

# num_rows = len(rows.fetchall())
# print(num_rows)

rows_to_insert = []
ii = 0
for row in rows:
    ii+=1
    time.sleep(.7) 
    logging.debug(f'Processing row {row[0]}')
    # print('ss')    
    # Get the URL for this row
    url = row[3]
    # print(str(ii) + '/' + str(num_rows) + ' ' + str(row[0]) + url)
    print(url)
    
    # Scrape the page
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        print('err')
        logging.error(f'Error scraping URL {url}: {e}')
        continue
    
    # Find the table containing the data we want
   
    try:
        table = soup.find('div', {'class': 'grup-parlamentar-list'}).find('table')
        
        # Loop through the rows in the table
        for tr in table.find_all('tr'):
            # print('--');
            # Get the columns of the row
            cols = [td.text.strip() for td in tr.find_all('td')]
            
            # Check that there are four columns (some rows might be empty)
            if len(cols) == 4:
                # Get the link in the second column
                link = tr.find_all('td')[1].find('a')
                href = link['href'] if link else ''
                
                # Add the row to the list
                rows_to_insert.append((cols[0], cols[1], cols[2], cols[3], href, row[0]))
        
        # Insert all the rows at once

    except Exception as e:
        print('4444')
        logging.error(f'Error processing URL {url}: {e}')
c.executemany('''INSERT INTO laws_index (nrcrt, id_lege, titlu, stadiu, url, src_id)
                VALUES (?, ?, ?, ?, ?, ?)''', rows_to_insert)
conn.commit()  # Commit the changes for this row
# Close the connection
conn.close()

# Print a message to indicate that the program is done
print('Done')
