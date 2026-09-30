import unittest
from unittest.mock import patch

from app import rag


class RetrievalTests(unittest.TestCase):
    def test_course_identifier_is_a_hard_filter_and_sources_are_deduplicated(self):
        chunks = [
            {"id": 1, "chunk_index": 0, "email_id": 10, "title": "Google AI Pro", "text": "AI task and subscription"},
            {"id": 2, "chunk_index": 0, "email_id": 20, "title": "PE6204 Welcome", "text": "PE6204 project task details"},
            {"id": 3, "chunk_index": 1, "email_id": 20, "title": "PE6204 Welcome", "text": "PE6204 bring a laptop"},
        ]
        with patch("app.rag.db.list_knowledge_chunks", return_value=chunks):
            rows = rag.retrieve("PE6204 有什么任务")
        self.assertEqual([20], [row["email_id"] for row in rows])
        self.assertIn("project task details", rows[0]["text"])
        self.assertIn("bring a laptop", rows[0]["text"])

    def test_unmatched_explicit_identifier_returns_no_sources(self):
        chunks = [{"id": 1, "email_id": 10, "title": "PE6204 Welcome", "text": "Course task"}]
        with patch("app.rag.db.list_knowledge_chunks", return_value=chunks):
            self.assertEqual([], rag.retrieve("PE9999 有什么任务"))


if __name__ == "__main__":
    unittest.main()
