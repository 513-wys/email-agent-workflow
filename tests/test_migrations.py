import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import db


class MigrationTests(unittest.TestCase):
    def test_migrations_are_repeatable_and_preserve_existing_email(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.db"
            with patch("app.config.DB_PATH", path):
                db.init_db()
                conn = sqlite3.connect(path)
                conn.execute(
                    """
                    INSERT INTO emails(trace_id, subject, created_at)
                    VALUES ('legacy-1', '保留的历史邮件', '2026-09-30 00:00:00')
                    """
                )
                legacy_id = conn.execute(
                    "SELECT id FROM emails WHERE trace_id='legacy-1'"
                ).fetchone()[0]
                conn.commit()
                conn.close()

                db.init_db()

                conn = sqlite3.connect(path)
                self.assertEqual(
                    legacy_id,
                    conn.execute(
                        "SELECT id FROM emails WHERE trace_id='legacy-1'"
                    ).fetchone()[0],
                )
                self.assertEqual(
            [("001",), ("002",), ("003",), ("004",), ("005",), ("006",), ("007",), ("008",)],
                    conn.execute(
                        "SELECT version FROM schema_migrations ORDER BY version"
                    ).fetchall(),
                )
                tables = {
                    row[0]
                    for row in conn.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    )
                }
                self.assertTrue(
                    {
                        "mail_sync_state",
                        "processing_runs",
                        "email_analysis",
                        "action_items",
                        "knowledge_documents",
                        "knowledge_chunks",
                        "rag_queries",
                        "rag_citations",
                    }.issubset(tables)
                )
                conn.close()


if __name__ == "__main__":
    unittest.main()
