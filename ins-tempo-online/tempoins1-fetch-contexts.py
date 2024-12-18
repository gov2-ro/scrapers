import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import urllib3
from time import sleep
import os

def load_existing_datasets(filepath):
    """Load existing dataset records if file exists"""
    if os.path.exists(filepath):
        return pd.read_csv(filepath)
    return pd.DataFrame(columns=['section', 'code', 'name', 'context'])

def save_new_records(new_records, existing_df, filepath):
    """Save new records while avoiding duplicates"""
    if not new_records:
        return existing_df
        
    new_df = pd.DataFrame(new_records)
    
    # Concatenate and drop duplicates based on code and context
    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    deduped_df = combined_df.drop_duplicates(subset=['code', 'context'], keep='last')
    
    # Save to CSV
    deduped_df.to_csv(filepath, index=False)
    return deduped_df

def extract_datasets(output_path='data/tempoins/dataset-list.csv'):
    # Suppress SSL warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Browser headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    # Load existing datasets
    dataset_df = load_existing_datasets(output_path)
    
    # Read context.csv
    context_df = pd.read_csv('data/tempoins/context.csv')
    
    # First ensure all context entries are saved
    context_records = context_df.to_dict('records')
    dataset_df = save_new_records(context_records, dataset_df, output_path)
    print(f"Saved {len(context_df)} context entries")

    # Process each context
    for index, row in context_df.iterrows():
        context = row['context']
        parent_section = row['section']
        parent_code = row['code']
        parent_name = row['name']
        
        print(f"Processing {parent_code}: {parent_name} (Context: {context})")
        
        url = f'http://statistici.insse.ro/tempoins/index.jsp?page=tempo2&lang=ro&context={context}'
        
        try:
            # Fetch page with retry mechanism
            for attempt in range(3):
                try:
                    response = requests.get(url, headers=headers, verify=False)
                    response.raise_for_status()
                    break
                except requests.exceptions.RequestException:
                    if attempt == 2:
                        raise
                    sleep(1)

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find target table
            target_link = soup.find('a', {'href': './?lang=ro', 'class': 'link'}, string='TEMPO - HOME')
            if not target_link:
                continue
                
            target_table = target_link.find_parent('table')
            current_section = ''
            current_section_num = ''
            new_records = []
            
            # Process table rows
            for row in target_table.find_all('tr'):
                # Check for section headers
                if section_text := row.get_text(strip=True):
                    if match := re.match(r'^\s*(\d+)\.\s+(.+)$', section_text):
                        current_section_num = match.group(1)
                        current_section = match.group(2)
                        continue
                
                # Process dataset entries
                cells = row.find_all('td')
                if len(cells) >= 2:
                    code = cells[0].get_text(strip=True)
                    if not re.match(r'^\d+\.\d+$', code):
                        continue
                    
                    if dataset_link := cells[1].find('a', class_='link'):
                        name = dataset_link.get_text(strip=True)
                        if ind_match := re.search(r'ind=([A-Z0-9]+)', dataset_link.get('href', '')):
                            hierarchical_code = f"{parent_code}.{current_section_num}.{code}"
                            
                            new_records.append({
                                'section': parent_section,
                                'code': hierarchical_code,
                                'name': name,
                                'context': ind_match.group(1)
                            })
            
            # Save new records from this page
            if new_records:
                dataset_df = save_new_records(new_records, dataset_df, output_path)
                print(f"Saved {len(new_records)} new datasets for {parent_code}")
            
            # Add small delay between requests
            sleep(0.5)
            
        except Exception as e:
            print(f"Error processing context {context}: {e}")
            continue

    print(f"Completed. Total records: {len(dataset_df)}")
    return dataset_df

if __name__ == "__main__":
    extract_datasets()