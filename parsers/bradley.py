import re
import pandas as pd

def parse_bradley_invoice(text: str) -> pd.DataFrame:
    lines = text.splitlines()
    data = []

    invoice_date = ""
    invoice_number = ""

    # Grab header info
    for line in lines:
        if "invoice date" in line.lower():
            match = re.search(r"Invoice Date:\s*([0-9/]+)", line, re.IGNORECASE)
            if match:
                invoice_date = match.group(1).strip()
        if "invoice #" in line.lower():
            match = re.search(r"Invoice #:\s*(\d+)", line, re.IGNORECASE)
            if match:
                invoice_number = match.group(1).strip()

    current_product = ""
    current_upc = ""

    for i, line in enumerate(lines):
        # Try to find a 12-digit UPC
        upc_match = re.search(r"\b\d{12}\b", line)
        if upc_match:
            current_upc = upc_match.group()

        # Try to find a product description line
        elif re.search(r"[A-Z].*[A-Z]", line) and not line.strip().isdigit():
            current_product = line.strip()

        # Try to extract qty/price rows
        qty_match = re.findall(r"\b\d+\b", line)
        price_match = re.findall(r"\d+\.\d{2}", line)

        if qty_match and price_match and len(price_match) >= 1:
            try:
                qty_ord = int(qty_match[0])
                qty_shp = int(qty_match[1]) if len(qty_match) > 1 else qty_ord
                backorder = int(qty_match[2]) if len(qty_match) > 2 else max(qty_ord - qty_shp, 0)
                price = float(price_match[-1])
                total = round(price * qty_shp, 2)

                data.append({
                    "Invoice Date": invoice_date,
                    "Invoice #": invoice_number,
                    "Product": current_product,
                    "UPC": current_upc,
                    "Qty Ordered": qty_ord,
                    "Qty Shipped": qty_shp,
                    "Backordered": backorder,
                    "Unit Price": price,
                    "Total": total,
                    "Flag": "✅" if qty_ord != qty_shp or backorder > 0 else ""
                })

            except Exception:
                continue

    return pd.DataFrame(data)
