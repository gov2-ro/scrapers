""" 
http://statistici.insse.ro:8077/tempo-ins/context/
 """
import requests
import pandas as pd

csv_filename = "data/context.csv"

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-GB,en;q=0.8',
    'Connection': 'keep-alive',
    'Referer': 'http://statistici.insse.ro:8077/tempo-online/',
    'Sec-GPC': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
}

# Define the URL
url = 'http://statistici.insse.ro:8077/tempo-ins/context/'

# Send the GET request with the specified headers
response = requests.get(url, headers=headers, verify=False)

# Send an HTTP GET request to fetch the JSON data
response = requests.get(url)
def flatten_json(y):
    """Recursively flatten JSON data."""
    out = {}

    def flatten(x, name=""):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + "_")
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + "_")
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out
# Check if the request was successful (HTTP status code 200)
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    
    # Flatten the JSON data
    flattened_data = []

   

    for item in data:
        flattened_item = flatten_json(item)
        flattened_data.append(flattened_item)

    # Create a DataFrame from the flattened data
    df = pd.DataFrame(flattened_data)

    # Extract the "Comunicate de presa" link from the name and add it as a new column
    df['Comunicate_de_presa_link'] = df['context_name'].str.extract(r'<a href="(.*?)">Comunicate de presa<\/a>')
    # Remove the "Comunicate de presa" part from the "context_name" column
    # df['context_name'] = df['context_name'].str.replace(r'<a href=".*?">Comunicate de presa<\/a>', '')
    df['context_name'] = df['context_name'].str.replace(r'<a href=".*?">Comunicate de presa<\/a>', '', regex=True)

    # Remove the unwanted columns
    df = df.drop(columns=['context_childrenUrl', 'context_comment', 'context_url'])

    
    
    df.to_csv(csv_filename, index=False)

    print(f"Data saved to {csv_filename}")
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")
