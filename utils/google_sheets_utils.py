import os
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDS = service_account.Credentials.from_service_account_file("credentials.json", scopes=SCOPES)

def log_invoice_to_sheets(vendor, df: pd.DataFrame):
    service = build("sheets", "v4", credentials=CREDS)
    sheet = service.spreadsheets()

    # Convert DataFrame to list of lists
    values = [df.columns.tolist()] + df.values.tolist()

    # Create new tab if it doesn't exist
    try:
        sheet_metadata = sheet.get(spreadsheetId=SHEET_ID).execute()
        sheet_titles = [s['properties']['title'] for s in sheet_metadata['sheets']]
        if vendor not in sheet_titles:
            sheet.batchUpdate(spreadsheetId=SHEET_ID, body={
                "requests": [{"addSheet": {"properties": {"title": vendor}}}]
            }).execute()
    except Exception as e:
        print(f"Error checking/creating sheet tab: {e}")
        return

    # Append data
    range_name = f"{vendor}!A1"
    body = {
        "values": values
    }

    sheet.values().append(
        spreadsheetId=SHEET_ID,
        range=range_name,
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()
