import pytesseract
from PIL import Image
import cv2
import numpy as np
from utils.ocr_utils import extract_images_from_pdf

VENDOR_LOGOS = {
    "Pet Food Experts": "logos/PFX-LOGO.png",
    "Phillips Pet Food & Supplies": "logos/phillips-logo.png",
    "Zeigler's Distributor, Inc.": "logos/zeiglers-logo.png",
    "Bradley Caldwell Inc.": "logos/BRADLEY-LOGO.png"
}

NAN_IDENTIFIER_TEXT = "NAN\n151 BATA BLVD\nSUITE C\nBELCAMP, MD 21017"

def load_logo_gray(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    return cv2.Canny(img, 50, 200) if img is not None else None

def detect_vendor_from_logo(image):
    image_gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(image_gray, 50, 200)
    for vendor, logo_path in VENDOR_LOGOS.items():
        logo = load_logo_gray(logo_path)
        if logo is None:
            continue
        res = cv2.matchTemplate(edges, logo, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        if max_val > 0.55:
            return vendor
    return None

def detect_vendor_from_text(text):
    if NAN_IDENTIFIER_TEXT in text:
        return "NAN"
    for vendor in VENDOR_LOGOS:
        if vendor.lower() in text.lower():
            return vendor
    return None

def detect_vendor(pdf_path, file_name=""):
    images = extract_images_from_pdf(pdf_path)
    if images:
        vendor = detect_vendor_from_logo(images[0])
        if vendor:
            return vendor
        text = pytesseract.image_to_string(images[0])
        vendor = detect_vendor_from_text(text)
        if vendor:
            return vendor
    # Fallback: filename keywords
    lower = file_name.lower()
    for vendor in VENDOR_LOGOS:
        if vendor.split()[0].lower() in lower:
            return vendor
    return "UNKNOWN"
