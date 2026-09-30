import unittest

from app.mail_links import gmail_message_url, gmail_search_url


class MailLinkTests(unittest.TestCase):
    def test_precise_gmail_link_uses_account_and_hex_message_id(self):
        self.assertEqual(
            "https://mail.google.com/mail/u/0/#all/75bcd15",
            gmail_message_url("user@example.com", "123456789"),
        )

    def test_fallback_prefers_rfc822_message_id(self):
        url = gmail_search_url("user@example.com", "<abc@example.com>")
        self.assertIn("/u/0/#search/", url)
        self.assertIn("rfc822msgid%3A%3Cabc%40example.com%3E", url)

    def test_fallback_can_search_sender_and_subject(self):
        url = gmail_search_url("user@example.com", sender="a@example.com", subject="Project update")
        self.assertIn("from%3A%22a%40example.com%22", url)
        self.assertIn("subject%3A%22Project%20update%22", url)


if __name__ == "__main__":
    unittest.main()
