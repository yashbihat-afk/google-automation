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
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

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


def add_row_to_spreadsheet(row_data):
    """Add a new row to the spreadsheet

    Args:
        row_data (list): List of values to add as a new row
    """
    # Define the scopes (needs write permission)
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    # Authenticate using service account
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )

    # Build the service with credentials
    service = build('sheets', 'v4', credentials=credentials)

    # Prepare the data
    body = {
        'values': [row_data]
    }

    # Append the row
    result = service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=SHEET_NAME,
        valueInputOption='RAW',
        body=body
    ).execute()

    return result


# Example usage
all_rows, headers = get_spreadsheet_data()
print(all_rows)

# Add a new row (example)
new_row = ["Value1", "Value2", "Value3"]
result = (add_row_to_spreadsheet(new_row))
print("Result", result)