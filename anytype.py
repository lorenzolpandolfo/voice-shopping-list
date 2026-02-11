import os

import requests
import json
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("ANYTYPE_API_KEY")
BASE_URL = "http://localhost:31009/v1"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def create_anytype_object(obj_data: dict):
    data = {
        "name": obj_data.get("name") if obj_data.get("name") is not None else "Item",
        "icon": {
            "emoji": "📄",
            "format": "emoji"
        },
        "type_key": "tabela",
        "properties": [
            {
                "key": "descricao",
                "text": obj_data["description"],
            },
            {
                "key": "valor",
                "number": obj_data["price"]
            },
            {
                "key": "data",
                "date": obj_data["date"]
            },
        ]
    }
    try:
        resp = requests.post(f"{BASE_URL}/spaces/{os.getenv("SPACE_ID")}/objects", headers=headers, data=json.dumps(data))
        print(resp.text)

    except Exception as e:
        print("[ANYTYPE] Erro: ", e)
