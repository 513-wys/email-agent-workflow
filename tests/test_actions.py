import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import actions, db


class ActionItemTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_patch = patch("app.config.DB_PATH", Path(self.tmp.name) / "actions.db")
        self.db_patch.start()
        db.init_db()
        fields = "message_id sender subject body_text date gmail_link threat_score risk_level is_safe intent category priority sentiment language summary summary_zh context_json status account_id provider source_uid internet_message_id provider_message_id received_at original_url content_hash uidvalidity provider_thread_id forwarded_by".split()
        record = {key: None for key in fields}
        record.update({"trace_id": "action-email", "created_at": db.now_str(), "subject": "Review plan", "sender": "sender@example.com"})
        self.email_id = db.insert_email(record)

    def tearDown(self):
        self.db_patch.stop()
        self.tmp.cleanup()

    def test_sync_is_idempotent_and_user_completion_is_preserved(self):
        analysis = {
            "requires_action": True, "intent": "ACTION_REQUIRED", "priority": "P1_HIGH",
            "deadline_at": None, "deadline_text": None,
            "action_items": [{"title": "Review the plan", "evidence": "Please review the plan", "deadline_at": None}],
        }
        actions.sync(self.email_id, analysis)
        actions.sync(self.email_id, analysis)
        rows = db.list_action_items("OPEN")
        self.assertEqual(1, len(rows))
        db.set_action_status(rows[0]["id"], "DONE")
        actions.sync(self.email_id, analysis)
        self.assertEqual("DONE", db.list_action_items("DONE")[0]["status"])

    def test_verification_action_expires(self):
        analysis = {
            "requires_action": False, "intent": "VERIFICATION_CODE", "priority": "P1_HIGH",
            "deadline_at": "2020-01-01T00:00:00+00:00", "deadline_text": "expires soon",
            "action_items": [{"title": "Enter verification code", "evidence": "Code 123456", "deadline_at": "2020-01-01T00:00:00+00:00"}],
        }
        actions.sync(self.email_id, analysis)
        self.assertEqual(1, len(db.list_action_items("EXPIRED")))


if __name__ == "__main__":
    unittest.main()
