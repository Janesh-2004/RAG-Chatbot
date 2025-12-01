"""
Utility functions for the RAG chatbot
"""
import os
from typing import List
from pypdf import PdfReader
from docx import Document


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted text as a string
    """
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise RuntimeError(f"Error extracting text from PDF: {str(e)}") from e


def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text content from a DOCX file.
    
    Args:
        file_path: Path to the DOCX file
        
    Returns:
        Extracted text as a string
    """
    try:
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        raise RuntimeError(f"Error extracting text from DOCX: {str(e)}") from e


def extract_text_from_txt(file_path: str) -> str:
    """
    Extract text content from a TXT file.
    
    Args:
        file_path: Path to the TXT file
        
    Returns:
        Extracted text as a string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise RuntimeError(f"Error extracting text from TXT: {str(e)}") from e


def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from a file based on its extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Extracted text as a string
    """
    extension = os.path.splitext(file_path)[1].lower()
    
    if extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif extension == '.docx':
        return extract_text_from_docx(file_path)
    elif extension == '.txt':
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {extension}")


def format_docs(docs: List) -> str:
    """
    Format a list of documents into a single string.
    
    Args:
        docs: List of document objects
        
    Returns:
        Formatted string of all documents
    """
    return "\n\n".join([doc.page_content for doc in docs])
