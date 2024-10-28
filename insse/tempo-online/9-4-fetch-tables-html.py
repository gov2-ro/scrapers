import requests
import json
from urllib3.exceptions import InsecureRequestWarning
import logging
from typing import Dict, List, Any
import os
import pathlib

# Suppress only the single InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_matrix_definition(file_path: str) -> Dict:
    """Load and parse the matrix definition file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading matrix definition: {e}")
        raise

def clean_response_data(response_data: Dict) -> str:
    """Clean the response data by removing extra quotes and escaping."""
    try:
        # Extract the result table string
        table_str = response_data.get('resultTable', '')
        
        # Remove surrounding quotes if they exist
        if table_str.startswith('"') and table_str.endswith('"'):
            table_str = table_str[1:-1]
            
        # Replace escaped quotes with regular quotes
        table_str = table_str.replace('\\"', '"')
        
        # Handle any specific escape sequences if needed
        table_str = table_str.replace('\\n', '\n')
        
        return table_str
    except Exception as e:
        logger.error(f"Error cleaning response data: {e}")
        raise

def convert_to_payload(matrix_def: Dict) -> Dict:
    """Convert matrix definition to API payload format."""
    payload = {
        "language": "ro",
        "arr": []
    }
    
    # Extract and convert each dimension from dimensionsMap
    for dim in matrix_def["dimensionsMap"]:
        # Filter options to remove "Total" when there are other options
        options = dim["options"]
        if len(options) > 1:
            options = [opt for opt in options if opt["label"].strip().lower() != "total"]
            
        if options:  # Only add dimension if it has options after filtering
            payload["arr"].append([
                {
                    "label": opt["label"],
                    "nomItemId": opt["nomItemId"],
                    "offset": opt["offset"],
                    "parentId": opt["parentId"]
                }
                for opt in options
            ])
    
    # Add matrix metadata
    payload["matrixName"] = matrix_def["matrixName"]
    payload["matrixDetails"] = matrix_def["details"]
    
    return payload

def fetch_insse_data(matrix_code: str, matrix_def: Dict, output_dir: str) -> None:
    """
    Fetch data from INSSE API using the matrix definition.
    
    Args:
        matrix_code: The code of the matrix (e.g., 'POP107D')
        matrix_def: The loaded matrix definition dictionary
        output_dir: Directory to save output files
    """
    # Convert to payload format
    logger.info(f"Converting matrix definition for {matrix_code} to payload format")
    payload = convert_to_payload(matrix_def)
    
    # Save payload for reference
    # payload_file = os.path.join(output_dir, f"sample-curl-payload-{matrix_code}.json")
    # with open(payload_file, 'w', encoding='utf-8') as f:
    #     json.dump(payload, f, ensure_ascii=False, indent=2)
    # logger.info(f"Saved payload to {payload_file}")
    
    # Prepare request
    url = f'http://statistici.insse.ro:8077/tempo-ins/matrix/{matrix_code}'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-GB,en;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'http://statistici.insse.ro:8077',
        'Pragma': 'no-cache',
        'Referer': 'http://statistici.insse.ro:8077/tempo-online/',
        'Sec-GPC': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    }
    
    try:
        # Make request
        logger.info(f"Making request to {url}")
        response = requests.post(url, json=payload, headers=headers, verify=False)
        response.raise_for_status()
        
        # Parse the initial JSON response
        json_response = response.json()
        
        # Clean and parse the result table
        cleaned_table = clean_response_data(json_response)
        
        # Save cleaned response
        response_file = os.path.join(output_dir, f"{matrix_code}_response.html")
        with open(response_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_table)  # Write the cleaned HTML/table string
        logger.info(f"Saved cleaned response to {response_file}")
        
        # Also save raw response
        # raw_response_file = os.path.join(output_dir, f"{matrix_code}_response.txt")
        # with open(raw_response_file, 'w', encoding='utf-8') as f:
        #     f.write(response.text)
        # logger.info(f"Saved raw response to {raw_response_file}")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making request for {matrix_code}: {e}")
        if hasattr(e.response, 'text'):
            logger.error(f"Response content: {e.response.text[:500]}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON response for {matrix_code}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing {matrix_code}: {e}")
        raise

def process_matrices_folder(input_folder: str, output_folder: str) -> None:
    """
    Process all JSON files in the input folder and fetch their data.
    
    Args:
        input_folder: Path to folder containing matrix definition JSON files
        output_folder: Path to folder where results should be saved
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Get all JSON files in input folder
    input_path = pathlib.Path(input_folder)
    json_files = list(input_path.glob('*.json'))
    
    if not json_files:
        logger.warning(f"No JSON files found in {input_folder}")
        return
    
    logger.info(f"Found {len(json_files)} JSON files to process")
    
    for json_file in json_files:
        try:
            # Extract matrix code from filename (assuming format like "POP107D sample.json")
            matrix_code = json_file.stem.split()[0]
            
            logger.info(f"Processing {json_file.name}")
            
            # Load matrix definition
            matrix_def = load_matrix_definition(str(json_file))
            
            # Fetch data
            fetch_insse_data(matrix_code, matrix_def, output_folder)
            
        except Exception as e:
            logger.error(f"Error processing {json_file.name}: {e}")
            continue
    
    logger.info("Finished processing all matrix files")

if __name__ == "__main__":
    process_matrices_folder(
        input_folder="data/matrices",
        output_folder="data/tables"
    )