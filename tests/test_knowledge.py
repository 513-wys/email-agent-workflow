import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import db, knowledge


class KnowledgeIndexTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_patch = patch("app.config.DB_PATH", Path(self.tmp.name) / "knowledge.db")
        self.db_patch.start()
        db.init_db()

    def tearDown(self):
        self.db_patch.stop()
        self.tmp.cleanup()

    def _email(self, body="First paragraph.\n\nSecond paragraph.", safe=1):
        return {
            "id": 7, "subject": "Project update", "sender": "sender@example.com",
            "received_at": "2026-09-30T10:00:00+08:00", "date": "", "summary": "Summary",
            "summary_zh": "摘要", "body_text": body, "is_safe": safe,
            "status": "已分类" if safe else "已隔离", "provider": "GMAIL", "original_url": "https://example.com/original",
        }

    def test_index_is_incremental_and_replaces_changed_chunks(self):
        status, count = knowledge.index_email(self._email())
        self.assertEqual("indexed", status)
        self.assertGreater(count, 0)
        self.assertEqual("unchanged", knowledge.index_email(self._email())[0])
        before = db.knowledge_stats()
        self.assertEqual(1, before["documents"])

        changed_status, _ = knowledge.index_email(self._email(body="Changed body."))
        self.assertEqual("indexed", changed_status)
        after = db.knowledge_stats()
        self.assertEqual(1, after["documents"])
        self.assertEqual(1, after["chunks"])

    def test_quarantined_email_is_not_indexed(self):
        self.assertEqual(("ineligible", 0), knowledge.index_email(self._email(safe=0)))
        self.assertEqual(0, db.knowledge_stats()["documents"])

    def test_chunking_is_stable_and_bounded(self):
        text = "\n\n".join(["A" * 700, "B" * 700, "C" * 700])
        first = knowledge.chunk_text(text)
        second = knowledge.chunk_text(text)
        self.assertEqual(first, second)
        self.assertGreater(len(first), 1)
        self.assertTrue(all(len(chunk) <= knowledge.CHUNK_SIZE + knowledge.CHUNK_OVERLAP + 1 for chunk in first))


if __name__ == "__main__":
    unittest.main()
