"""Real HTTP checks confined to the disposable smoke project."""

import os
import unittest

from journey import Browser
from store import connect


@unittest.skipUnless(
    os.getenv("VERTETIFY_ISOLATED_TEST") == "1", "requires disposable stack"
)
class AccessJourney(unittest.TestCase):
    def test_approval_to_scoped_staff(self):
        def browser():
            return Browser("http://127.0.0.1:8000")

        guest, operator, juniper = browser(), browser(), browser()
        operator.login("fixture-operator")
        juniper.login("fixture-registrar")

        def redeem(invitation):
            credentials = guest.call("access/activate", "POST", invitation, 201)
            guest.call("access/activate", "POST", invitation, 410)
            account = browser()
            account.call("session", "POST", credentials)
            return account, credentials

        application = guest.call(
            "access/requests",
            "POST",
            {"name": "Synthetic Northern College", "contact": "admin@example.test"},
            201,
        )
        path = "access/requests/" + application["id"]
        self.assertEqual(guest.call(path)["status"], "pending")
        guest.call(
            "session",
            "POST",
            {"member": "admin@example.test", "password": "synthetic"},
            401,
        )
        fields = {
            "subject_display_name": "Synthetic graduate",
            "award_name": "BSc",
            "program_name": "Computing",
            "award_date": "2026-06-30",
        }
        guest.call("diplomas", "POST", fields, 401)
        juniper.call(path + "/approve", "POST", expected=403)
        guest.call("access/operations", expected=401)
        admin, _ = redeem(operator.call(path + "/approve", "POST"))
        operator.call(path + "/approve", "POST", expected=409)
        self.assertEqual(guest.call(path)["status"], "approved")
        operator.call("diplomas", "POST", fields, 403)
        self.assertEqual(operator.call("diplomas")["items"], [])
        staff, credentials = redeem(
            admin.call("access/team/invite", "POST", {"role": "registrar"})
        )
        holder, graduate = redeem(
            admin.call("access/team/invite", "POST", {"role": "holder"})
        )
        self.assertEqual(holder.call("diplomas")["items"], [])
        key = staff.call(
            "diplomas", "POST", dict(fields, holder=graduate["member"]), 201
        )["id"]
        self.assertEqual([r["id"] for r in staff.call("diplomas")["items"]], [key])
        self.assertNotIn(key, [r["id"] for r in juniper.call("diplomas")["items"]])
        juniper.call("diplomas/" + key + "/issue", "POST", expected=404)
        staff.call("diplomas", "POST", dict(fields, holder="fixture-holder"), 409)
        staff.call("access/operations", expected=403)
        admin.call(
            "access/team/" + credentials["member"] + "/role",
            "POST",
            {"role": "auditor"},
        )
        staff.call("diplomas", expected=401)
        staff.call("session", "POST", credentials)
        staff.call("diplomas", "POST", fields, 403)
        self.assertEqual(
            operator.call("access/operations")["requests"][0]["state"], "active"
        )
        self.assertEqual(operator.call("access/health")["Chain"], "Simulator selected")
        with connect() as db:
            actions = {r[0] for r in db.execute("SELECT action FROM access_events")}
            self.assertTrue(
                {
                    "approve",
                    "activate_admin",
                    "invite_registrar",
                    "activate_registrar",
                    "set_role_auditor",
                }
                <= actions
            )
