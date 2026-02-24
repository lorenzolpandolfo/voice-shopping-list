import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

_client_cache = {}


def get_client(user_id: str, service_account_path: str):
    if user_id not in _client_cache:
        creds = Credentials.from_service_account_file(
            service_account_path,
            scopes=SCOPES,
        )
        _client_cache[user_id] = gspread.authorize(creds)

    return _client_cache[user_id]


def save_data_to_spreadsheet(payload: dict, user_id: str, user_config: dict):
    spreadsheet_id = user_config["spreadsheet_id"]
    spreadsheet_tab = user_config["spreadsheet_tab"]
    service_account_path = user_config["service_account_path"]

    client = get_client(user_id, service_account_path)

    sheet = client.open_by_key(spreadsheet_id).worksheet(spreadsheet_tab)

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
