import requests
import csv

# Define the URL
url = 'http://statistici.insse.ro:8077/tempo-ins/matrix/matrices'
csv_filename = 'data/matrices.csv'
# Define the headers
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-GB,en;q=0.8',
    'Connection': 'keep-alive',
    'Referer': 'http://statistici.insse.ro:8077/tempo-online/',
    'Sec-GPC': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
}

# Send a GET request to the URL
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()

    # Define the CSV file name
    

    # Extract and flatten the data
    flattened_data = [[item['name'], item['code'], item['childrenUrl'], item['comment'], item['url']] for item in data]

    # Save the flattened data to a CSV file
    with open(csv_filename, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['name', 'code', 'childrenUrl', 'comment', 'url'])  # Write header
        csv_writer.writerows(flattened_data)

    print(f'Data saved as {csv_filename}')
else:
    print(f'Failed to fetch data. Status code: {response.status_code}')
