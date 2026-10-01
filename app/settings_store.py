"""运行时可改设置：优先读本地 SQLite，未设置则回退 .env/config 默认值。"""
import sqlite3
import base64
import hashlib

from app import config
from app import tenant
from cryptography.fernet import Fernet, InvalidToken

SECRET_KEYS = {"deepseek_api_key", "mail_password"}

PROVIDERS = {
    "gmail": {
        "label": "Gmail",
        "host": "imap.gmail.com",
        "port": 993,
        "hint": "需先在 Google 账号开启两步验证，再在「安全性 → 应用专用密码」生成一个专用密码（不是登录密码）。",
    },
    "163": {
        "label": "网易 163",
        "host": "imap.163.com",
        "port": 993,
        "hint": "登录 163 网页版 → 设置 → POP3/SMTP/IMAP → 开启 IMAP 服务并生成「客户端授权码」（不是登录密码）。",
    },
}


def _conn():
    conn = sqlite3.connect(tenant.db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_table():
    conn = _conn()
    conn.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    conn.commit()
    conn.close()


def get(key, default=None):
    conn = _conn()
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    if row is None or row["value"] is None or row["value"] == "":
        return default
    value = row["value"]
    if key in SECRET_KEYS and value.startswith("enc:v1:"):
        try:
            return _fernet().decrypt(value.removeprefix("enc:v1:").encode()).decode()
        except (InvalidToken, ValueError):
            return default
    return value


def set(key, value):
    if key in SECRET_KEYS and value:
        value = "enc:v1:" + _fernet().encrypt(str(value).encode()).decode()
    conn = _conn()
    conn.execute("INSERT OR REPLACE INTO settings(key, value) VALUES(?, ?)", (key, value))
    conn.commit()
    conn.close()


def _fernet():
    source = (config.APP_ENCRYPTION_KEY or config.APP_SECRET_KEY).encode()
    key = base64.urlsafe_b64encode(hashlib.sha256(source).digest())
    return Fernet(key)


def get_all_masked():
    """给设置页表单回填用：密钥/密码类字段只给掩码提示，绝不回显明文。"""
    mail_mode = get("mail_mode", "demo" if config.DEMO_MODE else "real")
    mail_provider = get("mail_provider", "gmail")
    return {
        "deepseek_api_key_set": bool(get("deepseek_api_key", config.DEEPSEEK_API_KEY)),
        "mail_mode": mail_mode,
        "mail_provider": mail_provider,
        "mail_user": get("mail_user", config.IMAP_USER) or "",
        "mail_password_set": bool(get("mail_password", config.IMAP_PASSWORD)),
        "initial_sync_limit": get("initial_sync_limit", "100"),
        "initial_sync_completed": get("initial_sync_completed", "0") == "1",
        "owner_emails": get("owner_emails", ""),
    }
