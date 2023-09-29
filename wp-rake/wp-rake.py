import requests
import json

url = "https://www.adr.gov.ro/wp-json/wp/v2/posts"
dataRoot = '../../data/wp/adr/'
fileName='adr.gov.ro'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36"
}

page_number = 1

while True:
    # Make a request for the current page
    params = {"page": page_number}
    response = requests.get(url, headers=headers, params=params)

    try:
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        data = response.json()
        
        if not data:
            # No more data available, exit the loop
            break

        # Save the JSON data to a separate file for each page
        file_path = f"{dataRoot}{fileName}-{page_number}.json"
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)
        
        print(f"Data for page {page_number} has been saved to {file_path}")

        # Move to the next page
        page_number += 1

    except requests.exceptions.RequestException as e:
        print(f"Request failed with exception: {e}")
        break
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON with exception: {e}")
        break

print('DONE saved ' + str(page_number) + 'jsons')