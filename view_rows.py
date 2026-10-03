import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv


load_dotenv()

SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME")


def get_spreadsheet_data():
    """Fetch spreadsheet data using service account"""
    # Define the scopes
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    # Authenticate using service account
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )

    # Build the service with credentials
    service = build('sheets', 'v4', credentials=credentials)

    all_rows = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=SHEET_NAME
    ).execute()['values']

    headers = all_rows[0]
    return all_rows, headers


all_rows, headers = get_spreadsheet_data()
print(all_rows)


