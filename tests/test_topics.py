import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import db, topics


class TopicTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_patch = patch("app.config.DB_PATH", Path(self.tmp.name) / "topics.db")
        self.db_patch.start()
        db.init_db()

    def tearDown(self):
        self.db_patch.stop()
        self.tmp.cleanup()

    def _insert(self, trace_id, subject, intent, summary):
        fields = "message_id sender body_text date gmail_link threat_score risk_level sentiment language context_json account_id provider source_uid internet_message_id provider_message_id received_at original_url content_hash uidvalidity provider_thread_id forwarded_by".split()
        record = {key: None for key in fields}
        record.update({"trace_id": trace_id, "created_at": db.now_str(), "subject": subject,
                       "sender": "sender@example.com", "intent": intent, "category": intent,
                       "priority": "P2_NORMAL", "summary": summary, "summary_zh": summary,
                       "is_safe": 1, "status": "已分类"})
        email_id = db.insert_email(record)
        db.upsert_email_analysis(email_id, {
            "intent": intent, "priority": "P2_NORMAL", "confidence": .9,
            "requires_action": False, "requires_reply": False, "deadline_at": None,
            "deadline_text": None, "labels": [], "entities": [], "reason_codes": [],
            "model_provider": "test", "model_name": "", "prompt_version": "test", "action_items": [],
        })

    def test_related_project_messages_are_grouped(self):
        self._insert("a", "ShowMeYourAgent submission", "PROJECT_UPDATE", "Hackathon update")
        self._insert("b", "SMYA Hackathon deadline", "ACTION_REQUIRED", "Submission instructions")
        topics.rebuild()
        rows = db.list_topics()
        project = next(row for row in rows if row["topic_key"] == "project:showmeyouragent")
        self.assertEqual(2, project["email_count"])

    def test_subscription_is_recognized_as_topic(self):
        email = {"subject": "Your plan will renew", "summary": "Monthly subscription renewal", "intent": "PAYMENT_BILLING"}
        self.assertTrue(topics.is_subscription(email, {}))


if __name__ == "__main__":
    unittest.main()
