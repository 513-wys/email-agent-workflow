import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import db, triage


class TriageTests(unittest.TestCase):
    def test_low_confidence_becomes_other_and_invalid_deadline_is_dropped(self):
        result = triage.normalize({"category": "BUSINESS_INQUIRY", "priority": "P1_HIGH", "confidence": 0.4, "deadline_at": "tomorrow", "requires_action": True})
        self.assertEqual("OTHER", result["intent"])
        self.assertIsNone(result["deadline_at"])

    def test_output_is_persisted(self):
        result = triage.normalize({
            "category": "MEETING_CALENDAR", "priority": "P2_NORMAL", "confidence": 0.92,
            "requires_action": True, "requires_reply": True, "deadline_at": "2026-10-08T09:00:00+08:00",
            "deadline_text": "by 8 Oct", "labels": ["career"], "reason_codes": ["EXPLICIT_BOOKING"],
            "entities": [{"type": "ORGANIZATION", "value": "NTU"}],
            "action_items": [{"title": "Book a coaching slot", "evidence": "Book now"}],
        })
        with tempfile.TemporaryDirectory() as tmp, patch("app.config.DB_PATH", Path(tmp) / "test.db"):
            db.init_db()
            fields = "message_id sender subject body_text date gmail_link threat_score risk_level is_safe intent category priority sentiment language summary summary_zh context_json status account_id provider source_uid internet_message_id provider_message_id received_at original_url content_hash uidvalidity provider_thread_id".split()
            record = {key: None for key in fields}
            record.update({"trace_id": "analysis-test", "created_at": db.now_str()})
            email_id = db.insert_email(record)
            db.upsert_email_analysis(email_id, result)
            stored = db.get_email_analysis(email_id)
            self.assertEqual("MEETING_CALENDAR", stored["category"])
            self.assertEqual("NTU", stored["entities"][0]["value"])
            self.assertEqual("Book a coaching slot", stored["action_items"][0]["title"])


if __name__ == "__main__":
    unittest.main()
