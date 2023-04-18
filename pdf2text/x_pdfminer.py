import os
from pdfminer.high_level import extract_text

output_dir = '../data/mo/text/pdfminer/'
# source = '../data/mo/pdfs/Monitorul-Oficial--PI--520Bis--2021.pdf'
source = '../data/mo/pdfs/Monitorul-Oficial--PII--75--2021.pdf'
filename = os.path.splitext(os.path.basename(source))[0]

# Extract the text from the PDF file
try:
    text = extract_text(source)
except Exception as e:
    print('err ' + str(e))

# Write the text to a file
with open(output_dir + filename + '.txt', 'w', encoding='utf-8') as f:
    f.write(text)
print('saved ' + output_dir + filename + '.txt')
