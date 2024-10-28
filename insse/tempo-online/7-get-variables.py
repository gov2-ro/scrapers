import json
import csv
from pathlib import Path
import re

def extract_file_id(filename):
    """Extract the ID from filename (assumes format like 'ZEE1521.json')"""
    return re.search(r'([A-Z]+\d+)', filename).group(1)

def extract_dimension_labels(json_data):
    """Extract all labels from dimensionsMap"""
    try:
        dimensions_map = json_data.get('dimensionsMap', [])
        return [dim.get('label', '') for dim in dimensions_map if 'label' in dim]
    except (AttributeError, TypeError):
        return []

def process_matrices_folder(output_file='data/dimension_labels.csv'):
    """Process all JSON files in the matrices folder and save results to CSV"""
    # Define the matrices folder path
    matrices_path = Path('data/matrices')
    
    if not matrices_path.exists():
        print(f"Error: Folder not found: {matrices_path}")
        return
    
    # Store results
    results = []
    
    # Process each JSON file
    for json_file in matrices_path.glob('*.json'):
        try:
            print(f"Processing {json_file.name}...")
            
            # Read JSON content
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Extract file ID and labels
            file_id = extract_file_id(json_file.name)
            labels = extract_dimension_labels(json_data)
            
            # Store result
            results.append({
                'id': file_id,
                'labels': labels
            })
            
        except json.JSONDecodeError:
            print(f"Error reading JSON file: {json_file}")
        except Exception as e:
            print(f"Error processing file {json_file}: {str(e)}")
    
    # Write results to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'labels'])
        for result in results:
            writer.writerow([result['id'], '|'.join(result['labels'])])
    
    print(f"\nProcessed {len(results)} files")
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    process_matrices_folder()