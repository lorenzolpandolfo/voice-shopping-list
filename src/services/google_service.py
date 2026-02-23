import os
from datetime import datetime

import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

load_dotenv()

GOOGLE_SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID")
GOOGLE_SPREADSHEET_TAB = os.getenv("GOOGLE_SPREADSHEET_TAB")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPES)

gc = gspread.authorize(creds)
sheet = gc.open_by_key(GOOGLE_SPREADSHEET_ID).worksheet(GOOGLE_SPREADSHEET_TAB)


def save_data_to_spreadsheet(payload):
    raw_date = payload["date"]
    dt = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
    formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S")

    row = [
        payload["name"],
        payload["price"],
        payload["description"],
        payload["category"],
        formatted_date,
    ]
    sheet.append_row(row, value_input_option="USER_ENTERED")


if GOOGLE_SPREADSHEET_ID is None or GOOGLE_SPREADSHEET_TAB is None:
    raise EnvironmentError(
        "Google spreadsheet is not configured. Add to .env the values: GOOGLE_SPREADSHEET_ID and GOOGLE_SPREADSHEET_TAB."
    )
