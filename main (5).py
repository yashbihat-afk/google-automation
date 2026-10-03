import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv
from googleapiclient.discovery import build
from langchain.chat_models import init_chat_model

# ---------- Config ----------
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

GOOGLE_SPREADSHEET_API_KEY = os.getenv("GOOGLE_SPREADSHEET_API_KEY")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

LAST_ROW_FILE = BASE_DIR / "last_row.txt"


def check_env():
    """Stop early with a clear message if any env variable is missing."""
    required = {
        "GOOGLE_SPREADSHEET_API_KEY": GOOGLE_SPREADSHEET_API_KEY,
        "SPREADSHEET_ID": SPREADSHEET_ID,
        "SHEET_NAME": SHEET_NAME,
        "GEMINI_API_KEY": GEMINI_API_KEY,
        "SENDER_EMAIL": SENDER_EMAIL,
        "SENDER_PASSWORD": SENDER_PASSWORD,
        "RECIPIENT_EMAIL": RECIPIENT_EMAIL,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise SystemExit(
            f"Missing values in {BASE_DIR / '.env'}: {', '.join(missing)}"
        )


def read_last_row():
    """Number of rows already processed. Defaults to 1 (skips the header)."""
    if not LAST_ROW_FILE.exists():
        return 1
    try:
        return int(LAST_ROW_FILE.read_text().strip())
    except ValueError:
        return 1


def get_spreadsheet_data():
    """Fetch spreadsheet data and work out which rows are new."""
    service = build("sheets", "v4", developerKey=GOOGLE_SPREADSHEET_API_KEY)
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=SPREADSHEET_ID, range=SHEET_NAME)
        .execute()
    )
    all_rows = result.get("values", [])
    if not all_rows:
        return [], [], []

    headers = all_rows[0]
    last_row = read_last_row()
    new_rows = all_rows[last_row:]
    return all_rows, new_rows, headers


def summarize_with_ai(text):
    system_prompt = (
        "You are a helpful assistant that summarizes spreadsheet data. "
        "You will receive new rows that were added to a Google Spreadsheet. "
        "Please provide a clear, concise summary of this data."
    )
    model = init_chat_model(
    "gemini-3.5-flash",
    api_key=GEMINI_API_KEY,
    model_provider="google_genai",
)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Here are the new rows from the spreadsheet:\n{text}"},
    ]
    return model.invoke(messages).content

def main():
    check_env()

    all_rows, new_rows, headers = get_spreadsheet_data()
    if not all_rows:
        print("The sheet is empty. Nothing to do.")
        return

    if not new_rows:
        print("No new rows since the last run. Nothing to send.")
        return

    message = f"Headers: {headers}\nNew rows: {new_rows}"
    print(message)

    summary = summarize_with_ai(message)
    body = f"Here is today's summary\n\n{summary}\n\nThanks!"
    send_email("Daily Spreadsheet Summary", body)

    # Save progress only after the email went out successfully
    LAST_ROW_FILE.write_text(str(len(all_rows)))

    print("NEW ROWS:", new_rows)
    print("SUMMARY:", summary)
def send_email(subject, body):
    """Send email with the summary."""
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    server.send_message(msg)
    server.quit()
    print(f"Email sent successfully to {RECIPIENT_EMAIL}")

if __name__ == "__main__":
    main()
    send_email("Daily Spreadsheet Summary", "This is a test email to confirm that the email sending functionality works correctly.")