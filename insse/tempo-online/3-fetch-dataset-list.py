""" 
reads context.csv or tempo-context.json
loops datasets, gets dataset saves to csv

- read data/context.csv
- fetch each context, save to data/context/{context_code}.csv

 """
import requests
import csv
import pandas as pd
import json
import os

# Define the URL
inputCsv = 'data/context.csv'

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-GB,en;q=0.8',
    'Connection': 'keep-alive',
    'Referer': 'http://statistici.insse.ro:8077/tempo-online/',
    'Sec-GPC': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
}




# Read the CSV file
df = pd.read_csv(inputCsv)

#  loop df
for index, row in df.iterrows():
    print(row)
    
    # fetch http://statistici.insse.ro:8077/tempo-ins/context/<context_code> and save to data/context/<context_code>.json
    context_code = row['context_code']
    url = f'http://statistici.insse.ro:8077/tempo-ins/context/{context_code}'
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        with open(f'data/context/{context_code}.json', 'w') as json_file:
            json.dump(data, json_file)
    else:
        print(f'Failed to fetch data for context {context_code}. Status code: {response.status_code}')
    
    
    
    