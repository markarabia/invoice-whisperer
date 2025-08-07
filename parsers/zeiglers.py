import re
import pandas as pd

def parse_zeiglers_invoice(text: str) -> pd.DataFrame:
    lines = text.splitlines()
    data = []

    invoice_date = ""
    invoice_number = ""

    for line in lines:
        if "invoice date" in line.lower():
            match = re.search(r"Invoice Date\s+([0-9/]+)", line, re.IGNORECASE)
            if match:
                invoice_date = match.group(1).strip()
        if "order number" in line.lower():
            match = re.search(r"ORDER NUMBER\s+(\d+)", line, re.IGNORECASE)
            if match:
                invoice_number = match.group(1).strip()

    for line in lines:
        # Match Zeigler's standard line item format:
        # 6 6 0 EA 840199680009 205700 14oz Vital Freeze Dried Beef Nibs Dog 15.89 95.34
        match = re.match(
            r"^\s*(\d+)\s+(\d+)\s+(\d+)\s+\w+\s+(\d{12,13})\s+\d+\s+(.+?)\s+(\d+\.\d{2})\s+(\d+\.\d{2})",
            line
        )
        if match:
            qty_ordered = int(match.group(1))
            qty_shipped = int(match.group(2))
            backorder = int(match.group(3))
            upc = match.group(4)
            description = match.group(5).strip()
            unit_price = float(match.group(6))
            total = float(match.group(7))

            data.append({
                "Invoice Date": invoice_date,
                "Invoice #": invoice_number,
                "Product": description,
                "UPC": upc,
                "Qty Ordered": qty_ordered,
                "Qty Shipped": qty_shipped,
                "Backordered": backorder,
                "Unit Price": unit_price,
                "Total": total,
                "Flag": "✅" if backorder > 0 or qty_ordered != qty_shipped else ""
            })

    return pd.DataFrame(data)
