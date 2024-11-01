import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import urllib3
from time import sleep
import os
from typing import Dict, List, Optional


class TempoExtractor:
    def __init__(self, base_dir='data/tempoins'):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }

    def load_existing_data(self, filepath):
        if os.path.exists(filepath):
            return pd.read_csv(filepath)
        return pd.DataFrame()

    def save_data(self, df, filepath):
        df.to_csv(filepath, index=False)
        print(f"Saved {len(df)} records to {filepath}")

    def find_data_table(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """Find the main content table while avoiding menu tables"""
        # First try to find the main content cell (td with width="80%")
        main_content = soup.find('td', attrs={'width': '80%'})
        if main_content:
            # Look for our table within this main content area
            return main_content.find('table')
            
        # Fallback: try to find table after the main content marker
        tempo_home = soup.find('strong', string="TEMPO - HOME")
        if tempo_home:
            # Get the containing table
            return tempo_home.find_parent('table')
            
        print("Could not find main content table")
        return None

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a page with retries"""
        print(f"Fetching URL: {url}")
        for attempt in range(3):
            try:
                response = requests.get(url, headers=self.headers, verify=False)
                response.raise_for_status()
                content_length = len(response.text)
                print(f"Successfully fetched page (length: {content_length})")
                
                # Debug the HTML structure if needed
                # with open('debug.html', 'w', encoding='utf-8') as f:
                #     f.write(response.text)
                    
                return BeautifulSoup(response.text, 'html.parser')
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt == 2:
                    return None
                sleep(1)
        return None

    def extract_level_1(self):
        """Extract main context listing"""
        output_path = f"{self.base_dir}/tempo_hierarchy.csv"
        
        soup = self.fetch_page('http://statistici.insse.ro/tempoins')
        if not soup:
            return None

        # Find target table
        target_table = soup.find('td', class_='leftMenuTableYellow').find_parent('table')
        if not target_table:
            print("Target table not found")
            return None

        records = []
        current_section = ''
        
        for row in target_table.find_all('tr'):
            if section_cell := row.find('strong'):
                current_section = section_cell.get_text(strip=True)
                print(f"Found section: {current_section}")
                continue
                
            cells = row.find_all('td')
            if len(cells) >= 2:
                code = cells[0].get_text(strip=True)
                if not re.match(r'^[A-Z]\.\d+$', code):
                    continue
                    
                if main_link := cells[1].find('a', class_='link'):
                    name = main_link.get_text(strip=True)
                    if context_match := re.search(r'context=(\d+)', main_link.get('href', '')):
                        print(f"Found item: {code} - {name}")
                        records.append({
                            'code': code,
                            'name': name,
                            'section': current_section,
                            'targetId': context_match.group(1),
                            'parentCode': '',
                            'level': 1
                        })

        df = pd.DataFrame(records)
        self.save_data(df, output_path)
        return df

    def extract_level_2(self):
        """Extract sub-contexts for each main context"""
        hierarchy_path = f"{self.base_dir}/tempo_hierarchy.csv"
        
        # Load level 1 data
        df = self.load_existing_data(hierarchy_path)
        if df.empty:
            print("No level 1 data found. Please run extract_level_1 first.")
            return None

        level_1_items = df[df['level'] == 1]
        new_records = []

        for _, row in level_1_items.iterrows():
            context = row['targetId']
            print(f"\nProcessing {row['code']}: {row['name']} (Context: {context})")
            
            url = f'http://statistici.insse.ro/tempoins/index.jsp?page=tempo2&lang=ro&context={context}'
            soup = self.fetch_page(url)
            if not soup:
                continue

            target_table = soup.find('td', class_='leftMenuTableYellow').find_parent('table')
            if not target_table:
                continue

            current_section = ''
            current_section_num = ''

            for tr in target_table.find_all('tr'):
                if section_text := tr.get_text(strip=True):
                    if match := re.match(r'^\s*(\d+)\.\s+(.+)$', section_text):
                        current_section_num = match.group(1)
                        current_section = match.group(2)
                        print(f"Found subsection: {current_section_num}. {current_section}")
                        continue

                cells = tr.find_all('td')
                if len(cells) >= 2:
                    code = cells[0].get_text(strip=True)
                    if not re.match(r'^\d+\.\d+$', code):
                        continue

                    if link := cells[1].find('a', class_='link'):
                        name = link.get_text(strip=True)
                        if context_match := re.search(r'context=(\d+)', link.get('href', '')):
                            hierarchical_code = f"{row['code']}.{current_section_num}.{code}"
                            print(f"Found item: {hierarchical_code} - {name}")
                            new_records.append({
                                'code': hierarchical_code,
                                'name': name,
                                'section': row['section'],
                                'targetId': context_match.group(1),
                                'parentCode': row['code'],
                                'level': 2
                            })

            sleep(0.5)

        if new_records:
            new_df = pd.DataFrame(new_records)
            complete_df = pd.concat([df, new_df], ignore_index=True)
            self.save_data(complete_df, hierarchy_path)
        return df

    def extract_level_3(self):
        """Extract final datasets"""
        hierarchy_path = f"{self.base_dir}/tempo_hierarchy.csv"
        
        # Load level 2 data
        df = self.load_existing_data(hierarchy_path)
        if df.empty:
            print("No level 2 data found. Please run extract_level_2 first.")
            return None

        level_2_items = df[df['level'] == 2]
        new_records = []

        for _, row in level_2_items.iterrows():
            context = row['targetId']
            print(f"\nProcessing {row['code']}: {row['name']} (Context: {context})")
            
            url = f'http://statistici.insse.ro/tempoins/index.jsp?page=tempo2&lang=ro&context={context}'
            soup = self.fetch_page(url)
            if not soup:
                continue

            target_table = soup.find('td', class_='leftMenuTableYellow').find_parent('table')
            if not target_table:
                continue

            for tr in target_table.find_all('tr'):
                cells = tr.find_all('td')
                if len(cells) >= 2:
                    code = cells[0].get_text(strip=True)
                    if not re.match(r'^\d+\.\d+$', code):
                        continue

                    if link := cells[1].find('a', class_='link'):
                        name = link.get_text(strip=True)
                        if ind_match := re.search(r'ind=([A-Z0-9]+)', link.get('href', '')):
                            hierarchical_code = f"{row['code']}.{code}"
                            print(f"Found item: {hierarchical_code} - {name}")
                            new_records.append({
                                'code': hierarchical_code,
                                'name': name,
                                'section': row['section'],
                                'targetId': ind_match.group(1),
                                'parentCode': row['code'],
                                'level': 3
                            })

            sleep(0.5)

        if new_records:
            new_df = pd.DataFrame(new_records)
            complete_df = pd.concat([df, new_df], ignore_index=True)
            self.save_data(complete_df, hierarchy_path)
        return df

def extract_level(level: int):
    """Extract a single level"""
    if level not in [1, 2, 3]:
        print("Invalid level. Must be 1, 2, or 3")
        return
        
    extractor = TempoExtractor()
    
    if level == 1:
        extractor.extract_level_1()
    elif level == 2:
        extractor.extract_level_2()
    else:
        extractor.extract_level_3()

def extract_all_levels():
    """Extract all levels in sequence"""
    extractor = TempoExtractor()
    
    print("Processing Level 1...")
    extractor.extract_level_1()
    
    print("\nProcessing Level 2...")
    extractor.extract_level_2()
    
    print("\nProcessing Level 3...")
    extractor.extract_level_3()
    
    print("\nAll levels completed")

if __name__ == "__main__":
    extract_all_levels()
    # Or for single level:
    # extract_level(1)  # Replace with desired level