"""Append a row to the configured Google Sheet.

Configuration is loaded from the .env file beside this script. The spreadsheet
must be shared with the service account whose key is in SERVICE_ACCOUNT_FILE.

Example:
    python automation.py --values "2026-09-30" "Example task" "Done"
    python automation.py --range "Sheet1!A:C" --values "value 1" "value 2"
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.auth.exceptions import GoogleAuthError
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

SHEETS_SCOPE = "https://www.googleapis.com/auth/spreadsheets"


def get_service_account_credentials():
    """Load the service-account key configured in .env."""
    key_path_value = os.getenv("SERVICE_ACCOUNT_FILE")
    if not key_path_value:
        raise ValueError("SERVICE_ACCOUNT_FILE is missing from the .env file.")

    key_path = Path(key_path_value).expanduser()
    if not key_path.is_absolute():
        key_path = BASE_DIR / key_path
    if not key_path.is_file():
        raise FileNotFoundError(f"Service-account key file not found: {key_path}")

    return service_account.Credentials.from_service_account_file(
        str(key_path), scopes=[SHEETS_SCOPE]
    )


def append_row(spreadsheet_id: str, cell_range: str, values: list[str]) -> int:
    """Append one row and return the number of rows written."""
    service = build(
        "sheets", "v4", credentials=get_service_account_credentials()
    )
    result = (
        service.spreadsheets()
        .values()
        .append(
            spreadsheetId=spreadsheet_id,
            range=cell_range,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": [values]},
        )
        .execute()
    )
    return result.get("updates", {}).get("updatedRows", 0)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--spreadsheet-id",
        default=os.getenv("SPREADSHEET_ID"),
        help="Spreadsheet ID; defaults to SPREADSHEET_ID from .env.",
    )
    parser.add_argument(
        "--range",
        dest="cell_range",
        default=os.getenv("SHEET_NAME"),
        help="A1 range; defaults to SHEET_NAME from .env (for example, 'Sheet1!A:C').",
    )
    parser.add_argument(
        "--values",
        nargs="+",
        required=True,
        help="Values for the row, in column order.",
    )
    args = parser.parse_args()

    if not args.spreadsheet_id:
        parser.error("SPREADSHEET_ID is missing from .env; or pass --spreadsheet-id.")
    if not args.cell_range:
        parser.error("SHEET_NAME is missing from .env; or pass --range.")

    try:
        rows_written = append_row(args.spreadsheet_id, args.cell_range, args.values)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except (GoogleAuthError, OSError, ValueError) as exc:
        print(f"Could not authenticate with the configured service account: {exc}", file=sys.stderr)
        return 1
    except HttpError as exc:
        status = getattr(exc.resp, "status", "unknown")
        print(f"Google Sheets API request failed (HTTP {status}): {exc.reason}", file=sys.stderr)
        print(
            "Check that the Sheets API is enabled, the range is valid, and the sheet is shared with the service account.",
            file=sys.stderr,
        )
        return 1

    print(f"Appended {rows_written} row(s) to {args.cell_range}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
