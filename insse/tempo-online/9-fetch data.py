import requests
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def fetch_insse_data():
    # Create session with retry strategy
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Try both HTTP and HTTPS URLs
    urls = [
        'https://statistici.insse.ro:8077/tempo-ins/matrix/POP107A',
        'http://statistici.insse.ro:8077/tempo-ins/matrix/POP107A'
    ]
    
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-GB,en;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'https://statistici.insse.ro:8077',
        'Pragma': 'no-cache',
        'Referer': 'https://statistici.insse.ro:8077/tempo-online/',
        'Sec-GPC': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    }

    # Load the complete payload from your sample
    with open('sample-payload.json', 'w', encoding='utf-8') as f:
        json.dump({
            "language": "ro",
            "arr": [
                [{"label": "Total", "nomItemId": 1, "offset": 1, "parentId": None}],
                [
                    {"label": "Masculin ", "nomItemId": 106, "offset": 2, "parentId": None},
                    {"label": "Feminin ", "nomItemId": 107, "offset": 3, "parentId": None}
                ],
                # Full counties array from your sample
                [{"label": "Alba", "nomItemId": 3064, "offset": 2, "parentId": None},
                 {"label": "Arad", "nomItemId": 3065, "offset": 3, "parentId": None},
                 # ... include all counties ...],
                [{"label": "TOTAL", "nomItemId": 112, "offset": 0, "parentId": 112}],
                # Full years array from your sample
                [{"label": "Anul 1992", "nomItemId": 4285, "offset": 1, "parentId": None},
                 {"label": "Anul 1993", "nomItemId": 4304, "offset": 2, "parentId": None},
                 # ... include all years ...],
                [{"label": "Numar persoane", "nomItemId": 9685, "offset": 1, "parentId": None}]
            ],
            "matrixName": "POPULATIA DUPA DOMICILIU la 1 ianuarie pe grupe de varsta si varste, sexe, judete si localitati",
            "matrixDetails": {
                "nomJud": 3,
                "nomLoc": 4,
                "matMaxDim": 6,
                "matUMSpec": 0,
                "matSiruta": 1,
                "matCaen1": 0,
                "matCaen2": 0,
                "matRegJ": 0,
                "matCharge": 0,
                "matViews": 0,
                "matDownloads": 0,
                "matActive": 1,
                "matTime": 5
            }
        }, f, ensure_ascii=False, indent=2)

    # Load the payload
    with open('sample-payload.json', 'r', encoding='utf-8') as f:
        payload = json.load(f)

    success = False
    for url in urls:
        try:
            print(f"\nTrying URL: {url}")
            response = session.post(url, json=payload, headers=headers, verify=False, timeout=30)
            
            print(f"Status Code: {response.status_code}")
            print("Response Headers:", dict(response.headers))
            
            if not response.text:
                print("Warning: Empty response received")
                continue
                
            print("\nFirst 500 characters of response:", response.text[:500])
            
            # Save raw response
            with open('raw_response.txt', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("\nRaw response saved to 'raw_response.txt'")
            
            # Try to parse JSON
            if response.status_code == 200 and response.text:
                try:
                    json_response = response.json()
                    with open('insse_response.json', 'w', encoding='utf-8') as f:
                        json.dump(json_response, f, ensure_ascii=False, indent=2)
                    print("\nJSON response successfully saved to 'insse_response.json'")
                    success = True
                    break
                except json.JSONDecodeError as e:
                    print(f"\nError decoding JSON: {e}")
                    print("Response content type:", response.headers.get('Content-Type'))
            else:
                print(f"\nRequest failed with status code: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"Network error with {url}: {e}")
        except IOError as e:
            print(f"Error saving file: {e}")

    if not success:
        print("\nFailed to get valid response from any URL")
        
if __name__ == "__main__":
    fetch_insse_data()