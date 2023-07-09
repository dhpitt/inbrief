"""
Code to extract text from pdfs
"""

import argparse
import re 

import textract
import pypdf

def pdf_to_txt(filepath: str):
    """
    Parse an English PDF using textract's default Enligsh OCR functionality. 
    """
    reader = pypdf.PdfReader(filepath)
    num_pages = len(reader.pages)
    text = textract.process(filename=filepath)
    text = text.decode("utf-8")

    return re.sub("[\W+ ]", " ", text).encode("utf-8"), num_pages

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filepath")
    args = parser.parse_args()
    text, num_pages = pdf_to_txt(filepath=args.filepath)
    print(f"ingested {num_pages} pages")
    with open("test.txt", "wb+") as f:
        f.write(text)
        f.close()
     
    


    



