
folder_path = 'data/anunturi'
output_csv_path = 'data/anunturi/anunturi.csv'

import csv
import os
import glob
from bs4 import BeautifulSoup
from markdownify import markdownify as md

def extract_job_details(file_path):
    # Step 1: Load the local HTML file
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Step 2: Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Step 3: Extract job details (title, employer, location, etc.)
    try:
        job_title = soup.select_one('.titlu h1').text.strip()
    except AttributeError:
        job_title = None

    try:
        employer = soup.select_one('.caseta .ang').text.strip()
    except AttributeError:
        employer = None

    try:
        location = soup.select_one('.card-job-post-category-wrapper:nth-child(1) .card-job-post-category-text').text.strip()
    except AttributeError:
        location = None

    try:
        job_level = soup.select_one('.card-job-post-category-wrapper:nth-child(2) .card-job-post-category-text').text.strip()
    except AttributeError:
        job_level = None

    try:
        job_type = soup.select_one('.card-job-post-category-wrapper:nth-child(3) .card-job-post-category-text').text.strip()
    except AttributeError:
        job_type = None

    try:
        employer_category = soup.select_one('.card-job-post-category-wrapper:nth-child(5) .card-job-post-category-text').text.strip()
    except AttributeError:
        employer_category = None

    # Extract the announcement link (<a href='...'>Anunt</a>)
    announcement_link_tag = soup.find('a', string='Anunt')
    if announcement_link_tag:
        announcement_url = announcement_link_tag['href']
    else:
        announcement_url = None

    # Extract the HTML content after the <a> tag (the main body of the job description)
    main_body_html = ''
    if announcement_link_tag:
        for sibling in announcement_link_tag.find_all_next():
            # Stop before <nav>
            if sibling.name == 'nav':
                break
            main_body_html += str(sibling)

        # Convert the HTML body to markdown
        # main_body_markdown = md(main_body_html)
        main_body_markdown = md(main_body_html).replace('\n', '\\n')

    else:
        main_body_markdown = None

    # Extract all other links that start with 'https://posturi.gov.ro/wp-content/uploads/' excluding 'Announcement URL'
    other_links = []
    for link in soup.find_all('a', href=True):
        url = link['href']
        if url.startswith('https://posturi.gov.ro/wp-content/uploads/') and url != announcement_url:
            other_links.append(url)

    # Return all extracted data as a dictionary
    return {
        'job_title': job_title,
        'employer': employer,
        'location': location,
        'job_level': job_level,
        'job_type': job_type,
        'employer_category': employer_category,
        'announcement_url': announcement_url,
        'main_body_markdown': main_body_markdown,
        'other_links': other_links
    }

def save_to_csv(data_list, output_csv_path):
    # CSV column headers
    headers = ['Job Title', 'Employer', 'Location', 'Job Level', 'Job Type', 'Employer Category', 'Announcement URL', 'Main Body Markdown', 'Other Links']

    # Writing to CSV
    with open(output_csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for data in data_list:
            writer.writerow({
                'Job Title': data['job_title'],
                'Employer': data['employer'],
                'Location': data['location'],
                'Job Level': data['job_level'],
                'Job Type': data['job_type'],
                'Employer Category': data['employer_category'],
                'Announcement URL': data['announcement_url'],
                'Main Body Markdown': data['main_body_markdown'],
                'Other Links': ', '.join(data['other_links'])  # Join other links into a single string
            })

def find_html_files(directory):
    # Use glob to find all HTML files recursively in the given directory
    return glob.glob(os.path.join(directory, '**/*.html'), recursive=True)

def process_html_files(directory, output_csv_path):
    # Find all HTML files in the directory recursively
    html_files = find_html_files(directory)

    # List to store all extracted job details
    all_job_details = []

    # Loop through each HTML file and extract the details
    for html_file in html_files:
        job_details = extract_job_details(html_file)
        all_job_details.append(job_details)

    # Save all extracted data to CSV
    save_to_csv(all_job_details, output_csv_path)

# Example usage:

# Process all HTML files in the folder and save to CSV
process_html_files(folder_path, output_csv_path)

# Output the results to console (optional)
print(f"Data saved to {output_csv_path}")
