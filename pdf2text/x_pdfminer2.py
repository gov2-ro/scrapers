import os
from io import StringIO
from pdfminer.high_level import extract_text
from pdfminer.high_level import extract_text_to_fp


output_dir = '../data/mo/text/pdfminer/'
# source = '../data/mo/pdfs/Monitorul-Oficial--PI--520Bis--2021.pdf'
source = '../data/mo/pdfs/Monitorul-Oficial--PII--75--2021.pdf'
filename = os.path.splitext(os.path.basename(source))[0]


output_string = StringIO()

with open(source, 'rb') as fin:
    extract_text_to_fp(fin, output_string)

print(output_string.getvalue().strip())