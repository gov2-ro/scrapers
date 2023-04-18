import os
from pdf2docx import Converter
from pdf2image import convert_from_path
from PIL import Image

output_dir = '../data/mo/text/pdf2docx/'
# source = '../data/mo/pdfs/Monitorul-Oficial--PI--520Bis--2021.pdf'
source = '../data/mo/pdfs/Monitorul-Oficial--PII--75--2021.pdf'

filename = os.path.splitext(os.path.basename(source))[0]

pdf_file = source
docx_file = output_dir + filename + '.docx'

# convert pdf to docx
cv = Converter(pdf_file)
cv.convert(docx_file)      # all pages by default
cv.close()

 