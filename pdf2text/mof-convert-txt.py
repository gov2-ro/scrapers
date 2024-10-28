import PyPDF2
import os
import re
import sys

rootFolder = '../../data/mo/'
txtFolder = rootFolder + 'text/ciocan/'
pdfFolder = rootFolder + '_obsolete/small size samples/'

# date = sys.argv[1]

# print(f'Processing {date}:')

# if not os.path.exists(f'data/pdf/{date}'):
#     exit(f'Error: {date} does not exist')

unique_numbers = set()
file_list = os.listdir(f'{pdfFolder}')

for file_name in file_list:
    match = re.search(r'--(\d+)-', file_name)
    if match:
        unique_numbers.add(int(match.group(1)))

sorted_numbers = sorted(list(unique_numbers))

for number in sorted_numbers:
    text = ''
    idx = sorted_numbers.index(number) + 1
    filtered_files = [file_name for file_name in file_list if f'--{number}-' in file_name]
    total_pages = len(filtered_files)
    print(f'[{idx}/{len(sorted_numbers)}] processing {number} ({total_pages} pages) ...')

    for page in range(1, total_pages + 1):
        filename = f'{pdfFolder}/{number}-p{str(page).zfill(2)}.pdf'
        # print(filename) 
        pdf_file = open(filename, 'rb')
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text_page = pdf_reader.pages[0].extract_text()
        if page == 1:
            lines = text_page.split('\n')
            text_page = '\n'.join(lines[:-3])
        else:
            lines = text_page.split('\n')
            text_page = '\n'.join(lines[1:])
            if page < 10:
                text_page = text_page[:-1]
            else:
                text_page = text_page[:-2]
        text += text_page

    if not os.path.exists(f'{pdfFolder}'):
        os.makedirs(f'{pdfFolder}')

    output_file = open(f'{txtFolder}/{number}.txt', 'w')
    output_file.write(text)
    output_file.close()
    pdf_file.close()