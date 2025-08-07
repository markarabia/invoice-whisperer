import os
import mimetypes
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

load_dotenv()

DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
CREDS = service_account.Credentials.from_service_account_file("credentials.json", scopes=SCOPES)


def upload_to_drive(vendor_name, file_path):
    service = build("drive", "v3", credentials=CREDS)

    # Check if folder exists for vendor, otherwise create
    query = f"'{DRIVE_FOLDER_ID}' in parents and name = '{vendor_name}' and mimeType = 'application/vnd.google-apps.folder'"
    results = service.files().list(q=query, spaces='drive', fields="files(id, name)").execute()
    items = results.get("files", [])
    
    if items:
        folder_id = items[0]["id"]
    else:
        file_metadata = {
            "name": vendor_name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [DRIVE_FOLDER_ID]
        }
        folder = service.files().create(body=file_metadata, fields="id").execute()
        folder_id = folder.get("id")

    # Upload file using correct media type
    file_name = os.path.basename(file_path)
    mime_type = mimetypes.guess_type(file_path)[0] or "application/pdf"
    file_metadata = {
        "name": file_name,
        "parents": [folder_id]
    }
    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

    service.files().create(body=file_metadata, media_body=media, fields="id").execute()

