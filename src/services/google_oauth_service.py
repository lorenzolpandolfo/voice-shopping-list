import os
import json

import requests
from google.auth.transport import requests as greq
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
START_AUTH_URL = "https://oauth2.googleapis.com/device/code"
FINISH_AUTH_URL = "https://oauth2.googleapis.com/token"
TOKEN_DIR = "user_tokens"


os.makedirs(TOKEN_DIR, exist_ok=True)

with open("client_secret.json") as f:
    data = json.load(f)["installed"]
    _client_id = data["client_id"]
    _client_secret = data["client_secret"]

_user_device_codes_to_finish = {}


def start_device_auth(user_id: str) -> tuple[str, str]:
    payload = {"client_id": _client_id, "scope": " ".join(SCOPES)}
    r = requests.post(START_AUTH_URL, data=payload)
    r.raise_for_status()
    response = r.json()

    # salvar dados do token que precisa ser finalizado
    _user_device_codes_to_finish[user_id] = response

    return response["user_code"], response["verification_url"]


def finish_device_auth(user_id: str):
    """Finaliza o processo de autenticação de um token salvo em _user_device_codes."""

    token_to_finish_data = _user_device_codes_to_finish.get(user_id)
    if not token_to_finish_data:
        return None

    payload = {
        "client_id": _client_id,
        "client_secret": _client_secret,
        "device_code": token_to_finish_data["device_code"],
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
    }

    r = requests.post(FINISH_AUTH_URL, data=payload)
    response = r.json()

    if "error" in response:
        if response["error"] == "authorization_pending":
            raise Exception("Usuário ainda não concluiu a autorização.")
        else:
            raise Exception(f"Erro OAuth: {response['error']}")

    creds = Credentials(
        token=response["access_token"],
        refresh_token=response.get("refresh_token"),
        token_uri=FINISH_AUTH_URL,
        client_id=_client_id,
        client_secret=_client_secret,
        scopes=SCOPES,
    )

    token_path = os.path.join(TOKEN_DIR, f"{user_id}.json")
    with open(token_path, "w") as f:
        f.write(creds.to_json())

    return creds


def get_user_credentials(user_id: str) -> Credentials | None:
    """Retorna as credenciais do Google do usuário. Se estiverem expiradas, renova."""

    token_path = os.path.join(TOKEN_DIR, f"{user_id}.json")

    if not os.path.exists(token_path):
        return None

    creds: Credentials = Credentials.from_authorized_user_file(token_path, SCOPES)

    if creds.expired and creds.refresh_token:
        creds.refresh(greq.Request())
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    return creds
