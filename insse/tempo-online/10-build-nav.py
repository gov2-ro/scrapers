import json
import csv
import os
from typing import List, Dict
from datetime import datetime

def process_ancestors(ancestors: List[Dict], categories: List[Dict]):
    """Process ancestors and add them to categories list with proper level structure."""
    for level, ancestor in enumerate(ancestors):
        parent_code = ancestors[level - 1]['code'] if level > 0 else ''
        
        # Clean up name by removing HTML tags if present
        name = ancestor['name']
        if '<a href=' in name:
            name = name.split('<')[0].strip()
        
        category = {
            'level': level,
            'code': ancestor['code'],
            'parentCode': parent_code,
            'name': name,
            'comment': ancestor['comment'],
            'url': ancestor['url'],
            'childrenUrl': ancestor['childrenUrl']
        }
        
        # Only add if not already present (avoid duplicates)
        if not any(c['code'] == category['code'] and c['level'] == category['level'] for c in categories):
            categories.append(category)

def get_direct_ancestor(ancestors: List[Dict]) -> str:
    """Get the code of the last ancestor (with most digits)."""
    if not ancestors:
        return ''
    return ancestors[-1]['code']

def get_filters(dimensions_map: List[Dict]) -> str:
    """Convert dimensions_map labels to pipe-separated string."""
    if not dimensions_map:
        return ''
    return '|'.join(dim['label'] for dim in dimensions_map)

def get_source_link_number(surse_de_date: List[Dict]) -> str:
    """Get the linkNumber from surseDeDate if available."""
    if not surse_de_date:
        return ''
    return str(surse_de_date[0].get('linkNumber', '')) if surse_de_date else ''

def read_json_file(file_path: str) -> dict:
    """Try to read JSON file with different encodings."""
    encodings = ['utf-8', 'ISO-8859-1', 'windows-1252', 'latin1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return json.load(f)
        except UnicodeDecodeError:
            continue
        except json.JSONDecodeError:
            continue
    
    print(f"Failed to read file with any encoding: {file_path}")
    return None

def process_jsons(folder_path: str):
    """Process all JSON files in the specified folder."""
    categories = []
    datasets = []
    
    # Create output directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Process each JSON file in the folder
    for filename in os.listdir(folder_path):
        if not filename.endswith('.json'):
            continue
        
        file_path = os.path.join(folder_path, filename)
        data = read_json_file(file_path)
        
        if data is None:
            print(f"Skipping file due to encoding/parsing error: {filename}")
            continue
            
        try:
            # Process ancestors for categories.csv
            process_ancestors(data['ancestors'], categories)
            
            # Process dataset information for datasets.csv
            dataset = {
                'fileName': filename,
                'directAncestor': get_direct_ancestor(data['ancestors']),
                'matrixName': data.get('matrixName', ''),
                'surseDeDate.linkNumber': get_source_link_number(data.get('surseDeDate', [])),
                'definitie': data.get('definitie', ''),
                'metodologie': data.get('metodologie', ''),
                'ultimaActualizare': data.get('ultimaActualizare', ''),
                'observatii': data.get('observatii', ''),
                'persoaneResponsabile': data.get('persoaneResponsabile', ''),
                'filters': get_filters(data.get('dimensionsMap', []))
            }
            datasets.append(dataset)
        except Exception as e:
            print(f"Error processing file {filename}: {str(e)}")
            continue
    
    # Write categories.csv
    with open('data/x-categories.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['level', 'code', 'parentCode', 'name', 'comment', 'url', 'childrenUrl'])
        writer.writeheader()
        writer.writerows(categories)
    
    # Write datasets.csv
    with open('data/x-datasets.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['fileName', 'directAncestor', 'matrixName', 
                                             'surseDeDate.linkNumber', 'definitie', 'metodologie',
                                             'ultimaActualizare', 'observatii', 'persoaneResponsabile',
                                             'filters'])
        writer.writeheader()
        writer.writerows(datasets)

# Run the processor
process_jsons('data/matrices/')