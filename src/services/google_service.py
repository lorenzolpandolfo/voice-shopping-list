import gspread

from src.constants.constants import (
    COLUMN_DATE_INDEX,
    COLUMN_PRICE_INDEX,
    MONTHLY_ANSWER_MASK,
    MASK_TOTAL_SPENT,
    MASK_CATEGORIES_PRICES,
    COLUMN_CATEGORY_INDEX,
)
from src.services.google_oauth_service import get_user_credentials_google
from datetime import datetime
from logging import getLogger

_client_cache = {}
logger = getLogger(__name__)


def _get_client(user_id: str):
    """Retorna o client do user_id se existir no cache. Senão, consulta a credencial e salva no cache."""

    if user_id in _client_cache:
        return _client_cache[user_id]

    creds = get_user_credentials_google(user_id)
    if not creds:
        raise Exception("Usuário não autenticado. Use /auth primeiro.")

    client = gspread.authorize(creds)
    _client_cache[user_id] = client
    return client


def _get_sheet(user_config: dict, user_id: str):
    spreadsheet_id = user_config["spreadsheet_id"]
    spreadsheet_tab = user_config["spreadsheet_tab"]

    client = _get_client(user_id)
    return client.open_by_key(spreadsheet_id).worksheet(spreadsheet_tab)


def save_data_to_spreadsheet(payload: dict, user_id: str, user_config: dict):
    """Recebe um payload, user_id e user_config. Salva o payload conforme os dados do usuário."""

    sheet = _get_sheet(user_config, user_id)

    date = payload["date"]
    dt = datetime.fromisoformat(date)
    formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S")

    row = [
        payload["name"],
        payload["price"],
        payload["description"],
        payload["category"],
        formatted_date,
    ]
    sheet.append_row(row, value_input_option="USER_ENTERED")


def get_monthly_resume(user_config: dict, user_id: str, month: int):
    sheet = _get_sheet(user_config, user_id)
    all_table_data = sheet.get_all_values()[1:]

    monthly_resume = _get_monthly_rows(all_table_data, month)

    total_spent = sum(str_to_float(row[COLUMN_PRICE_INDEX]) for row in monthly_resume)
    category_totals = _sum_by_category(monthly_resume)
    categories_prices_answer = _categories_prices_to_str(category_totals)

    return to_monthly_answer(total_spent, categories_prices_answer)


def _get_monthly_rows(all_table_data: list[list[str]], month: int) -> list[list[str]]:
    monthly_resume = []

    today = datetime.now()
    month = month if month else today.month

    for row in all_table_data:
        buy_date = row[COLUMN_DATE_INDEX]

        try:
            buy_date = datetime.strptime(buy_date, "%d/%m/%Y %H:%M:%S")

        except ValueError as e:
            logger.error("Erro ao realizar parse da data: ", e)
            continue

        if buy_date.month != month or buy_date.year != today.year:
            continue

        monthly_resume.append(row)

    return monthly_resume


def _sum_by_category(rows):
    totals = {}

    for row in rows:
        category = row[COLUMN_CATEGORY_INDEX]
        price = str_to_float(row[COLUMN_PRICE_INDEX])

        totals[category] = totals.get(category, 0.0) + price

    return dict(
        sorted(totals.items(), key=lambda item: item[COLUMN_PRICE_INDEX], reverse=True)
    )


def _categories_prices_to_str(categories_prices: dict) -> str:
    answer = ""

    for category, price in categories_prices.items():
        answer += f" •  <b>{category}</b>: {float_to_real_str(price)}\n"

    return answer


def to_monthly_answer(total_spent: float, categories_prices: str) -> str:
    return MONTHLY_ANSWER_MASK.replace(
        MASK_TOTAL_SPENT, float_to_real_str(total_spent)
    ).replace(MASK_CATEGORIES_PRICES, categories_prices)


def float_to_real_str(num: float) -> str:
    return f"R$ {num:.2f}".replace(".", ",")


def str_to_float(data: str) -> float:
    return float(data.replace("R$", "").replace(",", ".").strip())
