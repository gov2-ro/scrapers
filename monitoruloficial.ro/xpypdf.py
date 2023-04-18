# from pypdf import PdfReader
# import PyPDF2
import os
from tqdm import tqdm
from pypdf import PdfReader

output_dir = '../data/mo/text/PyPDF2/'
source = '../data/mo/pdfs/Monitorul-Oficial--PI--520Bis--2021.pdf'

reader = PdfReader(source)
filename = os.path.splitext(os.path.basename(source))[0]
text = ''
num_pages = len(reader.pages) 
pbar = tqdm(num_pages)
tqdm.write(str(num_pages) + ' pages')
for i in tqdm(range(num_pages)):
    # tqdm.write('p ' + str(i))
    try:
        page = reader.pages[i]
        text += page.extract_text() + "\r\n\r\n            ----------xxx----------- \r\n\r\n"
    except Exception as e:
        tqdm.write('  err: ' + str(e))

with open(output_dir + filename + '.txt', 'w', encoding='utf-8') as file:
    file.write(text)

tqdm.write ('done')