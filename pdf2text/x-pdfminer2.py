import os
from pdfminer.high_level import extract_text

output_dir = '../../data/mo/text/pdfminer/'
# source = '../../data/mo/pdfs/Monitorul-Oficial--PI--520Bis--2021.pdf'
source = '../../data/mo/pdfs/2021/Monitorul-Oficial--PII--75--2021.pdf'
filename = os.path.splitext(os.path.basename(source))[0]


def pdf_to_txt(path):
    from io import StringIO

    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfdocument import PDFDocument
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.pdfpage import PDFPage
    from pdfminer.pdfparser import PDFParser

    output_string = StringIO()
    with open(path, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
    text = str(output_string.getvalue())
    return text

file = './2014-NaBITA-Whitepaper-Text-with-Graphics.pdf'

pdfminersix_test = pdf_to_txt(source)
 
# Write the text to a file
with open(output_dir + filename + '.txt', 'w', encoding='utf-8') as f:
    f.write(pdfminersix_test)
print('saved ' + output_dir + filename + '.txt')