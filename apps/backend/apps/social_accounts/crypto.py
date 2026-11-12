from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


def _fernet():
    key = getattr(settings, "TOKEN_ENCRYPTION_KEY", "")
    if not key:
        raise ValueError("TOKEN_ENCRYPTION_KEY is required to store social tokens.")
    try:
        return Fernet(key.encode("ascii"))
    except (ValueError, UnicodeEncodeError) as exc:
        raise ValueError("TOKEN_ENCRYPTION_KEY must be a Fernet URL-safe base64 key.") from exc


def encrypt_token(token):
    if not token:
        raise ValueError("Cannot encrypt an empty access token.")
    return _fernet().encrypt(token.encode("utf-8")).decode("ascii")


def decrypt_token(ciphertext):
    try:
        return _fernet().decrypt(ciphertext.encode("ascii")).decode("utf-8")
    except InvalidToken as exc:
        raise ValueError("Stored social token cannot be decrypted with the configured key.") from exc
