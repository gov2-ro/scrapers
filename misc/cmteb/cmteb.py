import os, json, re, requests,  shutil, datetime
import wget
from bs4 import BeautifulSoup

ziurl = 'https://www.cmteb.ro/harta_stare_sistem_termoficare_bucuresti.php'
data_root = '/Users/pax/devbox/gov2/data/cmteb/'

def fetch_and_save_html(url):
    # Get the current date and time
    current_date_time = datetime.datetime.now().strftime('%y-%m-%d %H:%M')

    # Set a custom user agent to mimic a regular browser request
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    # Fetch the webpage content using requests
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch data from the website. HTTP Error {response.status_code}")
        return None

    # Save the HTML content to a file
    html_file = f'{data_root}/cached/{current_date_time}.html'
    with open(html_file, 'w', encoding='utf-8') as file:
        file.write(response.text)

    return html_file

    return html_file

def extract_json_from_html(html_file):
    # Read the local HTML file
    with open(html_file, 'r') as file:
        html_content = file.read()

    # Search for the JavaScript variables containing the required data
    passed_features = {}
    for color in ['verde', 'rosu', 'galben']:
        pattern = r'var passedFeatures_{} = (.+?);'.format(color)
        data = re.search(pattern, html_content)
        if data:
            data_str = data.group(1)
            passed_features[color] = json.loads(data_str)
        else:
            print(f"Data for '{color}' not found in the HTML.")

    return passed_features

def save_json_to_file(data):
    # Get the current date and time
    current_date_time = datetime.datetime.now().strftime('%y-%m-%d %H:%M')

    # Save the data to a JSON file
    json_file = f'{data_root}/parsed/{current_date_time}.json'
    with open(json_file, 'w') as file:
        json.dump(data, file)

    return json_file

def move_files(src_html, dest_html):
    # Create the 'parsed' directory if it doesn't exist
    os.makedirs(data_root + 'cached/parsed', exist_ok=True)

    # Move the HTML file to the 'parsed' directory
    shutil.move(src_html, dest_html)

if __name__ == "__main__":
    url = ziurl

    # Step 1: Fetch the URL and save the HTML file
    cached_html_file = fetch_and_save_html(url)

    # Step 2: Extract JSON from the HTML file
    data = extract_json_from_html(cached_html_file)

    # Step 3: Save JSON to a file
    json_file = save_json_to_file(data)

    # Move the HTML file to 'cached/parsed' directory
    moved_html_file = f'{data_root}/cached/parsed/{os.path.basename(cached_html_file)}'
    move_files(cached_html_file, moved_html_file)

    print(f"-- JSON data saved to '{json_file}' and HTML file moved to '{moved_html_file}' successfully.")
