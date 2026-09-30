import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import db, demo_seed, rag


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


if __name__ == "__main__":
    unittest.main()
