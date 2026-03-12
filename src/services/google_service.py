import gspread
from gspread.utils import ValueInputOption

from src.constants.constants import (
    COLUMN_DATE_INDEX,
    COLUMN_PRICE_INDEX,
    COLUMN_CATEGORY_INDEX,
    COLUMN_NAME_INDEX,
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
    sheet.append_row(row, value_input_option=ValueInputOption.user_entered)


def get_monthly_resume(user_config: dict, user_id: str, month: int) -> tuple[str, str]:
    sheet = _get_sheet(user_config, user_id)
    rows = sheet.get_all_values()[1:]

    monthly_rows = _filter_rows_by_month(rows, month)

    total_spent = _sum_prices(monthly_rows)

    grouped = _group_rows_by_category(monthly_rows)

    category_totals = _sum_category_totals(grouped)
    category_top_items = _get_top_items_per_category(grouped, 3)

    categories_prices = _format_category_prices(category_totals)
    categories_percentages = _format_category_percentages(category_totals, total_spent)

    top_items_answer = _format_top_items(category_top_items)

    return _build_monthly_answer(
        total_spent, categories_prices, categories_percentages, top_items_answer
    )


def _filter_rows_by_month(rows: list[list[str]], month: int) -> list[list[str]]:
    today = datetime.now()
    month = month or today.month

    result = []

    for row in rows:
        try:
            buy_date = datetime.strptime(row[COLUMN_DATE_INDEX], "%d/%m/%Y %H:%M:%S")
        except ValueError as e:
            logger.error("Erro ao realizar parse da data: %s", e)
            continue

        if buy_date.month == month and buy_date.year == today.year:
            result.append(row)

    return result


def _group_rows_by_category(
    rows: list[list[str]],
) -> dict[str, list[tuple[str, float]]]:
    grouped = {}

    for row in rows:
        category = row[COLUMN_CATEGORY_INDEX]
        name = row[COLUMN_NAME_INDEX]
        price = str_to_float(row[COLUMN_PRICE_INDEX])

        grouped.setdefault(category, []).append((name, price))

    return grouped


def _sum_prices(rows: list[list[str]]) -> float:
    return sum(str_to_float(row[COLUMN_PRICE_INDEX]) for row in rows)


def _sum_category_totals(
    grouped: dict[str, list[tuple[str, float]]],
) -> dict[str, float]:
    totals = {
        category: sum(price for _, price in items)
        for category, items in grouped.items()
    }

    return dict(sorted(totals.items(), key=lambda item: item[1], reverse=True))


def _get_top_items_per_category(
    grouped: dict[str, list[tuple[str, float]]], limit: int
) -> dict[str, list[tuple[str, float]]]:

    result = {}

    for category, items in grouped.items():
        result[category] = sorted(items, key=lambda item: item[1], reverse=True)[:limit]

    return result


def _format_category_prices(category_totals: dict[str, float]) -> str:
    lines = []

    for category, total in category_totals.items():
        lines.append(f" •  <b>{category}</b>: {float_to_real_str(total)}")

    return "\n".join(lines)


def _format_category_percentages(
    category_totals: dict[str, float], total_spent: float
) -> str:
    lines = []

    for category, total in category_totals.items():
        percent = (total / total_spent) * 100 if total_spent else 0

        lines.append(f" •  <b>{category}</b>: {percent:.1f}%")

    return "\n".join(lines)


def _format_top_items(
    category_items: dict[str, list[tuple[str, float]]],
) -> str:

    lines = []

    for category, items in category_items.items():
        lines.append(f"\n<b>{category}</b>")

        for name, price in items:
            lines.append(f" •  {name}: {float_to_real_str(price)}")

    return "\n".join(lines)


def _build_monthly_answer(
    total_spent: float,
    categories_prices: str,
    categories_percentages: str,
    top_items: str,
) -> tuple[str, str]:

    return (
        _build_monthly_answer_general(
            total_spent, categories_prices, categories_percentages
        ),
        _build_monthly_answer_top_prices(top_items),
    )


def _build_monthly_answer_general(
    total_spent: float, categories_prices: str, categories_percentages: str
):
    return f"""
<b>Resumo do mês</b>
Total de gastos: {float_to_real_str(total_spent)}

<b>Gastos por categoria</b>
{categories_prices}

<b>Porcentagens por categoria</b>
{categories_percentages}
""".strip()


def _build_monthly_answer_top_prices(top_items: str):
    return f"""
<b>Maiores compras por categoria</b>
{top_items}
""".strip()


def float_to_real_str(num: float) -> str:
    return f"R$ {num:.2f}".replace(".", ",")


def str_to_float(data: str) -> float:
    return float(data.replace("R$", "").replace(",", ".").strip())
