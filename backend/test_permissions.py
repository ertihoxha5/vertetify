import os
import unittest

from fastapi import HTTPException
from starlette.requests import Request

from flows import actor, keyed
from issuance import draft
from store import connect
from test_proof import VECTOR


@unittest.skipUnless(
    os.getenv("VERTETIFY_ISOLATED_TEST") == "1", "requires disposable PostgreSQL"
)
class SessionPolicyTests(unittest.TestCase):
    def test_session_timeout_and_membership_change(self):
        request = Request(
            {
                "type": "http",
                "headers": [(b"cookie", b"vertetify_session=session-fixture")],
            }
        )
        with connect() as db:
            try:
                db.execute(
                    """INSERT INTO demo_sessions (digest,tenant,member,role)
                              VALUES (%s,'juniper','fixture-registrar','registrar')""",
                    (keyed("session", "session-fixture"),),
                )
                self.assertEqual(actor(db, request, "registrar")[0], "juniper")
                db.execute(
                    "UPDATE members SET role='holder' WHERE tenant_id='juniper' AND id='fixture-registrar'"
                )
                with self.assertRaises(HTTPException) as changed:
                    actor(db, request)
                self.assertEqual(changed.exception.status_code, 401)
                db.execute(
                    "UPDATE members SET role='registrar' WHERE tenant_id='juniper' AND id='fixture-registrar'"
                )
                db.execute(
                    "UPDATE demo_sessions SET touched=now()-interval '31 minutes' WHERE digest=%s",
                    (keyed("session", "session-fixture"),),
                )
                with self.assertRaises(HTTPException) as expired:
                    actor(db, request)
                self.assertEqual(expired.exception.status_code, 401)
            finally:
                db.rollback()

    def test_cross_tenant_holder_constraint(self):
        import psycopg

        with connect() as db:
            with self.assertRaises(psycopg.errors.ForeignKeyViolation):
                draft(db, "alder", "fixture-holder", VECTOR)
            db.rollback()
