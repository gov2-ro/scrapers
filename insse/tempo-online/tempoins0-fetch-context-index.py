import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import urllib3

def extract_tempo_contexts(save_path='data/tempoins/context.csv'):
    # Suppress SSL warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Browser headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    try:
        # Fetch webpage
        response = requests.get(
            'http://statistici.insse.ro/tempoins',
            headers=headers,
            verify=False
        )
        response.raise_for_status()
        
        # Find table containing "TEMPO - HOME"
        soup = BeautifulSoup(response.text, 'html.parser')
        target_table = soup.find('strong', string="TEMPO - HOME").find_parent('table')
        
        if not target_table:
            raise ValueError("Target table not found")
            
        # Process table contents
        sections, codes, names, contexts = [], [], [], []
        current_section = ''
        
        for row in target_table.find_all('tr'):
            # Check for section header
            if section_cell := row.find('strong'):
                current_section = section_cell.get_text(strip=True)
                continue
                
            # Process data rows
            cells = row.find_all('td')
            if len(cells) < 2:
                continue
                
            code = cells[0].get_text(strip=True)
            if not re.match(r'^[A-Z]\.\d+$', code):
                continue
                
            if main_link := cells[1].find('a', class_='link'):
                name = main_link.get_text(strip=True)
                if context_match := re.search(r'context=(\d+)', main_link.get('href', '')):
                    sections.append(current_section)
                    codes.append(code)
                    names.append(name)
                    contexts.append(context_match.group(1))
        
        # Create and save DataFrame
        df = pd.DataFrame({
            'section': sections,
            'code': codes,
            'name': names,
            'context': contexts
        })
        df.to_csv(save_path, index=False)
        print(f"Saved {len(df)} entries to {save_path}")
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching webpage: {e}")
        return None
    except Exception as e:
        print(f"Error processing data: {e}")
        return None

if __name__ == "__main__":
    extract_tempo_contexts()