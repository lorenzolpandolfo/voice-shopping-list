import json
import os
from typing import Any

from cryptography.fernet import Fernet, InvalidToken

KEY_FILE = "key.bin"
CLIENT_SECRET_FILE = "client_secret.json"
READONLY_PERMISSION = 0o600

if not os.path.exists(KEY_FILE):
    with open("key.bin", "wb") as f:
        f.write(Fernet.generate_key())

    os.chmod(KEY_FILE, READONLY_PERMISSION)

with open("key.bin", "rb") as f:
    _key = f.read()

_f = Fernet(_key)


def encrypt(o: str) -> str:
    return _f.encrypt(o.encode()).decode()


def decrypt(o: str) -> str:
    try:
        return _f.decrypt(o.encode()).decode()

    except InvalidToken:
        return o


def load_client_secret() -> tuple[Any, Any]:
    """Encrypt client_secret.json if it is not encrypted, and return its data."""
    with open(CLIENT_SECRET_FILE, "r") as f:
        raw = f.read()

    try:
        decrypted = decrypt(raw)
        content = decrypted
    except Exception:
        encrypted = encrypt(raw)
        with open(CLIENT_SECRET_FILE, "w") as f:
            f.write(encrypted)
        content = raw

    data = json.loads(content)["installed"]

    return data["client_id"], data["client_secret"]
