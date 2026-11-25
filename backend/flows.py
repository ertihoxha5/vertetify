"""Local-only synthetic registrar, holder and anonymous verification routes."""

from datetime import UTC, date, datetime
import hmac
import os
import re
import secrets
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field

from issuance import draft, evidence, event, mode
from proof import commitment
from registry import RegistryError
from store import connect

router = APIRouter(prefix="/api/v1")


def keyed(label, value):
    return hmac.digest(
        os.environ["PGPASSWORD"].encode(),
        f"{mode()}/{label}/{value}".encode(),
        "sha256",
    )


def password(member):
    return keyed("demo-login", member).hex()[:32]


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Login(Input):
    member: str = Field(max_length=80)
    password: str = Field(max_length=100)


class Academic(Input):
    subject_display_name: str = Field(min_length=1, max_length=80)
    program_name: str = Field(min_length=1, max_length=120)
    award_name: str = Field(min_length=1, max_length=80)
    award_date: date


class Token(Input):
    token: str = Field(pattern=r"^[A-Za-z0-9_-]{43}$")


def actor(db, req, role=None):
    token = req.cookies.get("vertetify_session", "")
    row = db.execute(
        """UPDATE demo_sessions s SET touched=now() FROM members m
        WHERE s.digest=%s AND m.tenant_id=s.tenant AND m.id=s.member AND m.role=s.role
        AND s.started>now()-interval '8 hours' AND s.touched>now()-interval '30 minutes'
        RETURNING s.tenant,s.member,s.role""",
        (keyed("session", token),),
    ).fetchone()
    if not row:
        raise HTTPException(401, "Sign in to the local workspace.")
    if role and role != row[2]:
        raise HTTPException(403, "Role cannot perform this action.")
    return row


@router.post("/session")
def login(data: Login, req: Request, response: Response):
    with connect() as db:
        row = db.execute(
            "SELECT tenant_id,id,role FROM members WHERE id=%s", (data.member,)
        ).fetchall()
        if len(row) != 1 or not hmac.compare_digest(
            password(data.member).encode(), data.password.encode()
        ):
            raise HTTPException(401, "Sign-in failed.")
        tenant, member, role = row[0]
        token = secrets.token_urlsafe(32)
        db.execute(
            "DELETE FROM demo_sessions WHERE digest=%s",
            (keyed("session", req.cookies.get("vertetify_session", "")),),
        )
        db.execute(
            "INSERT INTO demo_sessions (digest,tenant,member,role) VALUES (%s,%s,%s,%s)",
            (keyed("session", token), tenant, member, role),
        )
        response.set_cookie(
            "vertetify_session", token, httponly=True, samesite="strict", max_age=28800
        )
        return {"role": role}


@router.delete("/session")
def logout(req: Request, response: Response):
    with connect() as db:
        db.execute(
            "DELETE FROM demo_sessions WHERE digest=%s",
            (keyed("session", req.cookies.get("vertetify_session", "")),),
        )
    response.delete_cookie("vertetify_session")
    return {"status": "signed_out"}


@router.get("/diplomas")
def diplomas(req: Request):
    with connect() as db:
        tenant, member, role = actor(db, req)
        rows = db.execute(
            """SELECT id,snapshot,state,reference FROM diplomas WHERE tenant=%s AND mode=%s
            AND (%s='registrar' OR (%s='holder' AND holder=%s AND state='issued')) ORDER BY id""",
            (tenant, mode(), role, role, member),
        ).fetchall()
        return {
            "role": role,
            "items": [
                {"id": k, "snapshot": p, "state": s, "reference": r}
                for k, p, s, r in rows
            ],
        }


@router.post("/diplomas", status_code=201)
def create_draft(data: Academic, req: Request):
    with connect() as db:
        tenant, _, _ = actor(db, req, "registrar")
        # The local demo has one seeded recipient in the registrar's institution.
        holder = db.execute(
            "SELECT id FROM members WHERE tenant_id=%s AND role='holder' ORDER BY id LIMIT 1",
            (tenant,),
        ).fetchone()
        if not holder:
            raise HTTPException(409, "No fixture recipient.")
        return {"id": draft(db, tenant, holder[0], data.model_dump(mode="json"))}


