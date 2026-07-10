import base64
import hashlib
import os

from cryptography.fernet import Fernet
from django.conf import settings


def _fernet_key() -> bytes:
    raw = os.getenv('FIELD_ENCRYPTION_KEY', settings.SECRET_KEY)
    digest = hashlib.sha256(raw.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_value(plain: str) -> str:
    if not plain:
        return ''
    return Fernet(_fernet_key()).encrypt(plain.encode()).decode()


def decrypt_value(token: str) -> str:
    if not token:
        return ''
    return Fernet(_fernet_key()).decrypt(token.encode()).decode()
