"""Controlled local failure and concurrency cases, using an isolated Postgres fixture."""

import os
from concurrent.futures import ThreadPoolExecutor
import unittest
from unittest.mock import patch

import registry
from issuance import draft, process
from proof import commitment
from reconcile import reconcile
from store import connect
from test_proof import VECTOR


@unittest.skipUnless(
    os.getenv("VERTETIFY_ISOLATED_TEST") == "1", "requires the disposable smoke project"
)
class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.config = patch.dict(os.environ, REGISTRY_MODE="compellio-local")
        self.config.start()
        self.addCleanup(self.config.stop)
        with connect() as db:
            self.key = draft(db, "juniper", "fixture-holder", VECTOR)
            db.execute("UPDATE diplomas SET state='queued' WHERE id=%s", (self.key,))
        self.ref = "urn:tar:eip155.31337:" + "b" * 40

    def state(self):
        with connect() as db:
            return db.execute(
                "SELECT state,reference FROM diplomas WHERE id=%s", (self.key,)
            ).fetchone()

    def test_uncertain_write_requires_read_only_reconciliation(self):
        with patch(
            "registry.register",
            side_effect=registry.RegistryError("registry_unavailable"),
        ) as post:
            process()
            process()
            post.assert_called_once()
        self.assertEqual(self.state(), ("review", None))
        with patch(
            "registry.verify", side_effect=registry.RegistryError("evidence_mismatch")
        ):
            with self.assertRaises(registry.RegistryError):
                reconcile(self.key, self.ref)
        self.assertEqual(self.state(), ("review", None))
        with (
            patch("registry.verify", return_value="matched"),
            patch("registry.register") as post,
        ):
            reconcile(self.key, self.ref)
            process()
            post.assert_not_called()
        self.assertEqual(self.state(), ("issued", self.ref))

    def test_two_dispatchers_send_one_write(self):
        with (
            patch("registry.register", return_value=self.ref) as post,
            patch("registry.verify", return_value="matched"),
        ):
            with ThreadPoolExecutor(2) as pool:
                list(pool.map(lambda _: process(), range(2)))
            post.assert_called_once()
        self.assertEqual(self.state(), ("issued", self.ref))
        with connect() as db:
            snapshot, nonce = db.execute(
                "SELECT snapshot,nonce FROM diplomas WHERE id=%s", (self.key,)
            ).fetchone()
        self.assertEqual(post.call_args.args, (commitment(snapshot, nonce),))
