""" 
loops dataset list csv, fetches fields for each and saves as json, per dataset
 """
import pandas as pd
import requests
import os
from tqdm import tqdm
import time

# Define the paths
csv_file = 'data/matrices.csv'
output_directory = 'data/matrices'
error_log_file = 'data/error.log'
zitimeout = 10
sleeptime = 0.3

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Read the CSV file into a DataFrame
df = pd.read_csv(csv_file)

# Create a tqdm progress bar
progress_bar = tqdm(total=len(df), unit='file')

# Headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Function to download JSON data and handle errors
def download_json(code):
    url = f'http://statistici.insse.ro:8077/tempo-ins/matrix/{code}.json'
    output_file = os.path.join(output_directory, f'{code}.json')

    try:
        # Make an HTTP request to download the JSON data with timeout
        response = requests.get(url, headers=headers, timeout=zitimeout)

        if response.status_code == 200:
            # Save the JSON data to the specified file
            with open(output_file, 'wb') as json_file:
                json_file.write(response.content)
            progress_bar.update(1)  # Update the progress bar
            progress_bar.set_description(f'Downloaded {code}.json')
        else:
            with open(error_log_file, 'a') as error_log:
                error_log.write(f'Failed to download {code}.json. Status code: {response.status_code}\n')
            progress_bar.update(1)  # Update the progress bar even for failures

    except requests.exceptions.RequestException as e:
        with open(error_log_file, 'a') as error_log:
            error_log.write(f'Failed to download {code}.json. Error: {str(e)}\n')
        progress_bar.update(1)  # Update the progress bar even for exceptions

# Loop through each row in the DataFrame
for index, row in df.iterrows():
    code = row['code']
    download_json(code)
    time.sleep(sleeptime)  # Pause for 0.5 seconds to avoid overloading the server

# Close the tqdm progress bar
progress_bar.close()
