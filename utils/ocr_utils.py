import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
import fitz  # PyMuPDF
from PIL import Image
import io

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



def extract_images_from_pdf(pdf_path):
    """
    Extracts images from the first page of a PDF using PyMuPDF (fitz).
    Returns a list of PIL Image objects.
    """
    images = []
    with fitz.open(pdf_path) as doc:
        if doc.page_count == 0:
            return images
        page = doc.load_page(0)
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            images.append(image)
    return images
