import os
from PyPDF2 import PdfReader


def load_document(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    if file_path.endswith('.txt'):
        return load_text_file(file_path)
    if file_path.endswith('.pdf'):
        return load_pdf_file(file_path)
    
def load_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content

def load_pdf_file(file_path):
    reader = PdfReader(file_path)
    content = ""
    for page in reader.pages:
        content += page.extract_text() + "\n"
    return content

def main(file_path):
    document_content = load_document(file_path)
    print(document_content)

if __name__ == "__main__":
    test_file_path = "Chroma_DB_Filtering.pdf"
    main(test_file_path)
