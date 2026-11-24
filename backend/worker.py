"""One-shot local worker for foundation setup and a synthetic registry rehearsal."""
import argparse
import hashlib
from secrets import token_hex

from store import connect, migrate, seed


def register(conn, tenant, digest):
    candidate = f"sim-{token_hex(12)}"
    row = conn.execute(
        """INSERT INTO simulator_receipts (tenant_id, reference, digest) VALUES (%s, %s, %s)
           ON CONFLICT (tenant_id, digest) DO UPDATE SET digest = EXCLUDED.digest
           RETURNING reference""", (tenant, candidate, digest)
    ).fetchone()
    return row[0]


def lookup(conn, tenant, reference):
    return conn.execute(
        "SELECT digest FROM simulator_receipts WHERE tenant_id = %s AND reference = %s",
        (tenant, reference),
    ).fetchone()


def rehearse(conn):
    digest = hashlib.sha256(b"vertetify/local/synthetic-fixture-01").hexdigest()
    reference = register(conn, "juniper", digest)
    if lookup(conn, "juniper", reference) != (digest,):
        raise RuntimeError("Local simulator readback failed")
    print(f"Local simulator rehearsal matched synthetic digest ({reference})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["setup", "seed", "rehearse"])
    action = parser.parse_args().action
    with connect() as db:
        if action == "setup":
            migrate(db)
        if action in ("setup", "seed"):
            seed(db)
        else:
            rehearse(db)
