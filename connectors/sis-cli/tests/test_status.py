"""Offline regressions: synthetic cookies only; no user config or requests."""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from siscli import cli, config
from siscli.transport import Transport


class StatusTests(unittest.TestCase):
    def run_status(self, jar=None, cfg=None, env=None):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "session.json"
            if jar is not None:
                path.write_text(json.dumps(jar), encoding="utf-8")
            with patch.dict(os.environ, env or {}, clear=True), \
                    patch.object(config, "session_path", return_value=path):
                transport = Transport()
                sis = SimpleNamespace(transport=transport, cfg=cfg or {})
                before = path.read_bytes() if path.exists() else None
                with patch.object(transport._sess, "request", side_effect=AssertionError("network forbidden")), \
                        patch.object(cli, "Sis", return_value=sis), \
                        contextlib.redirect_stdout(io.StringIO()) as output:
                    result = cli.main(["status"])
                self.assertEqual(result, 0)
                self.assertEqual(before, path.read_bytes() if path.exists() else None)
                text = output.getvalue()
                for secret in ("test-secret", "test-token", "test-user"):
                    self.assertNotIn(secret, text)
                data = json.loads(text)
                self.assertIsNone(data["authenticated"])
                self.assertFalse(data["authentication_checked"])
                self.assertIsNone(data["reachable"])
                self.assertFalse(data["network_checked"])
                return data

    def test_missing_session_and_credentials_does_not_exit_or_login(self):
        data = self.run_status()
        self.assertEqual(data["session"], "absent_or_unusable")
        self.assertEqual(data["relogin"], "blocked_missing_credentials")

    def test_cached_token_never_implies_authenticated(self):
        data = self.run_status([{"name": "PS_TOKEN", "value": "test-token"}])
        self.assertEqual(data["session"], "cached_unverified")
        self.assertEqual(data["relogin"], "blocked_missing_credentials")

    def test_stored_credentials_are_not_used_to_login(self):
        data = self.run_status(cfg={"username": "test-user", "password": "test-secret"})
        self.assertEqual(data["relogin"], "credentials_available_unverified")

    def test_environment_credentials_follow_resolver(self):
        data = self.run_status(env={config.ENV_USERNAME: "test-user", config.ENV_PASSWORD: "test-secret"})
        self.assertEqual(data["relogin"], "credentials_available_unverified")

    def test_partial_credentials_block_relogin(self):
        data = self.run_status(cfg={"username": "test-user"})
        self.assertEqual(data["relogin"], "blocked_missing_credentials")

    def test_non_token_jar_is_not_authenticated(self):
        data = self.run_status([{"name": "PS_DEVICEFEATURES", "value": "test-token"}])
        self.assertEqual(data["session"], "absent_or_unusable")

    def test_malformed_cookie_entries_are_reported_without_details(self):
        data = self.run_status([{"value": "test-secret"}])
        self.assertEqual(data["session"], "unreadable")

    def test_unreadable_session_does_not_hide_credential_availability(self):
        with patch.object(Transport, "load_session", side_effect=OSError("test-secret")):
            data = self.run_status(cfg={"username": "test-user", "password": "test-secret"})
        self.assertEqual(data["session"], "unreadable")
        self.assertEqual(data["relogin"], "credentials_available_unverified")


if __name__ == "__main__":
    unittest.main()
