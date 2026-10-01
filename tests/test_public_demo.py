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
        self.db_patch.start()
        db.init_db()

    def tearDown(self):
        self.db_patch.stop()
        self.tmp.cleanup()

    def test_seed_contains_only_synthetic_addresses(self):
        self.assertTrue(demo_seed.seed())
        rows = db.list_emails()
        self.assertEqual(5, len(rows))
        self.assertTrue(all("example" in row["sender"] for row in rows))

    def test_public_demo_answer_does_not_call_model(self):
        source = {"id": 1, "email_id": 1, "title": "Demo", "sender": "demo@example.edu",
                  "text": "Synthetic project deadline is Friday.", "score": 1.0}
        with patch("app.rag.config.PUBLIC_DEMO", True), patch("app.rag.retrieve", return_value=[source]), patch(
            "app.rag.llm.chat_text"
        ) as model:
            result = rag.answer("What is due?")
        model.assert_not_called()
        self.assertEqual(1, len(result["sources"]))

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
            self.assertTrue(response.headers["Location"].endswith("/dashboard"))
            save_setting.assert_not_called()

    def test_demo_start_is_unavailable_outside_public_demo(self):
        app.config.update(TESTING=True, SECRET_KEY="test-secret")
        with patch.object(config, "PUBLIC_DEMO", False), patch.object(config, "MULTI_USER_MODE", False):
            response = app.test_client().post("/demo/start")
        self.assertEqual(302, response.status_code)
        self.assertTrue(response.headers["Location"].endswith("/"))


if __name__ == "__main__":
    unittest.main()
