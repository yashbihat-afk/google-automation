from dotenv import load_dotenv
import os
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME")


def get_spreadsheet_data():
    """Fetch spreadsheet data"""
    service = build("sheets", "v4", developerKey=GOOGLE_API_KEY)
    results = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,range=SHEET_NAME).execute()

    return results


print(get_spreadsheet_data())