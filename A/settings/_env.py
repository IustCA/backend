"""Environment helpers used by every settings module.

Importable as:  from A.settings._env import env_bool, env_int, env_list, BASE_DIR
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env exactly once, the first time any settings module is imported.
load_dotenv(BASE_DIR / '.env')


def env_bool(key: str, default: bool = False) -> bool:
    return os.getenv(key, str(default)).lower() in ('1', 'true', 'yes', 'on')


def env_int(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, default))
    except (TypeError, ValueError):
        return default


def env_list(key: str, default: list | None = None, sep: str = ',') -> list:
    raw = os.getenv(key)
    if not raw:
        return default or []
    return [item.strip() for item in raw.split(sep) if item.strip()]


def env_str(key: str, default: str = '') -> str:
    return os.getenv(key, default)