@router.post("/diplomas/{key}/issue", status_code=202)
def issue(key: UUID, req: Request):
    with connect() as db:
        tenant, _, _ = actor(db, req, "registrar")
        row = db.execute(
            "SELECT state FROM diplomas WHERE id=%s AND tenant=%s AND mode=%s FOR UPDATE",
            (key, tenant, mode()),
        ).fetchone()
        if not row:
            raise HTTPException(404)
        if row[0] == "draft":
            db.execute("UPDATE diplomas SET state='queued' WHERE id=%s", (key,))
            event(db, tenant, key, "queued")
        return {"state": "queued" if row[0] == "draft" else row[0]}


@router.post("/diplomas/{key}/share", status_code=201)
def share(key: UUID, req: Request):
    with connect() as db:
        tenant, member, _ = actor(db, req, "holder")
        if not db.execute(
            "SELECT 1 FROM diplomas WHERE tenant=%s AND id=%s AND holder=%s AND mode=%s AND state='issued'",
            (tenant, key, member, mode()),
        ).fetchone():
            raise HTTPException(404)
        token = secrets.token_urlsafe(32)
        db.execute(
            "INSERT INTO diploma_shares (digest,tenant,diploma) VALUES (%s,%s,%s)",
            (keyed("share", token), tenant, key),
        )
        event(db, tenant, key, "share_created")
        return {"token": token}


@router.get("/shares")
def active_shares(req: Request):
    with connect() as db:
        tenant, member, _ = actor(db, req, "holder")
        rows = db.execute(
            """SELECT s.management_id, s.expires, d.snapshot->>'program_name'
               FROM diploma_shares s JOIN diplomas d ON (s.tenant,s.diploma)=(d.tenant,d.id)
               WHERE s.tenant=%s AND d.holder=%s AND d.mode=%s AND d.state='issued'
                 AND NOT s.disabled AND s.expires>now()
               ORDER BY s.expires DESC, s.management_id""", (tenant, member, mode())
        ).fetchall()
        return [{"id": key, "expires": expires, "programme": programme} for key, expires, programme in rows]


def disable_owned_share(req: Request, *, digest: bytes | None = None, management_id: UUID | None = None):
    with connect() as db:
        tenant, member, _ = actor(db, req, "holder")
        row = db.execute(
            """SELECT d.id,s.digest,s.disabled FROM diploma_shares s
               JOIN diplomas d ON (s.tenant,s.diploma)=(d.tenant,d.id)
               WHERE (s.digest=%s OR s.management_id=%s)
                 AND s.tenant=%s AND d.holder=%s AND d.mode=%s FOR UPDATE OF s""",
            (digest, management_id, tenant, member, mode()),
        ).fetchone()
        if not row:
            raise HTTPException(404)
        if not row[2]:
            db.execute("UPDATE diploma_shares SET disabled=true WHERE digest=%s", (row[1],))
            event(db, tenant, row[0], "share_disabled")
    return {"status": "disabled"}


@router.post("/shares/disable")
def disable(data: Token, req: Request):
    return disable_owned_share(req, digest=keyed("share", data.token))


@router.delete("/shares/{management_id}")
def disable_by_id(management_id: UUID, req: Request):
    return disable_owned_share(req, management_id=management_id)


@router.post("/public/verify")
def public_verify(data: Token):
    result = {
        "source": mode(),
        "checked_at": datetime.now(UTC).isoformat(),
        "status": "link_unavailable",
    }
    with connect() as db:
        query = """SELECT d.snapshot,d.nonce,d.reference,d.tenant FROM diploma_shares s JOIN diplomas d
            ON d.id=s.diploma AND d.tenant=s.tenant WHERE s.digest=%s AND s.expires>clock_timestamp()
            AND NOT s.disabled AND d.state='issued' AND d.mode=%s"""
        params = (keyed("share", data.token), mode())
        row = db.execute(query, params).fetchone()
        if not row:
            return result
        snapshot, nonce, ref, tenant = row
        try:
            evidence(db, tenant, ref, commitment(snapshot, nonce))
        except RegistryError as exc:
            result["status"] = (
                str(exc)
                if re.fullmatch("evidence_mismatch|not_found", str(exc))
                else "proof_unavailable"
            )
            return result
        if not db.execute(query, params).fetchone():
            return result
        result.update(
            status="verified_local_chain"
            if mode() == "compellio-local"
            else "matched_simulator",
            diploma={
                k: snapshot[k]
                for k in ("award_name", "program_name", "award_date", "issuer_id")
            },
        )
        return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Display one local fixture sign-in password."
    )
    parser.add_argument(
        "member", choices=["fixture-registrar", "fixture-holder", "fixture-auditor"]
    )
    print(password(parser.parse_args().member))
