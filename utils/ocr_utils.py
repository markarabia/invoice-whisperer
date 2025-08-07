import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path):
    """Try to extract text directly; if that fails, use OCR."""
    try:
        text = ""
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t
        if text.strip():
            return text
        else:
            raise ValueError("No text found, switching to OCR.")
    except Exception:
        pass

    # Fallback to OCR
    images = convert_from_path(pdf_path)
    ocr_text = ""
    for image in images:
        ocr_text += pytesseract.image_to_string(image)
    return ocr_text
