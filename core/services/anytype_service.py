import os

import requests
import json

from dotenv import load_dotenv

from core.exceptions.anytype_exception import AnytypeException

load_dotenv()

SPACE_ID = os.getenv("ANYTYPE_SPACE_ID")

HOST = os.getenv("ANYTYPE_HOST")
PORT = os.getenv("ANYTYPE_PORT")
BASE_URL = f"http://{HOST}:{PORT}/v1"

TOKEN = os.getenv("ANYTYPE_API_KEY")
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def create_error_message(obj_data: dict) -> str:
    return f"[ANYTYPE ERROR] Erro ao enviar compra:\n > {obj_data}\n"

def create_anytype_object(obj_data: dict):
    err_msg = create_error_message(obj_data)

    data = {
        "name": obj_data.get("name") if obj_data.get("name") is not None else "Item",
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
            {
                "key": "categoria",
                "date": obj_data["category"]
            },
        ]
    }
    print(f"[ANYTYPE] Salvando dados do objeto:\n > {obj_data}\n")
    response = requests.post(f"{BASE_URL}/spaces/{SPACE_ID}/objects", headers=headers, data=json.dumps(data))

    if int(response.status_code) != 201:
        raise AnytypeException(err_msg)
