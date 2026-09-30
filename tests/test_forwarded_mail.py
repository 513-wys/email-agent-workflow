import unittest
from unittest.mock import patch

from app import security
from app.forwarded_mail import normalize, original_sender


FORWARDED_BODY = """
________________________________
发件人: Student Leadership Development <leadership@university.example>
已发送: 2026年9月28日星期一 18:41:17
主题: Voting for GSA Elections

Please vote at https://elections.university.example/vote
"""


class ForwardedMailTests(unittest.TestCase):
    def test_extracts_original_sender_only_from_owned_wrapper(self):
        sender = original_sender(
            "Student Owner <student@university.example>", FORWARDED_BODY,
            "student@university.example\npersonal@example.com",
        )
        self.assertEqual("Student Leadership Development <leadership@university.example>", sender)
        self.assertEqual("", original_sender("stranger@example.com", FORWARDED_BODY, "owner@example.com"))

    def test_normalize_preserves_forwarding_account(self):
        message = normalize(
            {"from": "student@university.example", "body_text": FORWARDED_BODY},
            "student@university.example",
        )
        self.assertEqual("Student Leadership Development <leadership@university.example>", message["from"])
        self.assertEqual("student@university.example", message["forwarded_by"])

    def test_trusted_institutional_forward_is_not_quarantined_for_external_link_alone(self):
        message = {
            "from": "Student Leadership Development <leadership@university.example>",
            "forwarded_by": "student@university.example",
            "subject": "Voting for GSA Elections", "body_text": FORWARDED_BODY,
            "headers": {}, "date": "",
        }
        model_result = {"is_safe": False, "threat_score": 85, "risk_level": "HIGH", "reasons": ["external link"]}
        with patch("app.security.llm.chat_json", return_value=model_result), patch(
            "app.security.settings_store.get", return_value="student@university.example"
        ):
            result = security.evaluate(message)
        self.assertTrue(result["is_safe"])
        self.assertEqual(70, result["threat_score"])


if __name__ == "__main__":
    unittest.main()
