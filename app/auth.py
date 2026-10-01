"""Small account layer for the hosted multi-user edition."""
import hmac
import secrets
import sqlite3
from datetime import datetime, timezone

from flask import session
from werkzeug.security import check_password_hash, generate_password_hash

from app import config, db, settings_store
from app.tenant import workspace


def _conn():
    conn = sqlite3.connect(config.AUTH_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_login_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def create_user(email, password):
    normalized = (email or "").strip().lower()
    if not normalized or "@" not in normalized:
        raise ValueError("email")
    if len(password or "") < 10:
        raise ValueError("password")
    conn = _conn()
    try:
        cursor = conn.execute(
            "INSERT INTO users(email,password_hash,created_at) VALUES(?,?,?)",
            (normalized, generate_password_hash(password), datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        user_id = cursor.lastrowid
    except sqlite3.IntegrityError as exc:
        raise ValueError("exists") from exc
    finally:
        conn.close()
    ensure_workspace(user_id)
    return get_user(user_id)


def authenticate(email, password):
    conn = _conn()
    row = conn.execute("SELECT * FROM users WHERE email=?", ((email or "").strip().lower(),)).fetchone()
    if not row or not check_password_hash(row["password_hash"], password or ""):
        conn.close()
        return None
    conn.execute(
        "UPDATE users SET last_login_at=? WHERE id=?",
        (datetime.now(timezone.utc).isoformat(), row["id"]),
    )
    conn.commit()
    conn.close()
    ensure_workspace(row["id"])
    return dict(row)


def get_user(user_id):
    if not user_id:
        return None
    conn = _conn()
    row = conn.execute("SELECT id,email,created_at,last_login_at FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def ensure_workspace(user_id):
    with workspace(user_id):
        db.init_db()
        settings_store.init_table()


def csrf_token():
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


def valid_csrf(candidate):
    expected = session.get("csrf_token", "")
    return bool(expected and candidate and hmac.compare_digest(expected, candidate))
