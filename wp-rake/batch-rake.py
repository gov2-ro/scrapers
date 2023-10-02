import requests
import json
import sqlite3
import csv
import re
from tqdm import tqdm

# Define the SQLite database file
dbFile = '../../data/wp/wp-articles6.db'

# Read the list of sites from the CSV file
sitelist = '../../data/wp/sites-wp.csv'
url_column = 2
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36"
}

# Function to get the total number of URLs
def get_total_urls(csv_file):
    with open(csv_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        return sum(1 for _ in reader) - 1  # Subtract 1 for the header row

# Get the total number of URLs
total_urls = get_total_urls(sitelist)

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
        slug TEXT,
        posts TEXT,
        count INTEGER
    )
''')
conn.commit()

# Temporary variables to store tag and category slugs
tag_slugs_cache = {}
category_slugs_cache = {}

# Function to fetch tags for a post
def fetch_tags(post_id, site_url):
    if post_id in tag_slugs_cache:
        return tag_slugs_cache[post_id]

    tags_url = f"{site_url}/wp-json/wp/v2/tags?post={post_id}"
    response = requests.get(tags_url, headers=headers)
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

# Function to fetch categories for a post
def fetch_categories(post_id, site_url):
    if post_id in category_slugs_cache:
        return category_slugs_cache[post_id]

    categories_url = f"{site_url}/wp-json/wp/v2/categories?post={post_id}"
    response = requests.get(categories_url, headers=headers)
    try:
        response.raise_for_status()
        category_data = response.json()
        category_slugs = [category["slug"] for category in category_data]
        category_slugs_cache[post_id] = category_slugs
        return category_slugs
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch categories for post {post_id} with exception: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Failed to decode categories JSON for post {post_id} with exception: {e}")
        return []

# Function to update the taxonomies table
def update_taxonomies(domain, tax_type, slug, post_id):
    cursor.execute('''
        INSERT OR IGNORE INTO taxonomies (domain, tax_type, slug, posts, count)
        VALUES (?, ?, ?, ?, 0)
    ''', (domain, tax_type, slug, json.dumps([])))
    cursor.execute('''
        UPDATE taxonomies
        SET posts = json_insert(posts, '$[#]', ?), count = count + 1
        WHERE domain = ? AND tax_type = ? AND slug = ?
    ''', (json.dumps(post_id), domain, tax_type, slug))
    conn.commit()

# Initialize counts
site_count = 0
article_count = 0
error_count = 0

# Initialize live counters
total_articles = 0
fetch_errors = 0

# Create a tqdm progress bar
with tqdm(total=total_urls, desc="Sites", dynamic_ncols=True) as pbar:
    # Loop through the list of sites
    with open(sitelist, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        for row in reader:
            site_url = row[url_column]
            parsed_domain = re.sub(r'^(https?://)?(www\.)?', '', site_url).strip('/')
            tag_slugs_cache = {}  # Clear the tag slugs cache for each site
            category_slugs_cache = {}  # Clear the category slugs cache for each site

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
                        post_id = article_data["id"]
                        # Fetch tags and categories
                        tags = fetch_tags(post_id, site_url)
                        categories = fetch_categories(post_id, site_url)

                        # Update the taxonomies table for tags
                        for tag_slug in tags:
                            update_taxonomies(parsed_domain, "tag", tag_slug, post_id)

                        # Update the taxonomies table for categories
                        for category_slug in categories:
                            update_taxonomies(parsed_domain, "category", category_slug, post_id)

                        cursor.execute('''
                            INSERT INTO articles (domain, date, date_gmt, guid, modified, modified_gmt, slug, status, type, link, title, content, excerpt, author, featured_media, comment_status, ping_status, sticky, template, format, categories, tags)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            parsed_domain,
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
                        total_articles += 1

                    conn.commit()

                    # Update the live counters in the progress bar description
                    pbar.set_description(f"Sites: {site_count}, Articles: {total_articles}, Fetch Errors: {fetch_errors}")

                    # Move to the next page
                    page_number += 1

                except requests.exceptions.RequestException as e:
                    print(f"Request failed with exception: {e}")
                    error_count += 1
                    fetch_errors += 1
                    break
                except json.JSONDecodeError as e:
                    print(f"Failed to decode JSON with exception: {e}")
                    error_count += 1
                    fetch_errors += 1
                    break

            site_count += 1

# Close the SQLite connection
conn.close()

print(f'DONE: Scraped {site_count} sites, {total_articles} articles, encountered {fetch_errors} fetch errors.')
