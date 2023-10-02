import requests
import json
import sqlite3
import csv
import re
from tqdm import tqdm

# Define the SQLite database file
dbFile = '../../data/wp/wp-articles4.db'

# Read the list of sites from the CSV file
sitelist = '../../data/wp/sites-wp.csv'
url_column = 2
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36"
}
timeout = 6

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

# Create the 'taxonomies' table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS taxonomies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain TEXT,
        tax_type TEXT,
        tax_id INTEGER,
        slug TEXT,
        posts TEXT,
        count INTEGER
    )
''')
conn.commit()

# Temporary variables to store tag slugs
tag_slugs_cache = {}

# Function to fetch tags for a post
def fetch_tags(post_id, site_url):
    if post_id in tag_slugs_cache:
        return tag_slugs_cache[post_id]

    tags_url = f"{site_url}/wp-json/wp/v2/tags?post={post_id}"
    response = requests.get(tags_url, headers=headers, timeout=timeout, allow_redirects=True)
    try:
        response.raise_for_status()
        tag_data = response.json()
        tag_slugs = [tag["slug"] for tag in tag_data]
        tag_slugs_cache[post_id] = tag_slugs
        return tag_slugs
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch tags for post {post_id} with exception: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Failed to decode tags JSON for post {post_id} with exception: {e}")
        return []

# Function to update the taxonomies table
def update_taxonomies(domain, tax_type, tax_id, slug, post_id):
    # Fetch the current posts JSON string from the taxonomies table
    cursor.execute('''
        SELECT posts FROM taxonomies
        WHERE domain = ? AND tax_type = ? AND slug = ?
    ''', (domain, tax_type, slug))
    current_posts_json = cursor.fetchone()

    if current_posts_json:
        # Parse the JSON string to a Python list
        current_posts = json.loads(current_posts_json[0])
    else:
        # If no record found, create a new list
        current_posts = []

    # Check if post_id is not already in the list
    if post_id not in current_posts:
        current_posts.append(post_id)

        # Update the taxonomies table with the updated posts list
        cursor.execute('''
            UPDATE taxonomies
            SET posts = ?
            WHERE domain = ? AND tax_type = ? AND slug = ?
        ''', (json.dumps(current_posts), domain, tax_type, slug))
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
        tqdm.write(site_url)
        # Construct the API URL
        api_url = f"{site_url}/wp-json/wp/v2/posts"

        page_number = 1

        while True:
            # Make a request for the current page
            params = {"page": page_number}
            response = requests.get(api_url, headers=headers, timeout=timeout, allow_redirects=True, params=params)

            try:
                response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
                data = response.json()

                if not data:
                    # No more data available, exit the loop
                    break

                # Save data to the SQLite database for each article
                for article_data in data:
                    article_count += 1
                    post_id = article_data["id"]
                    # Fetch tags and categories
                    tags = fetch_tags(post_id, site_url)
                    categories = article_data["categories"]  # Assuming you already have category slugs

                    # Update the taxonomies table
                    for tag_slug in tags:
                        update_taxonomies(site_url, "tag", post_id, tag_slug, post_id)

                    for category_slug in categories:
                        update_taxonomies(site_url, "category", post_id, category_slug, post_id)

                    cursor.execute('''
                        INSERT INTO articles (domain, date, date_gmt, guid, modified, modified_gmt, slug, status, type, link, title, content, excerpt, author, featured_media, comment_status, ping_status, sticky, template, format, categories, tags)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        re.sub(r'^(https?://)?(www\.)?', '', site_url),
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
                        json.dumps(categories),
                        json.dumps(tags)
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
