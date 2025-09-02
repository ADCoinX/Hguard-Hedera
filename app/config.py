import os
from dotenv import load_dotenv

load_dotenv()

def get_bool(name: str, default=False) -> bool:
    """Read env var and parse as boolean."""
    val = os.getenv(name, "")
    if val == "":
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")

APP_ENV = os.getenv("APP_ENV", "production")
PORT = int(os.getenv("PORT", "8080"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_SALT = os.getenv("LOG_SALT", "")
ML_ENABLED = get_bool("ML_ENABLED", False)

PRIMARY_MIRROR_BASE = os.getenv("PRIMARY_MIRROR_BASE")
FALLBACK_MIRROR_BASE_1 = os.getenv("FALLBACK_MIRROR_BASE_1")
FALLBACK_MIRROR_BASE_2 = os.getenv("FALLBACK_MIRROR_BASE_2")
FALLBACK_MIRROR_BASE_3 = os.getenv("FALLBACK_MIRROR_BASE_3")
FALLBACK_MIRROR_BASE_4 = os.getenv("FALLBACK_MIRROR_BASE_4")

DB_URL = os.getenv("DB_URL")
USE_POSTGRES = get_bool("USE_POSTGRES", False)
RATE_LIMIT_RPS = int(os.getenv("RATE_LIMIT_RPS", "10"))
CB_FAILURE_THRESHOLD = int(os.getenv("CB_FAILURE_THRESHOLD", "5"))
CB_RESET_SECONDS = int(os.getenv("CB_RESET_SECONDS", "30"))

def get_mirror_bases():
    """
    Return up to 5 mirror base URLs, skipping unset/empty, and stripping trailing slash.
    """
    bases = [
        PRIMARY_MIRROR_BASE,
        FALLBACK_MIRROR_BASE_1,
        FALLBACK_MIRROR_BASE_2,
        FALLBACK_MIRROR_BASE_3,
        FALLBACK_MIRROR_BASE_4,
    ]
    result = []
    for b in bases:
        if b and b.strip():
            base = b.strip().rstrip("/")
            if base:
                result.append(base)
    return result