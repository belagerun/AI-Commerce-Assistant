import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv(BASE_DIR / ".env")

APP_NAME = "AI Agent Network for E-commerce Customer Service"
DATABASE_PATH = BASE_DIR / "chat_history.db"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
DATA_DIR = BASE_DIR / "data"
PRODUCT_IMAGES_DIR = DATA_DIR / "product_images"
CHAT_UPLOADS_DIR = DATA_DIR / "chat_uploads"

AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini")
AI_VISION_MODEL = os.getenv("AI_VISION_MODEL", AI_MODEL)

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587") or "587")
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "")
EMAIL_DEBUG = os.getenv("EMAIL_DEBUG", "false").strip().lower() in {"1", "true", "yes", "on"}
COOKIE_PASSWORD = os.getenv("COOKIE_PASSWORD", "local-dev-cookie-password-change-me")
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").strip().lower() in {"1", "true", "yes", "on"}
