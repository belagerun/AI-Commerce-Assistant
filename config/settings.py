import os
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv(BASE_DIR / ".env")

try:
    import streamlit as st
except ImportError:
    st = None


def _get_setting(name: str, default: str = "") -> str:
    if st is not None:
        try:
            if name in st.secrets:
                return str(st.secrets[name])
        except Exception:
            pass
    return os.getenv(name, default)


def _get_bool_setting(name: str, default: str = "false") -> bool:
    return _get_setting(name, default).strip().lower() in {"1", "true", "yes", "on"}


def _get_int_setting(name: str, default: str) -> int:
    raw_value = _get_setting(name, default).strip()
    try:
        return int(raw_value)
    except ValueError:
        return int(default)


def _log_smtp_diagnostics() -> None:
    fields: dict[str, Any] = {
        "SMTP_HOST": SMTP_HOST,
        "SMTP_PORT": SMTP_PORT,
        "SMTP_USERNAME": SMTP_USERNAME,
        "SMTP_PASSWORD": SMTP_PASSWORD,
        "SMTP_FROM": SMTP_FROM,
    }
    print("SMTP diagnostics:")
    for name, value in fields.items():
        print(f"- {name} loaded: {'yes' if bool(value) else 'no'}")


APP_NAME = "AI Agent Network for E-commerce Customer Service"
DATABASE_PATH = BASE_DIR / "chat_history.db"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
DATA_DIR = BASE_DIR / "data"
PRODUCT_IMAGES_DIR = DATA_DIR / "product_images"
CHAT_UPLOADS_DIR = DATA_DIR / "chat_uploads"

AI_API_KEY = _get_setting("AI_API_KEY", "")
AI_MODEL = _get_setting("AI_MODEL", "gpt-4o-mini")
AI_VISION_MODEL = _get_setting("AI_VISION_MODEL", AI_MODEL)
SMTP_HOST = _get_setting("SMTP_HOST", "")
SMTP_PORT = _get_int_setting("SMTP_PORT", "587")
SMTP_USERNAME = _get_setting("SMTP_USERNAME", "")
SMTP_PASSWORD = _get_setting("SMTP_PASSWORD", "")
SMTP_FROM = _get_setting("SMTP_FROM", "")
EMAIL_DEBUG = _get_bool_setting("EMAIL_DEBUG")
COOKIE_PASSWORD = _get_setting("COOKIE_PASSWORD", "local-dev-cookie-password-change-me")
DEBUG_MODE = _get_bool_setting("DEBUG_MODE")

_log_smtp_diagnostics()
