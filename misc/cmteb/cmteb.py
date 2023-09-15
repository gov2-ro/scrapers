import os, json, re, requests,  shutil, datetime
import wget
from bs4 import BeautifulSoup

ziurl = 'https://www.cmteb.ro/harta_stare_sistem_termoficare_bucuresti.php'
data_root = '/Users/pax/devbox/gov2/data/cmteb/'

def fetch_and_save_html(url):
    current_date_time = datetime.datetime.now().strftime('%y-%m-%d %H:%M')

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch data from the website. HTTP Error {response.status_code}")
        return None

    html_file = f'{data_root}/cached/{current_date_time}.html'
    with open(html_file, 'w', encoding='utf-8') as file:
        file.write(response.text)

    return html_file

    return html_file

def extract_json_from_html(html_file):
    with open(html_file, 'r') as file:
        html_content = file.read()

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
    current_date_time = datetime.datetime.now().strftime('%y-%m-%d %H:%M')
    
    json_file = f'{data_root}/parsed/{current_date_time}.json'
    with open(json_file, 'w') as file:
        json.dump(data, file)

    return json_file

def move_files(src_html, dest_html):
    os.makedirs(data_root + 'cached/parsed', exist_ok=True)
    shutil.move(src_html, dest_html)

if __name__ == "__main__":
    url = ziurl

    cached_html_file = fetch_and_save_html(url)

    data = extract_json_from_html(cached_html_file)

    json_file = save_json_to_file(data)

    moved_html_file = f'{data_root}/cached/parsed/{os.path.basename(cached_html_file)}'
    move_files(cached_html_file, moved_html_file)

    print(f"-- JSON data saved to '{json_file}' and HTML file moved to '{moved_html_file}' successfully.")
