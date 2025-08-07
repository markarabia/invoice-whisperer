import re
import pandas as pd

def parse_phillips_invoice(text: str) -> pd.DataFrame:
    lines = text.splitlines()
    data = []

    invoice_date = ""
    invoice_number = ""

    for line in lines:
        if "invoice date" in line.lower():
            match = re.search(r"Invoice Date\s*([0-9/]+)", line, re.IGNORECASE)
            if match:
                invoice_date = match.group(1).strip()
        if "invoice no" in line.lower():
            match = re.search(r"Invoice No\s*([0-9]+)", line, re.IGNORECASE)
            if match:
                invoice_number = match.group(1).strip()

    # Loop through lines looking for UPCs and build context around them
    current_product = ""
    for i, line in enumerate(lines):
        # UPC line
        upc_match = re.match(r"^\s*(\d{12})\s*$", line.strip())
        if upc_match:
            upc = upc_match.group(1)

            # Try to find product description from the 1-2 lines above
            desc = ""
            for offset in range(1, 4):
                if i - offset >= 0:
                    candidate = lines[i - offset].strip()
                    if len(candidate) > 4 and any(c.isalpha() for c in candidate):
                        desc = candidate
                        break

            # Try to find quantity and price from 1-2 lines below
            qty_ord, qty_shp, price = None, None, None
            for offset in range(1, 4):
                if i + offset < len(lines):
                    next_line = lines[i + offset]
                    qty_match = re.findall(r"\b\d+\b", next_line)
                    price_match = re.findall(r"\d+\.\d{2}", next_line)
                    if qty_match and len(qty_match) >= 2:
                        qty_ord = int(qty_match[0])
                        qty_shp = int(qty_match[1])
                    if price_match:
                        price = float(price_match[-1])
                    if qty_ord and qty_shp and price:
                        break

            if qty_ord and qty_shp and price:
                total = round(price * qty_shp, 2)
                backorder = max(qty_ord - qty_shp, 0)

                data.append({
                    "Invoice Date": invoice_date,
                    "Invoice #": invoice_number,
                    "Product": desc,
                    "UPC": upc,
                    "Qty Ordered": qty_ord,
                    "Qty Shipped": qty_shp,
                    "Backordered": backorder,
                    "Unit Price": price,
                    "Total": total,
                    "Flag": "✅" if backorder > 0 or qty_ord != qty_shp else ""
                })

    return pd.DataFrame(data)
