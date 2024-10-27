import os, requests, time, random
import pandas as pd
from tqdm import tqdm

# Directory where files will be saved
download_dir = 'data/downloads'
csv_path = 'data/anunturi.csv'  # Update this to the actual path

# Create the directory if it doesn't exist
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# Function to download a file from a given URL
def download_file(url, save_dir):
    try:
        # Extract the filename from the URL
        filename = os.path.basename(url)
        file_path = os.path.join(save_dir, filename)

        # Check if file already exists
        if os.path.exists(file_path):
            tqdm.write(f"File already exists: {filename}. Skipping download.")
            return file_path

        # Send a GET request to download the file
        response = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://posturi.gov.ro/',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'TE': 'Trailers'
        }, stream=True)
        response.raise_for_status()  # Check for any HTTP errors

        # Download the file in chunks
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        tqdm.write(f"Successfully downloaded: {filename}")
        return file_path
    except requests.exceptions.RequestException as e:
        tqdm.write(f"Failed to download {url}: {e}")
        return None

# Function to process the CSV and download all files from 'Announcement URL' and 'Other Links'
def download_from_csv(csv_path, download_dir):
    # Read the CSV file
    df = pd.read_csv(csv_path)

    # Process each row in the CSV
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing rows"):
        # Download the 'Announcement URL'
        if pd.notna(row['Announcement URL']):
            tqdm.write(f"Processing Announcement URL: {row['Announcement URL']}")
            download_file(row['Announcement URL'], download_dir)

        # Download files from 'Other Links'
        if pd.notna(row['Other Links']):
            other_links = row['Other Links'].split(', ')  # Assuming other links are comma-separated
            for link in other_links:
                tqdm.write(f"Processing Other Link: {link}")
                download_file(link, download_dir)
                sleep_time = random.uniform(0.5, 1.1)  # Random sleep time between 0.5 and 1.1 seconds
                time.sleep(sleep_time)

download_from_csv(csv_path, download_dir)

tqdm.write("Download process completed.")