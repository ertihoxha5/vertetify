"""Durable issuance queue. One operator serializes outbound writes for this database."""

import os
from uuid import uuid4

from psycopg.types.json import Jsonb

import registry
from registry_profile import ensure_profile
import worker
from proof import commitment
from store import connect


def mode():
    return os.getenv("REGISTRY_MODE", "simulator")


def event(db, tenant, key, name):
    db.execute(
        "INSERT INTO diploma_events (tenant,diploma,event) VALUES (%s,%s,%s)",
        (tenant, key, name),
    )


def draft(db, tenant, holder, fields):
    key = uuid4()
    snapshot = dict(
        fields,
        credential_id=str(key),
        issuer_id=tenant,
        profile_version="vertetify-diploma-v1",
    )
    db.execute(
        "INSERT INTO diplomas (id,tenant,holder,mode,snapshot,nonce) VALUES (%s,%s,%s,%s,%s,%s)",
        (key, tenant, holder, mode(), Jsonb(snapshot), os.urandom(32)),
    )
    event(db, tenant, key, "drafted")
    return key


def evidence(db, tenant, ref, digest, profile=None):
    if mode() == "compellio-local":
        return registry.verify(ref, digest, profile)
    if worker.lookup(db, tenant, ref) != (digest,):
        raise registry.RegistryError("evidence_mismatch")
    return digest


def process():
    with connect() as db:
        # Session lock spans the committed dispatch marker and the external POST.
        if not db.execute("SELECT pg_try_advisory_lock(1736202)").fetchone()[0]:
            return "busy"
        db.execute(
            "UPDATE diplomas SET state='review' WHERE state='dispatching' AND mode=%s",
            (mode(),),
        )
        targets = db.execute(
            """SELECT id,tenant,snapshot,nonce,state,reference,registry_profile FROM diplomas
                                WHERE mode=%s AND state IN ('registered','queued') AND next_check<=now()
                                ORDER BY next_check,id LIMIT 16""",
            (mode(),),
        ).fetchall()
        db.commit()
        for key, tenant, snapshot, nonce, state, ref, profile in targets:
            digest = commitment(snapshot, nonce)
            if state == "queued":
                if mode() == "compellio-local":
                    try:
                        profile = ensure_profile(db)
                    except registry.RegistryError:
                        db.execute("UPDATE diplomas SET next_check=now()+interval '1 minute' WHERE id=%s", (key,))
                        db.commit()
                        continue
                db.execute(
                    "UPDATE diplomas SET state='dispatching',registry_profile=%s WHERE id=%s", (profile, key)
                )
                db.commit()
                try:
                    ref = (
                        registry.register(digest, profile)
                        if mode() == "compellio-local"
                        else worker.register(db, tenant, digest)
                    )
                except registry.RegistryError:
                    db.execute("UPDATE diplomas SET state='review' WHERE id=%s", (key,))
                    event(db, tenant, key, "write_requires_review")
                    db.commit()
                    continue
                db.execute(
                    "UPDATE diplomas SET state='registered',reference=%s WHERE id=%s",
                    (ref, key),
                )
                event(db, tenant, key, "receipt_saved")
                db.commit()
            try:
                matched = evidence(db, tenant, ref, digest, profile)
            except registry.RegistryError as exc:
                db.execute(
                    """UPDATE diplomas SET verify_attempts=verify_attempts+1,
                              next_check=now()+make_interval(secs => LEAST(300, 5*power(2,LEAST(verify_attempts,6)))::int),
                              state=CASE WHEN verify_attempts>=7 OR %s='evidence_mismatch' THEN 'review' ELSE 'registered' END
                              WHERE id=%s""",
                    (str(exc), key),
                )
                event(db, tenant, key, str(exc))
            else:
                db.execute("UPDATE diplomas SET state='issued',registry_checksum=%s WHERE id=%s",
                           (matched if mode() == "compellio-local" else None, key))
                event(db, tenant, key, "evidence_matched")
            db.commit()
        return "processed"
