"""Request and background-job workspace isolation.

Each account receives a separate SQLite database.  Keeping the existing query
layer inside a per-user database makes accidental cross-account reads much
harder than relying on every query author to remember a user_id predicate.
"""
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path

from app import config


_workspace_id = ContextVar("workspace_id", default=None)


def current_id():
    return _workspace_id.get()


def bind(workspace_id):
    return _workspace_id.set(int(workspace_id) if workspace_id is not None else None)


def reset(token):
    _workspace_id.reset(token)


def db_path() -> Path:
    workspace_id = current_id()
    if workspace_id is None:
        return Path(config.DB_PATH)
    root = Path(config.USER_DATA_DIR)
    root.mkdir(parents=True, exist_ok=True)
    return root / f"workspace-{workspace_id}.db"


@contextmanager
def workspace(workspace_id):
    token = bind(workspace_id)
    try:
        yield
    finally:
        reset(token)
