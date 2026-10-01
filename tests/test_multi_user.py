import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import auth, config, db, demo_seed, settings_store
from app.main import app
from app.tenant import workspace


class MultiUserTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        root = Path(self.tempdir.name)
        self.patches = [
            patch.object(config, "AUTH_DB_PATH", root / "accounts.db"),
            patch.object(config, "USER_DATA_DIR", root / "users"),
            patch.object(config, "DB_PATH", root / "legacy.db"),
            patch.object(config, "MULTI_USER_MODE", True),
            patch.object(config, "PUBLIC_DEMO", False),
            patch.object(config, "COOKIE_SECURE", False),
            patch.object(config, "APP_SECRET_KEY", "test-secret-key"),
            patch.object(config, "APP_ENCRYPTION_KEY", "test-encryption-key"),
        ]
        for item in self.patches:
            item.start()
        auth.init_db()
        app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)

    def tearDown(self):
        for item in reversed(self.patches):
            item.stop()
        self.tempdir.cleanup()

    def test_workspaces_and_credentials_are_isolated(self):
        first = auth.create_user("first@example.com", "correct-horse-1")
        second = auth.create_user("second@example.com", "correct-horse-2")

        with workspace(first["id"]):
            settings_store.set("deepseek_api_key", "sk-first-secret")
            demo_seed.seed()
            self.assertEqual(db.stats()["total"], 20)
            self.assertEqual(settings_store.get("deepseek_api_key"), "sk-first-secret")

        with workspace(second["id"]):
            self.assertEqual(db.stats()["total"], 0)
            self.assertIsNone(settings_store.get("deepseek_api_key"))

        first_db = Path(config.USER_DATA_DIR) / f"workspace-{first['id']}.db"
        raw = sqlite3.connect(first_db).execute(
            "SELECT value FROM settings WHERE key='deepseek_api_key'"
        ).fetchone()[0]
        self.assertTrue(raw.startswith("enc:v1:"))
        self.assertNotIn("sk-first-secret", raw)

    def test_hosted_routes_require_login_and_registration_creates_session(self):
        client = app.test_client()
        response = client.get("/dashboard")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

        with client.session_transaction() as session:
            session["csrf_token"] = "test-csrf"
        response = client.post(
            "/register",
            data={
                "csrf_token": "test-csrf",
                "email": "new@example.com",
                "password": "a-secure-passphrase",
                "confirm_password": "a-secure-passphrase",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/onboarding", response.headers["Location"])
        response = client.get("/onboarding")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"DeepSeek API Key", response.data)


if __name__ == "__main__":
    unittest.main()
