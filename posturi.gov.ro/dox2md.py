import os
import sys
import subprocess
import docx2txt
import pypandoc
from pdf2image import convert_from_path
import pytesseract
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Download pandoc if it's not already installed
try:
    pypandoc.get_pandoc_version()
except OSError:
    logging.info("Pandoc not found. Attempting to download...")
    pypandoc.download_pandoc()
    logging.info("Pandoc has been downloaded and installed.")

def convert_doc_to_markdown(file_path):
    logging.info(f"Converting DOC file: {file_path}")
    temp_docx = file_path + ".docx"
    try:
        subprocess.run(['soffice', '--headless', '--convert-to', 'docx', '--outdir', os.path.dirname(file_path), file_path], check=True)
        logging.info(f"DOC converted to DOCX: {temp_docx}")
        markdown = convert_docx_to_markdown(temp_docx)
        os.remove(temp_docx)
        return markdown
    except subprocess.CalledProcessError as e:
        logging.error(f"Error converting DOC to DOCX: {e}")
        raise

def convert_docx_to_markdown(file_path):
    logging.info(f"Converting DOCX file: {file_path}")
    try:
        # First attempt: using docx2txt and pypandoc
        text = docx2txt.process(file_path)
        markdown = pypandoc.convert_text(text, 'md', format='plain')
        logging.info("DOCX conversion completed using docx2txt and pypandoc")
        return markdown
    except Exception as e:
        logging.warning(f"First conversion method failed: {e}")
        try:
            # Second attempt: direct conversion with pypandoc
            markdown = pypandoc.convert_file(file_path, 'md')
            logging.info("DOCX conversion completed using direct pypandoc conversion")
            return markdown
        except Exception as e:
            logging.error(f"All conversion methods failed. Final error: {e}")
            raise

def convert_pdf_to_markdown(file_path):
    logging.info(f"Converting PDF file: {file_path}")
    try:
        images = convert_from_path(file_path)
        logging.info(f"PDF converted to {len(images)} images")
        text = ""
        for i, image in enumerate(images):
            logging.info(f"Performing OCR on page {i+1}")
            text += pytesseract.image_to_string(image)
        markdown = pypandoc.convert_text(text, 'md', format='plain')
        logging.info("PDF conversion completed")
        return markdown
    except Exception as e:
        logging.error(f"Error converting PDF to Markdown: {e}")
        raise

def convert_to_markdown(file_path):
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()

    if file_extension == '.doc':
        return convert_doc_to_markdown(file_path)
    elif file_extension == '.docx':
        return convert_docx_to_markdown(file_path)
    elif file_extension == '.pdf':
        return convert_pdf_to_markdown(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

def batch_convert(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    supported_extensions = ['.doc', '.docx', '.pdf']
    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)
        _, file_extension = os.path.splitext(filename)
        
        if file_extension.lower() in supported_extensions:
            try:
                logging.info(f"Starting conversion of {filename}")
                markdown_content = convert_to_markdown(file_path)
                output_file = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.md")
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                logging.info(f"Conversion complete. Output saved to {output_file}")
                print(f"Converted: {filename} -> {os.path.basename(output_file)}")
            except Exception as e:
                logging.error(f"Error converting {filename}: {str(e)}")
                print(f"Error converting {filename}: {str(e)}")
        else:
            logging.warning(f"Skipping unsupported file: {filename}")
            print(f"Skipping unsupported file: {filename}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_directory> <output_directory>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isdir(input_dir):
        print(f"Error: {input_dir} is not a valid directory")
        sys.exit(1)

    batch_convert(input_dir, output_dir)

if __name__ == "__main__":
    main()