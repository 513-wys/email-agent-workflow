import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import db, email_client


RAW_EMAIL = b"""From: Sender <sender@example.com>\r
To: user@example.com\r
Subject: Incremental test\r
Message-ID: <stable-message@example.com>\r
Date: Wed, 30 Sep 2026 09:15:00 +0800\r
Content-Type: text/plain; charset=utf-8\r
\r
Please review the attached plan.\r
"""


class FakeImap:
    instances = []

    def __init__(self, host, port):
        self.calls = []
        self.__class__.instances.append(self)

    def login(self, user, password):
        self.calls.append(("login", user))
        return "OK", []

    def select(self, folder, readonly=False):
        self.calls.append(("select", folder, readonly))
        return "OK", [b"1"]

    def response(self, name):
        return name, [b"777"]

    def uid(self, command, *args):
        self.calls.append(("uid", command, *args))
        if command == "search":
            return "OK", [b"101"]
        if command == "fetch":
            meta = b'1 (UID 101 INTERNALDATE "30-Sep-2026 09:16:00 +0800" X-GM-MSGID 123456789 X-GM-THRID 987654321 BODY[] {1}'
            return "OK", [(meta, RAW_EMAIL), b")"]
        raise AssertionError(command)

    def logout(self):
        self.calls.append(("logout",))
        return "BYE", []


class ManyMessagesImap(FakeImap):
    def uid(self, command, *args):
        self.calls.append(("uid", command, *args))
        if command == "search":
            return "OK", [b"101 102 103 104 105"]
        if command == "fetch":
            uid = args[0].decode()
            meta = (
                f'1 (UID {uid} INTERNALDATE "30-Sep-2026 09:16:00 +0800" '
                f'X-GM-MSGID {uid} X-GM-THRID {uid} BODY[] {{1}}'
            ).encode()
            return "OK", [(meta, RAW_EMAIL), b")"]
        raise AssertionError(command)


class IncrementalSyncTests(unittest.TestCase):
    def test_fetch_uses_uid_readonly_and_body_peek(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sync.db"
            with patch("app.config.DB_PATH", path), patch(
                "app.email_client.imaplib.IMAP4_SSL", FakeImap
            ), patch(
                "app.email_client.settings_store.get",
                side_effect=lambda key, default=None: {
                    "mail_mode": "real",
                    "mail_provider": "gmail",
                    "mail_user": "user@example.com",
                    "mail_password": "secret",
                }.get(key, default),
            ):
                db.init_db()
                batch = email_client.fetch_incremental()

                self.assertEqual(1, len(batch["emails"]))
                message = batch["emails"][0]
                self.assertEqual("101", message["source_uid"])
                self.assertEqual("<stable-message@example.com>", message["internet_message_id"])
                self.assertEqual("2026-09-30T09:16:00+08:00", message["received_at"])
                self.assertEqual("123456789", message["provider_message_id"])
                self.assertEqual("987654321", message["provider_thread_id"])
                self.assertEqual(
                    "https://mail.google.com/mail/u/0/#all/3ade68b1",
                    message["gmail_link"],
                )

                calls = FakeImap.instances[-1].calls
                self.assertIn(("select", "INBOX", True), calls)
                search_call = next(c for c in calls if c[:2] == ("uid", "search"))
                self.assertNotIn("SINCE", search_call)
                fetch_call = next(c for c in calls if c[:2] == ("uid", "fetch"))
                self.assertIn("BODY.PEEK[]", fetch_call[-1])
                self.assertNotIn("RFC822", fetch_call[-1])

    def test_limit_selects_newest_messages_and_reports_older_omissions(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sync.db"
            with patch("app.config.DB_PATH", path), patch(
                "app.email_client.imaplib.IMAP4_SSL", ManyMessagesImap
            ), patch(
                "app.email_client.settings_store.get",
                side_effect=lambda key, default=None: {
                    "mail_mode": "real", "mail_provider": "gmail",
                    "mail_user": "user@example.com", "mail_password": "secret",
                }.get(key, default),
            ):
                db.init_db()
                batch = email_client.fetch_incremental(limit=2)

                self.assertEqual(["104", "105"], [item["source_uid"] for item in batch["emails"]])
                self.assertEqual(3, batch["older_skipped"])
                self.assertEqual(0, batch["remaining"])


if __name__ == "__main__":
    unittest.main()
