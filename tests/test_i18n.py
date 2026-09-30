import unittest
from unittest.mock import patch

from app.main import app


class I18nTests(unittest.TestCase):
    def test_onboarding_first_sync_limit_defaults_to_100(self):
        with patch("app.main.settings_store.get", side_effect=lambda key, default=None: "0" if key == "initial_sync_completed" else default):
            response = self.client.get("/onboarding")
        self.assertIn(b'name="initial_sync_limit"', response.data)
        self.assertIn(b'value="100"', response.data)

    def test_dashboard_ingest_is_incremental_after_onboarding(self):
        batch = {"results": [], "inserted": 0, "skipped": 0, "failed": 0,
                 "remaining": 0, "older_skipped": 0}
        values = {"initial_sync_completed": "1"}
        with patch("app.main.settings_store.get", side_effect=lambda key, default=None: values.get(key, default)), patch(
            "app.main.pipeline.ingest", return_value=batch
        ) as ingest:
            response = self.client.post("/ingest")
        self.assertEqual(302, response.status_code)
        ingest.assert_called_once_with(limit=500)

    def setUp(self):
        self.client = app.test_client()

    def test_english_is_default(self):
        response = self.client.get("/", follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertIn(b"Enter workspace", response.data)
        self.assertIn(b'<html lang="en">', response.data)

    def test_language_switch_persists_chinese_cookie(self):
        response = self.client.get("/language/zh?next=/emails")
        self.assertEqual(302, response.status_code)
        self.assertEqual("/emails", response.headers["Location"])
        page = self.client.get("/emails")
        self.assertIn("邮件列表".encode(), page.data)
        self.assertIn(b'<html lang="zh-CN">', page.data)

    def test_language_redirect_rejects_external_target(self):
        response = self.client.get("/language/zh?next=https://example.com")
        self.assertEqual("/", response.headers["Location"])

    def test_demo_email_does_not_offer_fake_gmail_link(self):
        response = self.client.get("/emails/40")
        self.assertIn(b"built-in demo email", response.data)
        self.assertNotIn(b"Find this email in Gmail", response.data)

    def test_real_gmail_detail_rebuilds_canonical_thread_link(self):
        email_row = {
            "id": 99, "provider": "GMAIL", "provider_thread_id": "987654321",
            "original_url": "https://mail.google.com/mail/u/old@example.com/#all/stale",
            "gmail_link": "", "context_json": "{}", "message_id": "<x@example.com>",
            "subject": "Test", "sender": "sender@example.com", "date": "", "received_at": "",
            "status": "已分类", "threat_score": 0, "risk_level": "LOW", "is_safe": 1,
            "intent": "OTHER", "category": "其他", "priority": "P2_NORMAL",
            "sentiment": "NEUTRAL", "language": "en-US", "summary": "", "summary_zh": "",
            "body_text": "",
        }
        with patch("app.main.db.get_email", return_value=email_row), patch(
            "app.main.settings_store.get", return_value="user@example.com"
        ):
            response = self.client.get("/emails/99")
        self.assertIn(b"https://mail.google.com/mail/u/0/#all/3ade68b1", response.data)
        self.assertNotIn(b"old@example.com", response.data)


if __name__ == "__main__":
    unittest.main()
