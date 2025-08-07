from .bradley import parse_bradley_invoice
from .nan import parse_nan_invoice
from .zeiglers import parse_zeiglers_invoice
from .pet_food_experts import parse_pfe_invoice
from .phillips import parse_phillips_invoice

from .vendor_detection import detect_vendor

def parse_invoice(vendor: str, text: str):
    if vendor == "Bradley Caldwell Inc.":
        return parse_bradley_invoice(text)
    elif vendor == "NAN":
        return parse_nan_invoice(text)
    elif vendor == "Zeigler's Distributor, Inc.":
        return parse_zeiglers_invoice(text)
    elif vendor == "Pet Food Experts":
        return parse_pfe_invoice(text)
    elif vendor == "Phillips Pet Food & Supplies":
        return parse_phillips_invoice(text)
    else:
        raise ValueError(f"No parser available for vendor: {vendor}")
