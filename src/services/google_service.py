import gspread
from src.services.google_oauth_service import get_user_credentials_google
from datetime import datetime

_client_cache = {}


def get_client(user_id: str):
    """Retorna o client do user_id se existir no cache. Senão, consulta a credencial e salva no cache."""

    if user_id in _client_cache:
        return _client_cache[user_id]

    creds = get_user_credentials_google(user_id)
    if not creds:
        raise Exception("Usuário não autenticado. Use /auth primeiro.")

    client = gspread.authorize(creds)
    _client_cache[user_id] = client
    return client


def save_data_to_spreadsheet(payload: dict, user_id: str, user_config: dict):
    """Recebe um payload, user_id e user_config. Salva o payload conforme os dados do usuário."""

    spreadsheet_id = user_config["spreadsheet_id"]
    spreadsheet_tab = user_config["spreadsheet_tab"]

    client = get_client(user_id)

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
