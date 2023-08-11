import sqlite3
import scrapy
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerRunner

# Connect to the database
conn = sqlite3.connect('../data/cdep/cdep.db')
c = conn.cursor()
src_table = 'src_years'
table = 'laws_index'
c.execute('''CREATE TABLE IF NOT EXISTS ''' + table + '''
             (src_id TEXT, nrcrt TEXT, id_lege TEXT, titlu TEXT, stadiu TEXT, url TEXT)''')

# Define the scrapy spider
class LawsSpider(scrapy.Spider):
    name = 'laws_spider'

    # Define the start URLs from the src_years table
    start_urls = []
    for row in c.execute('SELECT url, id FROM ' + src_table):
        start_urls.append(row[0])
        src_id = row[1]

    # Parse the response from each URL
    def parse(self, response):
        # Loop through each row in the grup-parlamentar-list table
        for row in response.xpath('//div[@class="grup-parlamentar-list"]/table/tr'):
            # Extract the columns
            columns = row.xpath('td')

            # Extract the text and href values from the second column
            link_text = columns[1].xpath('a/text()').get()
            link_href = columns[1].xpath('a/@href').get()

            # Store the data in the laws_index table
            c.execute('INSERT INTO laws_index (nrcrt, id_lege, url, titlu, stadiu, src_id) VALUES (?, ?, ?, ?, ?, ?)',
                      (columns[0].xpath('text()').get(),
                       link_text,
                       columns[2].xpath('text()').get(),
                       columns[3].xpath('text()').get(),
                       src_id))

            # Commit the changes to the database
            conn.commit()

# Set up the crawler
settings = get_project_settings()
settings['REQUEST_FINGERPRINTER_IMPLEMENTATION'] = 'scrapy.fingerprint.NoopFingerprinter'
runner = CrawlerRunner(settings)

# Run the spider
runner.crawl(LawsSpider)
runner.join()

