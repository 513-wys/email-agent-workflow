"""SQLite schema migrations for the local TraceInbox database."""

import hashlib
import inspect
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable


@dataclass(frozen=True)
class Migration:
    version: str
    description: str
    apply: Callable

    @property
    def checksum(self):
        payload = (
            f"{self.version}:{self.description}\n{inspect.getsource(self.apply)}"
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()


def _columns(conn, table):
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}


def _add_column(conn, table, definition):
    name = definition.split()[0]
    if name not in _columns(conn, table):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {definition}")


def _migration_001(conn):
    """Add stable source identity plus the tables needed by the three-day flow."""
    for definition in (
        "account_id TEXT",
        "provider TEXT",
        "source_uid TEXT",
        "internet_message_id TEXT",
        "provider_message_id TEXT",
        "received_at TEXT",
        "original_url TEXT DEFAULT ''",
        "content_hash TEXT",
    ):
        _add_column(conn, "emails", definition)

    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS mail_sync_state (
            account_id TEXT NOT NULL,
            folder TEXT NOT NULL,
            uidvalidity TEXT,
            last_uid INTEGER NOT NULL DEFAULT 0,
            last_synced_at TEXT,
            PRIMARY KEY (account_id, folder)
        );

        CREATE TABLE IF NOT EXISTS processing_runs (
            id TEXT PRIMARY KEY,
            account_id TEXT,
            started_at TEXT NOT NULL,
            finished_at TEXT,
            status TEXT NOT NULL,
            fetched INTEGER NOT NULL DEFAULT 0,
            inserted INTEGER NOT NULL DEFAULT 0,
            skipped INTEGER NOT NULL DEFAULT 0,
            failed INTEGER NOT NULL DEFAULT 0,
            error_summary TEXT
        );

        CREATE TABLE IF NOT EXISTS email_analysis (
            email_id INTEGER PRIMARY KEY,
            category TEXT NOT NULL,
            priority TEXT NOT NULL,
            confidence REAL NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
            requires_action INTEGER NOT NULL DEFAULT 0,
            requires_reply INTEGER NOT NULL DEFAULT 0,
            deadline_at TEXT,
            deadline_text TEXT,
            labels_json TEXT NOT NULL DEFAULT '[]',
            entities_json TEXT NOT NULL DEFAULT '[]',
            reason_codes_json TEXT NOT NULL DEFAULT '[]',
            model_provider TEXT,
            model_name TEXT,
            prompt_version TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS action_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_id INTEGER NOT NULL,
            fingerprint TEXT NOT NULL,
            title TEXT NOT NULL,
            details TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'OPEN'
                CHECK (status IN ('OPEN', 'DONE', 'DISMISSED', 'EXPIRED')),
            priority TEXT NOT NULL,
            deadline_at TEXT,
            expiry_at TEXT,
            evidence_text TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            user_modified INTEGER NOT NULL DEFAULT 0,
            UNIQUE (email_id, fingerprint),
            FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS knowledge_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type TEXT NOT NULL,
            source_id TEXT NOT NULL,
            title TEXT NOT NULL,
            source_url TEXT NOT NULL DEFAULT '',
            content_hash TEXT NOT NULL,
            indexed_at TEXT NOT NULL,
            UNIQUE (source_type, source_id)
        );

        CREATE TABLE IF NOT EXISTS knowledge_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            chunk_index INTEGER NOT NULL,
            text TEXT NOT NULL,
            embedding BLOB,
            token_count INTEGER NOT NULL DEFAULT 0,
            metadata_json TEXT NOT NULL DEFAULT '{}',
            UNIQUE (document_id, chunk_index),
            FOREIGN KEY (document_id) REFERENCES knowledge_documents(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS rag_queries (
            id TEXT PRIMARY KEY,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            model_provider TEXT,
            model_name TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS rag_citations (
            query_id TEXT NOT NULL,
            chunk_id INTEGER NOT NULL,
            email_id INTEGER NOT NULL,
            rank INTEGER NOT NULL,
            score REAL,
            quoted_text TEXT NOT NULL,
            PRIMARY KEY (query_id, rank),
            FOREIGN KEY (query_id) REFERENCES rag_queries(id) ON DELETE CASCADE,
            FOREIGN KEY (chunk_id) REFERENCES knowledge_chunks(id) ON DELETE CASCADE,
            FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_emails_account_uid
            ON emails(account_id, source_uid);
        CREATE INDEX IF NOT EXISTS idx_emails_internet_message_id
            ON emails(account_id, internet_message_id);
        CREATE INDEX IF NOT EXISTS idx_emails_received_at
            ON emails(received_at);
        CREATE INDEX IF NOT EXISTS idx_action_items_status_deadline
            ON action_items(status, deadline_at);
        CREATE INDEX IF NOT EXISTS idx_chunks_document
            ON knowledge_chunks(document_id, chunk_index);
        """
    )


def _migration_002(conn):
    """Enforce stable source identifiers when they are available."""
    conn.executescript(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_emails_account_source_uid
            ON emails(account_id, source_uid)
            WHERE account_id IS NOT NULL AND source_uid IS NOT NULL;
        CREATE UNIQUE INDEX IF NOT EXISTS uq_emails_account_message_id
            ON emails(account_id, internet_message_id)
            WHERE account_id IS NOT NULL
              AND internet_message_id IS NOT NULL
              AND internet_message_id <> '';
        """
    )


def _migration_003(conn):
    """Include UIDVALIDITY in an IMAP message's stable identity."""
    _add_column(conn, "emails", "uidvalidity TEXT")
    conn.executescript(
        """
        DROP INDEX IF EXISTS uq_emails_account_source_uid;
        CREATE UNIQUE INDEX IF NOT EXISTS uq_emails_account_uidvalidity_uid
            ON emails(account_id, uidvalidity, source_uid)
            WHERE account_id IS NOT NULL
              AND uidvalidity IS NOT NULL
              AND source_uid IS NOT NULL;
        """
    )


def _migration_004(conn):
    """Store Gmail thread identity used by the web interface URL."""
    _add_column(conn, "emails", "provider_thread_id TEXT")


def _migration_005(conn):
    """Persist structured action candidates produced by multidimensional triage."""
    _add_column(conn, "email_analysis", "action_items_json TEXT NOT NULL DEFAULT '[]'")


def _migration_006(conn):
    """Restart the one-time Inbox walk after removing the today-only filter."""
    conn.execute("UPDATE mail_sync_state SET last_uid=0, last_synced_at=NULL")


def _migration_007(conn):
    """Preserve the user-owned wrapper account for forwarded messages."""
    _add_column(conn, "emails", "forwarded_by TEXT")


def _migration_008(conn):
    """Persist cross-email topics and their source membership."""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS knowledge_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_key TEXT NOT NULL UNIQUE,
            topic_type TEXT NOT NULL,
            title_en TEXT NOT NULL,
            title_zh TEXT NOT NULL,
            summary_en TEXT NOT NULL DEFAULT '',
            summary_zh TEXT NOT NULL DEFAULT '',
            latest_update_at TEXT,
            deadline_at TEXT,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS knowledge_topic_emails (
            topic_id INTEGER NOT NULL,
            email_id INTEGER NOT NULL,
            PRIMARY KEY (topic_id, email_id),
            FOREIGN KEY (topic_id) REFERENCES knowledge_topics(id) ON DELETE CASCADE,
            FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_topic_emails_email ON knowledge_topic_emails(email_id);
        """
    )


MIGRATIONS = (
    Migration("001", "stable identity and three-day workflow tables", _migration_001),
    Migration("002", "unique stable email source identifiers", _migration_002),
    Migration("003", "include UIDVALIDITY in stable IMAP identity", _migration_003),
    Migration("004", "store provider thread identity", _migration_004),
    Migration("005", "store structured action candidates", _migration_005),
    Migration("006", "restart cursor for full Inbox backfill", _migration_006),
    Migration("007", "store forwarded message wrapper identity", _migration_007),
    Migration("008", "cross-email knowledge topics", _migration_008),
)


def apply_migrations(conn):
    """Apply pending migrations and reject changed already-applied migrations."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            description TEXT NOT NULL,
            applied_at TEXT NOT NULL,
            checksum TEXT NOT NULL
        )
        """
    )
    applied = {
        row[0]: row[1]
        for row in conn.execute("SELECT version, checksum FROM schema_migrations")
    }

    for migration in MIGRATIONS:
        if migration.version in applied:
            if applied[migration.version] != migration.checksum:
                raise RuntimeError(f"数据库迁移 {migration.version} 校验失败，请检查迁移历史")
            continue
        with conn:
            migration.apply(conn)
            conn.execute(
                """
                INSERT INTO schema_migrations(version, description, applied_at, checksum)
                VALUES (?, ?, ?, ?)
                """,
                (
                    migration.version,
                    migration.description,
                    datetime.now(timezone.utc).isoformat(),
                    migration.checksum,
                ),
            )
