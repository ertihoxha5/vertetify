"""Attach a known TAR after a lost response, only after full read-only proof verification."""

import argparse
from uuid import UUID

from issuance import event, mode
from proof import commitment
import registry
from store import connect


def reconcile(key, reference):
    if mode() != "compellio-local":
        raise ValueError("Reconciliation requires the official local provider mode.")
    with connect() as db:
        db.execute("SELECT pg_advisory_xact_lock(1736202)")
        row = db.execute(
            """SELECT tenant,snapshot,nonce,reference FROM diplomas
                            WHERE id=%s AND mode=%s AND state='review' FOR UPDATE""",
            (key, mode()),
        ).fetchone()
        if not row or row[3] not in (None, reference):
            raise ValueError("A matching operation in review is required.")
        tenant, snapshot, nonce, _ = row
        registry.verify(reference, commitment(snapshot, nonce))
        db.execute(
            """UPDATE diplomas SET reference=%s,state='registered',verify_attempts=0,next_check=now()
                      WHERE id=%s""",
            (reference, key),
        )
        event(db, tenant, key, "reconciled_by_operator")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("credential_id", type=UUID)
    parser.add_argument("tar_id")
    args = parser.parse_args()
    reconcile(args.credential_id, args.tar_id)
    print(
        "Read-only reconciliation matched. The dispatcher will recheck before issuance."
    )
