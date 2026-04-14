import json

import requests
from google.auth.transport import requests as greq
from google.oauth2.credentials import Credentials

from src.api.utils.encrypt import encrypt, decrypt
from src.api.model.user_model import User
from src.api.repository.user_repository import UserRepository

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
START_AUTH_URL = "https://oauth2.googleapis.com/device/code"
FINISH_AUTH_URL = "https://oauth2.googleapis.com/token"


with open("client_secret.json") as f:
    data = json.load(f)["installed"]
    _client_id = data["client_id"]
    _client_secret = data["client_secret"]

_user_device_codes_to_finish = {}

user_repo = UserRepository()


def start_device_auth(user_id: str) -> tuple[str, str]:
    payload = {"client_id": _client_id, "scope": " ".join(SCOPES)}
    r = requests.post(START_AUTH_URL, data=payload)
    r.raise_for_status()
    response = r.json()

    # salvar dados do token que precisa ser finalizado
    _user_device_codes_to_finish[user_id] = response

    return response["user_code"], response["verification_url"]


def finish_device_auth(user_id: str) -> Credentials | None:
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

    user = user_repo.find_by_id(user_id)

    if not user:
        raise Exception("Usuário não autorizado para cadastro")

    __update_user_token(user, creds)

    return creds


def get_user_credentials_google(user_id: str) -> Credentials | None:
    """Retorna as credenciais do Google do usuário. Se estiverem expiradas, renova."""

    user: User | None = user_repo.find_by_id(user_id)

    if user is None or not user.token:
        return None

    user_token = decrypt(user.token)

    creds: Credentials = Credentials.from_authorized_user_info(
        json.loads(user_token), SCOPES
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(greq.Request())

        __update_user_token(user, creds)

    return creds


def __update_user_token(user: User, token: Credentials) -> User:
    user.token = encrypt(token.to_json())
    user_repo.update(user)
    return user
