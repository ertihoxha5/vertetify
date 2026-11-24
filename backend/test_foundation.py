import os
import unittest
from unittest.mock import patch

from main import live, readiness, workspace
from store import check_mode, connect, migrate, seed
from worker import lookup, register


class LocalModeTests(unittest.TestCase):
    def test_hosted_and_live_rejected(self):
        for config in ({"APP_ENV": "production"}, {"REGISTRY_MODE": "live"}):
            with self.subTest(config=config), patch.dict(os.environ, config):
                with self.assertRaises(RuntimeError):
                    check_mode()


class FoundationTests(unittest.TestCase):
    def test_repeatable_setup_and_scoped_readback(self):
        with connect() as db:
            try:
                for _ in range(2):
                    migrate(db)
                    seed(db)
                self.assertEqual(db.execute("SELECT count(*) FROM members").fetchone(), (3,))
                digest = "a" * 64
                ref = register(db, "juniper", digest)
                self.assertEqual(register(db, "juniper", digest), ref)
                self.assertEqual(lookup(db, "juniper", ref), (digest,))
                self.assertIsNone(lookup(db, "alder", ref))
            finally:
                db.rollback()

    def test_health_and_workspace(self):
        self.assertEqual(live()["status"], "alive")
        self.assertEqual(readiness()["status"], "ready")
        result = workspace()
        self.assertEqual(result.mode, "simulator")
        self.assertEqual(sorted(i.members for i in result.institutions), [1, 2])
