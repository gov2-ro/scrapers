import scrapy
import sqlite3

class MySpider(scrapy.Spider):
    name = 'my_spider'

    def start_requests(self):
        db_conn = sqlite3.connect(self.db)
        db_cursor = db_conn.cursor()
        db_cursor.execute("SELECT id, url FROM " + self.table)
        urls = db_cursor.fetchall()
        db_conn.close()

        for url in urls:
            yield scrapy.Request(url=url[1], callback=self.parse, meta={'id': url[0]})

    def parse(self, response):
        src_id = response.meta['id']

        db_conn = sqlite3.connect(self.db)
        db_cursor = db_conn.cursor()
        db_cursor.execute('''CREATE TABLE IF NOT EXISTS ''' + self.table + '''
                 (src_id TEXT, nrcrt TEXT, id_lege TEXT, titlu TEXT, stadiu TEXT, url TEXT)''')

        for row in response.xpath('//div[@class="grup-parlamentar-list"]/table/tbody/tr'):
            columns = row.xpath('./td')

            data = {
                'src_id': src_id,
                'nrcrt': columns[0].xpath('./text()').get(),
                'id_lege': columns[1].xpath('./text()').get(),
                'url': columns[1].xpath('./a/@href').get(),
                'titlu': columns[2].xpath('./text()').get(),
                'stadiu': columns[3].xpath('./text()').get(),
            }

            db_cursor.execute('INSERT INTO ' + self.table + ' (src_id, nrcrt, id_lege, titlu, stadiu, url) VALUES (?, ?, ?, ?, ?)', (data['src_id'], data['nrcrt'], data['id_lege'], data['titlu'], data['stadiu'], data['url']))
        print('-')
        db_conn.commit()
        db_conn.close()

db_filename = '../data/cdep/cdep.db'
table = 'src_years'

def crawl(db, table):
    process = scrapy.crawler.CrawlerProcess(settings={
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'DOWNLOAD_DELAY': 1.6
    })

    spider = MySpider()
    spider.db = db
    spider.table = table

    process.crawl(spider)
    process.start()

crawl(db_filename, table)

print('done')
