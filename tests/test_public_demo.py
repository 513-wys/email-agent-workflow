import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import config, db, demo_seed, rag
from app.main import app


class PublicDemoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_patch = patch("app.config.DB_PATH", Path(self.tmp.name) / "demo.db")
        self.user_data_patch = patch("app.config.USER_DATA_DIR", Path(self.tmp.name) / "users")
        self.db_patch.start()
        self.user_data_patch.start()
        db.init_db()

    def tearDown(self):
        self.user_data_patch.stop()
        self.db_patch.stop()
        self.tmp.cleanup()

    def test_seed_contains_only_synthetic_addresses(self):
        self.assertTrue(demo_seed.seed())
        rows = db.list_emails()
        self.assertEqual(20, len(rows))
        self.assertTrue(all("example" in row["sender"] or row["sender"].endswith(".invalid") for row in rows))
        self.assertEqual(1, sum(not row["is_safe"] for row in rows))
        self.assertGreaterEqual(len(db.list_topics()), 8)

    def test_recording_helpers_are_not_shipped_as_product_routes(self):
        app.config.update(TESTING=True, SECRET_KEY="test-secret")
        client = app.test_client()
        self.assertEqual(404, client.get("/presentation").status_code)
        self.assertEqual(404, client.get("/presenter").status_code)

    def test_old_synthetic_seed_is_safely_replaced(self):
        db.insert_email({
            "trace_id": "public-demo-old", "message_id": "<old@example.invalid>",
            "sender": "old@example.com", "subject": "Old demo", "body_text": "Synthetic",
            "date": "2026-01-01T00:00:00+00:00", "gmail_link": "", "threat_score": 0,
            "risk_level": "LOW", "is_safe": 1, "intent": "OTHER", "category": "OTHER",
            "priority": "P3_LOW", "sentiment": "NEUTRAL", "language": "en-US",
            "summary": "Old", "summary_zh": "", "context_json": "{}", "status": "已分类",
            "created_at": "2026-01-01T00:00:00+00:00", "account_id": "public-demo",
            "provider": "DEMO", "source_uid": "1", "internet_message_id": "",
            "provider_message_id": "", "received_at": "2026-01-01T00:00:00+00:00",
            "original_url": "", "content_hash": "old", "uidvalidity": "demo",
            "provider_thread_id": "", "forwarded_by": "",
        })
        self.assertTrue(demo_seed.seed())
        self.assertEqual(20, db.stats()["total"])

    def test_public_demo_answer_does_not_call_model(self):
        source = {"id": 1, "email_id": 1, "title": "Demo", "sender": "demo@example.edu",
                  "text": "Synthetic project deadline is Friday.", "score": 1.0}
        with patch("app.rag.config.PUBLIC_DEMO", True), patch("app.rag.retrieve", return_value=[source]), patch(
            "app.rag.llm.chat_text"
        ) as model:
            result = rag.answer("What is due?")
        model.assert_not_called()
        self.assertEqual(1, len(result["sources"]))

    def test_public_demo_abstention_matches_question_language(self):
        with patch("app.rag.retrieve", return_value=[]):
            english = rag.answer("What hotel did I reserve?")
            chinese = rag.answer("我预订了哪家酒店？")
        self.assertIn("not enough relevant email evidence", english["answer"])
        self.assertIn("没有找到足够相关的邮件依据", chinese["answer"])

    def test_published_demo_question_uses_auditable_synthesis(self):
        sources = [
            {"id": 1, "email_id": 1, "title": "Deadline", "sender": "teacher@example.edu", "text": "Deadline", "score": 1.0},
            {"id": 2, "email_id": 2, "title": "Receipt", "sender": "platform@example.edu", "text": "Received", "score": 0.9},
        ]
        with patch("app.rag.config.PUBLIC_DEMO", True), patch("app.rag.retrieve", return_value=sources):
            result = rag.answer("What remains to be done for AX4102?")
        self.assertIn("proposal was submitted", result["answer"])
        self.assertIn("No further action", result["answer"])

    def test_public_demo_entry_uses_only_display_values(self):
        app.config.update(TESTING=True, SECRET_KEY="test-secret")
        with patch.object(config, "PUBLIC_DEMO", True), patch.object(config, "MULTI_USER_MODE", False):
            client = app.test_client()
            page = client.get("/")
            self.assertEqual(200, page.status_code)
            self.assertIn(b"demo.student@example.com", page.data)
            self.assertIn(b"sk-demo-example-key", page.data)
            with patch("app.main.settings_store.set") as save_setting:
                response = client.post("/demo/start", data={
                    "demo_email": "submitted@example.com",
                    "demo_api_key": "should-never-be-stored",
                    "demo_limit": "20",
                })
            self.assertEqual(302, response.status_code)
            self.assertTrue(response.headers["Location"].endswith("/demo/import"))
            save_setting.assert_not_called()

            progress = client.get("/demo/import")
            self.assertEqual(200, progress.status_code)
            self.assertIn(b"20", progress.data)

    def test_demo_email_opens_simulated_original(self):
        app.config.update(TESTING=True, SECRET_KEY="test-secret")
        with patch.object(config, "PUBLIC_DEMO", True), patch.object(config, "MULTI_USER_MODE", False):
            demo_seed.seed()
            client = app.test_client()
            detail = client.get("/emails/1")
            self.assertIn(b"/demo/original/1", detail.data)
            original = client.get("/demo/original/1")
            self.assertEqual(200, original.status_code)
            self.assertIn(b"Synthetic Gmail preview", original.data)

    def test_twenty_case_dataset_populates_product_surfaces(self):
        app.config.update(TESTING=True, SECRET_KEY="test-secret")
        with patch.object(config, "PUBLIC_DEMO", True), patch.object(config, "MULTI_USER_MODE", False):
            demo_seed.seed()
            client = app.test_client()
            emails = client.get("/emails")
            knowledge_page = client.get("/knowledge")
            actions_page = client.get("/actions")
            self.assertEqual(200, emails.status_code)
            self.assertIn(b"AX4102", emails.data)
            self.assertIn(b"CloudNotes", emails.data)
            self.assertEqual(200, knowledge_page.status_code)
            self.assertIn(b"Project NOVA", knowledge_page.data)
            self.assertEqual(200, actions_page.status_code)
            self.assertIn(b"CloudNotes", actions_page.data)

            digest = client.post("/digest")
            self.assertEqual(200, digest.status_code)
            self.assertIn(b"Project NOVA", digest.data)
            self.assertNotIn(b"mailbox suspension", digest.data)

    def test_explicit_demo_entry_uses_isolated_synthetic_workspace(self):
        app.config.update(TESTING=True, SECRET_KEY="test-secret")
        with patch.object(config, "PUBLIC_DEMO", False), patch.object(config, "MULTI_USER_MODE", True):
            client = app.test_client()
            entry = client.get("/demo")
            self.assertEqual(200, entry.status_code)
            self.assertIn(b"demo.student@example.com", entry.data)
            with client.session_transaction() as current_session:
                csrf_token = current_session["csrf_token"]
            response = client.post("/demo/start", data={"csrf_token": csrf_token})
            self.assertEqual(302, response.status_code)
            self.assertTrue(response.headers["Location"].endswith("/demo/import"))
            progress = client.get("/demo/import")
            self.assertEqual(200, progress.status_code)
            dashboard = client.get("/dashboard")
            self.assertEqual(200, dashboard.status_code)
            self.assertIn(b"AX4102", dashboard.data)


if __name__ == "__main__":
    unittest.main()
