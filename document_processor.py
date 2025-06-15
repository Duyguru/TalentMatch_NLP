from typing import Union
import PyPDF2
from docx import Document
import io

def extract_text_from_pdf(file_content: bytes) -> str:
    """
    PDF dosyasından metin çıkarma
    """
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
            
        return text
    except Exception as e:
        raise Exception(f"PDF dosyası işlenirken hata oluştu: {str(e)}")

def extract_text_from_docx(file_content: bytes) -> str:
    """
    DOCX dosyasından metin çıkarma
    """
    try:
        docx_file = io.BytesIO(file_content)
        doc = Document(docx_file)
        text = ""
        
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
            
        return text
    except Exception as e:
        raise Exception(f"DOCX dosyası işlenirken hata oluştu: {str(e)}")

def process_document(file_content: bytes, file_extension: str) -> str:
    """
    Dosya uzantısına göre belgeyi işle ve metni çıkar
    """
    if file_extension.lower() == '.pdf':
        return extract_text_from_pdf(file_content)
    elif file_extension.lower() == '.docx':
        return extract_text_from_docx(file_content)
    else:
        raise ValueError("Desteklenmeyen dosya formatı. Sadece PDF ve DOCX dosyaları desteklenir.") 