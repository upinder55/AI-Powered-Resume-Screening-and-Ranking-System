"""
parser.py
Extracts clean, normalized text from various resume formats (PDF, DOCX, TXT).
Handles errors gracefully with multiple fallback strategies.
"""

import os
import re
import zipfile
import xml.etree.ElementTree as ET

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF using pypdf with fallback."""
    text = ""
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        # Fallback raw byte extraction if pypdf has an issue
        try:
            with open(file_path, 'rb') as f:
                content = f.read().decode('latin-1', errors='ignore')
                # Extract text within parentheses in PDF streams (common in simple PDFs)
                matches = re.findall(r'\((.*?)\)\s*Tj', content)
                if matches:
                    text = " ".join(matches)
        except Exception:
            pass

    return clean_text(text)

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX using python-docx with XML fallback."""
    text = ""
    try:
        import docx
        doc = docx.Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        # Also extract text inside tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        paragraphs.append(cell.text.strip())
        text = "\n".join(paragraphs)
    except Exception:
        # Fallback: DOCX is a zip file containing word/document.xml
        try:
            with zipfile.ZipFile(file_path) as z:
                xml_content = z.read('word/document.xml')
                tree = ET.fromstring(xml_content)
                namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                texts = [node.text for node in tree.iterfind('.//w:t', namespaces) if node.text]
                text = " ".join(texts)
        except Exception:
            pass

    return clean_text(text)

def extract_text_from_txt(file_path: str) -> str:
    """Extract text from a plain text file trying multiple encodings."""
    for enc in ['utf-8', 'latin-1', 'cp1252', 'utf-16']:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                return clean_text(f.read())
        except UnicodeDecodeError:
            continue
        except Exception:
            break
    return ""

def clean_text(text: str) -> str:
    """Clean and normalize extracted resume text."""
    if not text:
        return ""
    # Replace weird unicode bullets and symbols with clean spaces/characters
    text = re.sub(r'[\u2022\u2023\u25E6\u2043\u2219\u00B7\u25CF\u25CB\u25AA\u25BA]', ' ', text)
    # Replace non-breaking spaces
    text = text.replace('\xa0', ' ')
    # Normalize multiple whitespace characters
    text = re.sub(r'[ \t]+', ' ', text)
    # Limit consecutive newlines
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    return text.strip()

def parse_resume(file_path: str) -> dict:
    """
    Given a file path, identify format and return parsed text and status.
    """
    if not os.path.exists(file_path):
        return {"success": False, "error": f"File not found: {file_path}", "text": ""}

    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    try:
        if ext == '.pdf':
            text = extract_text_from_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            text = extract_text_from_docx(file_path)
        elif ext in ['.txt', '.rtf']:
            text = extract_text_from_txt(file_path)
        else:
            return {"success": False, "error": f"Unsupported file format: {ext}", "text": ""}
        
        if not text or len(text.strip()) < 30:
            return {
                "success": False, 
                "error": "Extracted text is empty or too short. File might be an image-only scanned document.",
                "text": text
            }
            
        return {"success": True, "error": None, "text": text}
    except Exception as e:
        return {"success": False, "error": str(e), "text": ""}
