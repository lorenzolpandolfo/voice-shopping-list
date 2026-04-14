import os

from cryptography.fernet import Fernet

KEY_FILE = "key.bin"
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
    return _f.decrypt(o.encode()).decode()
