"""Provide optional legacy Telegram alerts when explicitly configured."""
import requests

from app import config


def send(text):
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        return False
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": config.TELEGRAM_CHAT_ID, "text": text},
            timeout=10,
        )
        return r.status_code == 200
    except Exception:
        return False
