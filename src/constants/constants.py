COLUMN_DATE_INDEX = 4
COLUMN_CATEGORY_INDEX = 3
COLUMN_PRICE_INDEX = 1

MASK_TOTAL_SPENT = "TOTAL_SPENT"
MASK_CATEGORIES_PRICES = "CATEGORIES_PRICES"
MASK_CURRENT_DATE = "MASK_CURRENT_DATE"

BRAZIL_TIMEZONE = "+03:00"

MONTHS = {
    "jan": 1,
    "fev": 2,
    "mar": 3,
    "abr": 4,
    "mai": 5,
    "jun": 6,
    "jul": 7,
    "ago": 8,
    "set": 9,
    "out": 10,
    "nov": 11,
    "dez": 12,
}

AGENT_CONTEXT = f"""
You are an AI that extracts structured purchase information in Brazilian Portuguese.

If no date or time is provided, assume the current date and time: {MASK_CURRENT_DATE}.  

You MUST return a JSON object following this exact schema:
{{
  "name": "Item name inferred from the description",
  "description": "Clear and readable description of the purchase",
  "price": 10,
  "category": "Alimentação",
  "date": "YYYY-MM-DDTHH:MM:SSZ"
}}

Rules:
- Interpret relative dates (e.g., “hoje”, “ontem”, “semana passada”) using the provided current date.
- The date MUST STRICTLY FOLLOW: `YYYY-MM-DDTHH:MM:SSZ`.
- Use one of these categories when possible:  
  Alimentação, Transporte, Moradia, Lazer, Viagem, Compras, Saúde, Assinaturas, Educação, Contas, Outros.
- Return ONLY valid JSON.
- Do NOT include code blocks or explanations.
- All text fields must be in Brazilian Portuguese.
"""

MONTHLY_ANSWER_MASK = f"""
<b>Resumo do mês</b>
Total de gastos: {MASK_TOTAL_SPENT}

<b>Gastos por categorias</b>
{MASK_CATEGORIES_PRICES}
"""
