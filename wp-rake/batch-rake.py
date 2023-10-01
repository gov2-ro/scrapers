import requests
import json
import sqlite3
import csv
from tqdm import tqdm

# Define the SQLite database file
dbFile = '../../data/wp/wp-articles.db'

# Read the list of sites from the CSV file
sitelist = '../../data/wp/sites-wp.csv'
url_column = 2
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36"
}


# Create a SQLite connection and cursor
conn = sqlite3.connect(dbFile)
cursor = conn.cursor()

# Create the 'articles' table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain TEXT,
        date TEXT,
        date_gmt TEXT,
        guid TEXT,
        modified TEXT,
        modified_gmt TEXT,
        slug TEXT,
        status TEXT,
        type TEXT,
        link TEXT,
        title TEXT,
        content TEXT,
        excerpt TEXT,
        author TEXT,
        featured_media TEXT,
        comment_status TEXT,
        ping_status TEXT,
        sticky TEXT,
        template TEXT,
        format TEXT,
        categories TEXT,
        tags TEXT
    )
''')
conn.commit()


# Initialize counts
site_count = 0
article_count = 0
error_count = 0

# Loop through the list of sites
with open(sitelist, 'r') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # Skip the header row

    for row in tqdm(reader, desc="Sites"):
        site_url = row[url_column] 
        
        # Construct the API URL
        api_url = f"{site_url}/wp-json/wp/v2/posts"

        page_number = 1

        while True:
            # Make a request for the current page
            params = {"page": page_number}
            response = requests.get(api_url, headers=headers, params=params)

            try:
                response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
                data = response.json()

                if not data:
                    # No more data available, exit the loop
                    break

                # Save data to the SQLite database for each article
                for article_data in data:
                    article_count += 1
                    cursor.execute('''
                        INSERT INTO articles (domain, date, date_gmt, guid, modified, modified_gmt, slug, status, type, link, title, content, excerpt, author, featured_media, comment_status, ping_status, sticky, template, format, categories, tags)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        site_url,
                        article_data["date"],
                        article_data["date_gmt"],
                        article_data["guid"]["rendered"],
                        article_data["modified"],
                        article_data["modified_gmt"],
                        article_data["slug"],
                        article_data["status"],
                        article_data["type"],
                        article_data["link"],
                        article_data["title"]["rendered"],
                        article_data["content"]["rendered"],
                        article_data["excerpt"]["rendered"],
                        article_data["author"],
                        article_data["featured_media"],
                        article_data["comment_status"],
                        article_data["ping_status"],
                        article_data["sticky"],
                        article_data["template"],
                        article_data["format"],
                        json.dumps(article_data["categories"]),
                        json.dumps(article_data["tags"])
                    ))
                conn.commit()

                # Move to the next page
                page_number += 1

            except requests.exceptions.RequestException as e:
                print(f"Request failed with exception: {e}")
                error_count += 1
                break
            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON with exception: {e}")
                error_count += 1
                break

        site_count += 1

# Close the SQLite connection
conn.close()

print(f'DONE: Scraped {site_count} sites, {article_count} articles, encountered {error_count} errors.')
