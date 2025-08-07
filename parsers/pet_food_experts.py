import re
import pandas as pd

def parse_pfe_invoice(text: str) -> pd.DataFrame:
    lines = text.splitlines()
    data = []

    invoice_date = ""
    invoice_number = ""

    for line in lines:
        if "invoice date" in line.lower():
            match = re.search(r"Invoice Date:\s*([0-9/]+)", line, re.IGNORECASE)
            if match:
                invoice_date = match.group(1).strip()
        if "invoice number" in line.lower():
            match = re.search(r"Invoice Number:\s*(\d+)", line, re.IGNORECASE)
            if match:
                invoice_number = match.group(1).strip()

    for line in lines:
        # Look for line item pattern: UPC in middle, description, price, total, qty
        match = re.search(r"(\d{12})\s+.+?\s+(\d+)\s*/\s*(\d+)\s+([\d.]+)\s+([\d.]+)", line)
        if match:
            upc = match.group(1)
            qty_ord = int(match.group(2))
            qty_shp = int(match.group(3))
            price = float(match.group(4))
            total = float(match.group(5))

            # Try to capture the product name
            description = ""
            prev_index = lines.index(line) - 1
            if prev_index >= 0:
                description = lines[prev_index].strip()

            backordered = max(qty_ord - qty_shp, 0)

            data.append({
                "Invoice Date": invoice_date,
                "Invoice #": invoice_number,
                "Product": description,
                "UPC": upc,
                "Qty Ordered": qty_ord,
                "Qty Shipped": qty_shp,
                "Backordered": backordered,
                "Unit Price": price,
                "Total": total,
                "Flag": "✅" if qty_ord != qty_shp else ""
            })

    return pd.DataFrame(data)
