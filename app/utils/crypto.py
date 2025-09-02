import hashlib
import os
from app.config import LOG_SALT

def safe_hash(value: str) -> str:
    """
    Hashes the value using SHA256 and a salt from LOG_SALT env.
    Returns a 64-char hex string.
    """
    salt = LOG_SALT or ""
    to_hash = (salt + value).encode("utf-8")
    return hashlib.sha256(to_hash).hexdigest()