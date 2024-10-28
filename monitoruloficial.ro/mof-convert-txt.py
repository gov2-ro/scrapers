import PyPDF2
import os
import re
import sys
from typing import List, Tuple

def detect_formatting(page) -> str:
    """
    Extract text with formatting from a PDF page.
    Preserves document layout including blank lines and centering.
    """
    try:
        # Extract text while preserving layout
        text = page.extract_text()
        
        # Split into lines, preserving empty lines
        lines = text.split('\n')
        formatted_lines = []
        
        # Track document sections for better spacing
        in_header = True
        last_was_blank = False
        
        for line in lines:
            stripped = line.strip()
            
            # Handle completely empty lines
            if not stripped:
                if not last_was_blank:  # Avoid multiple consecutive blank lines
                    formatted_lines.append('')
                last_was_blank = True
                continue
            
            last_was_blank = False
            
           # Detect centered titles and headers
            is_centered = False
            if re.match(r'^[A-Z\s]+$', stripped) or \
            re.match(r'^D\s*E\s*C\s*R\s*E\s*T', stripped) or \
            stripped.startswith('PREȘEDINTELE') or \
            re.match(r'^Art\.\s*\d+\.?\s*—', stripped):
                is_centered = True

            # Format based on type
            if is_centered:
                formatted_lines.append('')  # Add space before centered text
                formatted_lines.append(f'**{stripped}**')
                formatted_lines.append('')  # Add space after centered text
            elif re.match(r'^[A-Z][A-Z\s]+:', stripped):  # Section headers
                formatted_lines.append('')
                formatted_lines.append(f'**{stripped}**')
            elif any(keyword in stripped for keyword in [
                'MONITORUL OFICIAL', 'PARLAMENTUL ROMÂNIEI', 
                'CAMERA DEPUTAȚILOR', 'SENATUL', 'GUVERNUL ROMÂNIEI'
            ]):
                if in_header:  # Only add extra spacing in document header
                    formatted_lines.append('')
                formatted_lines.append(f'**{stripped}**')
                formatted_lines.append('')
            else:
                # Regular text - preserve indentation
                leading_spaces = len(line) - len(line.lstrip())
                if leading_spaces > 0:
                    formatted_lines.append('    ' + stripped)  # Convert to markdown indentation
                else:
                    formatted_lines.append(stripped)
            
            # No longer in header section after first non-header content
            if in_header and not is_centered and not any(keyword in stripped for keyword in [
                'MONITORUL OFICIAL', 'PARLAMENTUL ROMÂNIEI', 
                'CAMERA DEPUTAȚILOR', 'SENATUL'
            ]):
                in_header = False
        
        return '\n'.join(formatted_lines)
            
    except Exception as e:
        print(f"Warning: Could not extract formatting: {str(e)}")
        return page.extract_text()

def clean_output(text: str) -> str:
    """Clean up the formatted text."""
    # Remove excessive blank lines (more than 2 consecutive)
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    
    # Ensure proper spacing around centered elements
    text = re.sub(r'(\*\*[A-Z][A-Z\s]+\*\*)\n(?!\n)', r'\1\n\n', text)
    
    # Ensure articles have proper spacing
    text = re.sub(r'(\*\*Art\.[^\n]+\*\*)\n(?!\n)', r'\1\n\n', text)
    
    return text.strip()

rootFolder = '../../data/mo/'
txtFolder = rootFolder + 'text/ciocan/'
pdfFolder = rootFolder + '_obsolete/small size samples/'

# Get list of PDF files
file_list = [f for f in os.listdir(pdfFolder) if f.endswith('.pdf')]

# Extract numbers using the correct pattern
unique_numbers = set()
for file_name in file_list:
    match = re.search(r'Monitorul-Oficial--PI--(\d+)--\d{4}\.pdf', file_name)
    if match:
        unique_numbers.add(int(match.group(1)))

sorted_numbers = sorted(list(unique_numbers))

# Make sure output directory exists
if not os.path.exists(txtFolder):
    os.makedirs(txtFolder)

# Process each unique number
for number in sorted_numbers:
    markdown_text = ''
    idx = sorted_numbers.index(number) + 1
    
    # Find the matching file for this number
    matching_file = None
    for file_name in file_list:
        if f'--{number}--' in file_name:
            matching_file = file_name
            break
    
    if matching_file:
        print(f'[{idx}/{len(sorted_numbers)}] processing {number} ...')
        
        try:
            filename = os.path.join(pdfFolder, matching_file)
            with open(filename, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                
                # Extract text from all pages
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    
                    # Get formatted text
                    page_text = detect_formatting(page)
                    
                    # Process first page
                    if page_num == 0:
                        lines = page_text.split('\n')
                        # Keep more lines from header, remove only pure footer
                        page_text = '\n'.join(lines[:-2])
                    else:
                        # Process subsequent pages
                        lines = page_text.split('\n')
                        if len(lines) > 2:
                            # Remove header/footer but preserve document structure
                            page_text = '\n'.join(lines[1:-2])
                    
                    markdown_text += page_text + '\n\n\n'
            
            # Clean up the final text
            markdown_text = clean_output(markdown_text)
            
            # Write output file
            output_path = os.path.join(txtFolder, f'{number}.md')
            with open(output_path, 'w', encoding='utf-8') as output_file:
                output_file.write(markdown_text)
                
        except Exception as e:
            print(f"Error processing file {matching_file}: {str(e)}")