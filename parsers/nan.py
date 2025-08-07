import re
import pandas as pd

def parse_nan_invoice(text: str) -> pd.DataFrame:
    lines = text.splitlines()
    data = []

    invoice_date = ""
    invoice_number = ""

    # Grab Sales Order # as invoice #
    for line in lines:
        if "sales order" in line.lower():
            match = re.search(r"Sales Order #:\s*(\d+)", line, re.IGNORECASE)
            if match:
                invoice_number = match.group(1).strip()
        if "date ordered" in line.lower():
            match = re.search(r"Date Ordered\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})", line)
            if match:
                invoice_date = match.group(1).strip()

    current_product = ""
    current_upc = ""
    current_qty = ""

    for i, line in enumerate(lines):
        # UPC is on its own line with 12+ digits
        if re.match(r"^\s*\d{12,13}\s*$", line.strip()):
            current_upc = line.strip()
        # Line above UPC is product name
        elif current_upc and current_product:
            data.append({
                "Invoice Date": invoice_date,
                "Invoice #": invoice_number,
                "Product": current_product,
                "UPC": current_upc,
                "Qty Ordered": current_qty,
                "Qty Shipped": current_qty,
                "Backordered": 0 if current_qty != "0" else 1,
                "Unit Price": "",
                "Total": "",
                "Flag": "✅" if current_qty == "0" else ""
            })
            current_product = ""
            current_upc = ""
            current_qty = ""
        # Product name (first line of a block)
        elif re.search(r"[A-Z].*[A-Z]", line) and not line.strip().isdigit():
            current_product = line.strip()
        # Quantity line
        elif re.match(r".*Qty In Carton.*", line):
            qty_match = re.search(r"Qty In Carton.*?(\d+)", line)
            if qty_match:
                current_qty = qty_match.group(1)

    return pd.DataFrame(data)
