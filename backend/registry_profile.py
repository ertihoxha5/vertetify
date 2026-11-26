"""Manage the single diploma profile on this deployment's local chain."""
import argparse

import registry
from store import connect, check_mode


def ensure_profile(db):
    # Caller holds the session-wide issuance lock across commits and network calls.
    row = db.execute("SELECT reference FROM registry_profile WHERE singleton").fetchone()
    if row:
        if row[0] is None:
            raise registry.RegistryError("profile_requires_review")
        registry.verify_record(row[0], registry.PROFILE)
        return row[0]
    registry.check_chain()
    db.execute("INSERT INTO registry_profile DEFAULT VALUES")
    db.commit()
    ref = registry.post_record(registry.PROFILE)
    db.execute("UPDATE registry_profile SET reference=%s WHERE singleton", (ref,))
    db.commit()
    registry.verify_record(ref, registry.PROFILE)
    return ref


if __name__ == "__main__":
    import os

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recover", help="Known profile TAR after an uncertain registration")
    args = parser.parse_args()
    check_mode()
    if os.getenv("REGISTRY_MODE") != "compellio-local":
        parser.error("Select compellio-local mode.")
    with connect() as db:
        db.execute("SELECT pg_advisory_lock(1736202)")
        if args.recover:
            registry.verify_record(args.recover, registry.PROFILE)
            if db.execute("UPDATE registry_profile SET reference=%s WHERE singleton AND reference IS NULL",
                          (args.recover,)).rowcount != 1:
                parser.error("Recovery requires an unresolved profile write.")
        print(ensure_profile(db))
