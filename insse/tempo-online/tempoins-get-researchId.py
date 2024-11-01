import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from typing import Dict, Optional

def scrape_research_data(research_id: int) -> Optional[Dict]:
    """
    Scrape statistical research data from the given URL for a specific research ID.
    
    Args:
        research_id: The ID of the research to scrape
        
    Returns:
        Dictionary containing the scraped data, or None if the request fails
    """
    url = f'http://80.96.186.4:81/metadata/viewStatisticalResearch.htm?locale=ro&researchId={research_id}'
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching data for research ID {research_id}: {e}")
        return None
        
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the target table
    table = soup.find('table', class_='msrAdd')
    if not table:
        print(f"No data table found for research ID {research_id}")
        return None
        
    # Extract data from table rows
    data = {}
    for row in table.find_all('tr'):
        # Find the header cell (first column) and value cell
        header_cell = row.find('td', class_='localFirstColumn')
        value_cell = row.find_all('td')[-1]  # Last cell contains the value
        
        if header_cell and value_cell:
            # Clean up the text
            header = header_cell.get_text(strip=True).rstrip(':')
            value = value_cell.get_text(strip=True)
            
            # Store in dictionary
            data[header] = value
            
    return data

def save_to_csv(research_id: int, data: Dict) -> None:
    """
    Save the scraped data to a CSV file.
    
    Args:
        research_id: The ID of the research
        data: Dictionary containing the scraped data
    """
    # Create data/meta directory if it doesn't exist
    os.makedirs('data/meta', exist_ok=True)
    
    # Convert dictionary to DataFrame
    df = pd.DataFrame.from_dict(data, orient='index', columns=['Value'])
    
    # Save to CSV
    output_path = f'data/meta/{research_id}.csv'
    df.to_csv(output_path)
    print(f"Saved data to {output_path}")

def process_research_ids(research_ids: list) -> None:
    """
    Process multiple research IDs and save their data.
    
    Args:
        research_ids: List of research IDs to process
    """
    for research_id in research_ids:
        print(f"Processing research ID: {research_id}")
        data = scrape_research_data(research_id)
        
        if data:
            save_to_csv(research_id, data)
        else:
            print(f"Skipping research ID {research_id} due to errors")
        
# Example usage for a single ID
if __name__ == "__main__":
    # Example with a single ID
    research_id = 552  # Replace with your desired ID
    data = scrape_research_data(research_id)
    if data:
        save_to_csv(research_id, data)
    
    # Example with multiple IDs
    # research_ids = [552, 553, 554]  # Replace with your list of IDs
    # process_research_ids(research_ids)