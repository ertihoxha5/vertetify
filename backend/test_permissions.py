import os
import unittest

from contextlib import nullcontext
from unittest.mock import patch

from fastapi import HTTPException
from starlette.requests import Request

from flows import Token, actor, diplomas, keyed, public_verify, share
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

    def test_scoped_records_and_public_failures(self):
        from registry import RegistryError

        def session(db, name, role, tenant):
            db.execute(
                "INSERT INTO demo_sessions(digest,tenant,member,role) VALUES (%s,%s,%s,%s)",
                (keyed("session", name), tenant, name, role),
            )
            return Request(
                {
                    "type": "http",
                    "headers": [(b"cookie", ("vertetify_session=" + name).encode())],
                }
            )

        with connect() as db, patch("flows.connect", return_value=nullcontext(db)):
            try:
                holder = session(db, "fixture-holder", "holder", "juniper")
                auditor = session(db, "fixture-auditor", "auditor", "alder")
                registrar = session(db, "fixture-registrar", "registrar", "juniper")
                db.execute(
                    "INSERT INTO members(tenant_id,id,role) VALUES ('juniper','another-holder','holder')"
                )
                mine = draft(db, "juniper", "fixture-holder", VECTOR)
                other = draft(db, "juniper", "another-holder", VECTOR)
                for state in ("queued", "dispatching", "registered", "issued"):
                    db.execute(
                        "UPDATE diplomas SET state=%s,reference='fixture' WHERE id IN (%s,%s)",
                        (state, mine, other),
                    )
                self.assertIn(other, [i["id"] for i in diplomas(registrar)["items"]])
                self.assertNotIn(other, [i["id"] for i in diplomas(holder)["items"]])
                self.assertEqual(diplomas(auditor)["items"], [])
                with self.assertRaises(HTTPException) as denied:
                    share(other, holder)
                self.assertEqual(denied.exception.status_code, 404)
                token = Token(**share(mine, holder))
                for failure, expected in [
                    ("registry_unavailable", "proof_unavailable"),
                    ("evidence_mismatch", "evidence_mismatch"),
                ]:
                    with patch("flows.evidence", side_effect=RegistryError(failure)):
                        value = public_verify(token)
                        self.assertEqual(value["status"], expected)
                        self.assertNotIn("diploma", value)
                db.execute(
                    "UPDATE diploma_shares SET expires=now()-interval '1 second' WHERE diploma=%s",
                    (mine,),
                )
                self.assertEqual(public_verify(token)["status"], "link_unavailable")
                db.execute(
                    "UPDATE diploma_shares SET expires=now()+interval '1 day' WHERE diploma=%s",
                    (mine,),
                )
                pending = draft(db, "juniper", "fixture-holder", VECTOR)
                db.execute("UPDATE diplomas SET state='queued' WHERE id=%s", (pending,))
                db.execute(
                    "UPDATE diploma_shares SET diploma=%s WHERE diploma=%s",
                    (pending, mine),
                )
                self.assertNotIn("diploma", public_verify(token))
            finally:
                db.rollback()
