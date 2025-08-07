import streamlit as st
from utils.ocr_utils import extract_text_from_pdf
from utils.google_drive_utils import upload_to_drive
from utils.google_sheets_utils import log_invoice_to_sheets
from parsers import detect_vendor, parse_invoice

from pathlib import Path
import tempfile
import os

st.set_page_config(page_title="Invoice Whisperer™", layout="wide")

st.title("🧾 Invoice Whisperer™")
st.caption("Upload a scanned or PDF invoice. We'll extract, analyze, and log it like magic ✨")

uploaded_file = st.file_uploader("📤 Upload Invoice PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("Processing invoice..."):

        # Save uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        # Extract text
        text = extract_text_from_pdf(tmp_path)

        # Detect vendor from text or filename
        vendor = detect_vendor(text, uploaded_file.name)
        if not vendor:
            st.error("❌ Could not detect vendor. Please check the file or rename it to include the vendor.")
        else:
            st.success(f"📦 Vendor detected: {vendor}")

            # Parse invoice using the vendor-specific parser
            try:
                invoice_data = parse_invoice(vendor, text)
                st.write("✅ Parsed Invoice Data:")
                st.dataframe(invoice_data)

                # Upload PDF to Google Drive
                upload_to_drive(vendor, tmp_path)

                # Log to Google Sheets
                log_invoice_to_sheets(vendor, invoice_data)

                st.success("📤 Uploaded to Google Drive and logged to Google Sheets!")

            except Exception as e:
                st.error(f"❌ Error during parsing: {e}")

        os.unlink(tmp_path)
