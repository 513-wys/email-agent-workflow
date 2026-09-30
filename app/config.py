"""配置加载：优先读 .env，其次读环境变量，最后用默认值。"""
import os
from pathlib import Path

from dotenv import load_dotenv

# 项目根目录（email-assistant/）
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "email_assistant.db"


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

# ---- Telegram ----
TELEGRAM_BOT_TOKEN = _env("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = _env("TELEGRAM_CHAT_ID")

# ---- Web ----
HOST = _env("HOST", "127.0.0.1")
PORT = int(_env("PORT", "8000"))
