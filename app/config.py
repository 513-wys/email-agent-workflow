"""Load TraceInbox configuration from .env, environment, and safe defaults."""
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv

# 项目根目录（email-assistant/）
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "email_assistant.db"
AUTH_DB_PATH = DATA_DIR / "accounts.db"
USER_DATA_DIR = DATA_DIR / "users"
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)


def _env(key, default=""):
    return os.getenv(key, default)


# ---- LLM ----
DEEPSEEK_API_KEY = _env("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = _env("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
DEEPSEEK_MODEL = _env("DEEPSEEK_MODEL", "deepseek-chat")
OLLAMA_BASE_URL = _env("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = _env("OLLAMA_MODEL", "qwen2.5:7b")

# ---- 邮件 ----
IMAP_HOST = _env("IMAP_HOST", "imap.gmail.com")
IMAP_PORT = int(_env("IMAP_PORT", "993"))
IMAP_USER = _env("IMAP_USER")
IMAP_PASSWORD = _env("IMAP_PASSWORD")
DEMO_MODE = _env("DEMO_MODE", "true").lower() in ("1", "true", "yes", "on")
PUBLIC_DEMO = _env("PUBLIC_DEMO", "false").lower() in ("1", "true", "yes", "on")
MULTI_USER_MODE = _env("MULTI_USER_MODE", "false").lower() in ("1", "true", "yes", "on")
COOKIE_SECURE = _env("COOKIE_SECURE", "false").lower() in ("1", "true", "yes", "on")

# ---- Telegram ----
TELEGRAM_BOT_TOKEN = _env("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = _env("TELEGRAM_CHAT_ID")

# ---- Web ----
HOST = _env("HOST", "127.0.0.1")
PORT = int(_env("PORT", "8000"))
APP_SECRET_KEY = _env("APP_SECRET_KEY") or secrets.token_urlsafe(48)
APP_ENCRYPTION_KEY = _env("APP_ENCRYPTION_KEY")
