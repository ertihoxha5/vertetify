import json
import os
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parent
MIGRATIONS = sorted((ROOT / "migrations").glob("*.sql"))


def check_mode():
    if os.getenv("APP_ENV", "local") != "local" or os.getenv("REGISTRY_MODE", "simulator") not in ("simulator","compellio-local"):
        raise RuntimeError("Select a supported local registry mode.")


def connect():
    check_mode()
    return psycopg.connect(connect_timeout=3)


def migrate(conn):
    conn.execute("SELECT pg_advisory_xact_lock(1736201)")
    conn.execute("CREATE TABLE IF NOT EXISTS schema_versions (version text PRIMARY KEY)")
    for path in MIGRATIONS:
        if not conn.execute("SELECT 1 FROM schema_versions WHERE version = %s", (path.stem,)).fetchone():
            conn.execute(path.read_text(encoding="utf-8"))
            conn.execute("INSERT INTO schema_versions VALUES (%s)", (path.stem,))


def seed(conn):
    for tenant in json.loads((ROOT / "fixtures.json").read_text(encoding="utf-8")):
        conn.execute("INSERT INTO tenants VALUES (%s, %s) ON CONFLICT DO NOTHING", (tenant["id"], tenant["name"]))
        for person, role in tenant["members"]:
            conn.execute("INSERT INTO members VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (tenant["id"], person, role))


def ready(conn):
    rows = conn.execute("SELECT version FROM schema_versions").fetchall()
    return {row[0] for row in rows} == {path.stem for path in MIGRATIONS}
