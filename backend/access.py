"""Local institution onboarding and platform-wide operational aggregates."""

from datetime import UTC, datetime, timedelta
import secrets
from typing import Literal
from urllib.request import build_opener, ProxyHandler
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Request
from pydantic import Field

from flows import Input, Token, actor, keyed
from issuance import mode
import registry
from store import connect

router = APIRouter(prefix="/api/v1/access")


class Application(Input):
    name: str = Field(min_length=2, max_length=120)
    contact: str = Field(max_length=180, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Invitation(Input):
    role: Literal["registrar", "auditor", "holder"]


class StaffChange(Input):
    role: Literal["registrar", "auditor", "inactive"]


def audit(db, who, action, subject):
    db.execute(
        "INSERT INTO access_events(mode,actor,action,subject) VALUES (%s,%s,%s,%s)",
        (mode(), who, action, str(subject)),
    )


def invite(db, tenant, role, who):
    token = secrets.token_urlsafe(32)
    db.execute(
        "INSERT INTO access_invitations(digest,tenant,mode,role) VALUES (%s,%s,%s,%s)",
        (keyed("invite", token), tenant, mode(), role),
    )
    audit(db, who, "invite_" + role, tenant)
    return {"token": token}


@router.post("/requests", status_code=201)
def apply(data: Application):
    key = uuid4()
    with connect() as db:
        db.execute(
            "INSERT INTO institution_requests(id,name,contact,mode) VALUES (%s,%s,%s,%s)",
            (key, data.name, data.contact, mode()),
        )
    return {"id": key, "status": "pending"}


@router.get("/requests/{key}")
def status(key: UUID):
    with connect() as db:
        row = db.execute(
            "SELECT tenant IS NOT NULL FROM institution_requests WHERE id=%s AND mode=%s",
            (key, mode()),
        ).fetchone()
        if not row:
            raise HTTPException(404)
        return {"status": "approved" if row[0] else "pending"}


@router.post("/requests/{key}/approve")
def approve(key: UUID, req: Request):
    with connect() as db:
        _, who, _ = actor(db, req, "superadmin")
        row = db.execute(
            "SELECT name,tenant FROM institution_requests WHERE id=%s AND mode=%s FOR UPDATE",
            (key, mode()),
        ).fetchone()
        if not row:
            raise HTTPException(404)
        tenant = row[1]
        if tenant:
            db.execute(
                "SELECT digest FROM access_invitations WHERE tenant=%s AND role='admin' FOR UPDATE",
                (tenant,),
            ).fetchall()
            if db.execute(
                "SELECT 1 FROM members WHERE tenant_id=%s AND role='admin'", (tenant,)
            ).fetchone():
                raise HTTPException(409, "First administrator already activated.")
            db.execute(
                "UPDATE access_invitations SET used=true WHERE tenant=%s AND role='admin'",
                (tenant,),
            )
        else:
            tenant = str(uuid4())
            db.execute("INSERT INTO tenants(id,name) VALUES (%s,%s)", (tenant, row[0]))
            db.execute(
                "UPDATE institution_requests SET tenant=%s WHERE id=%s", (tenant, key)
            )
            audit(db, who, "approve", key)
        return invite(db, tenant, "admin", who)


@router.post("/activate", status_code=201)
def activate(data: Token):
    with connect() as db:
        row = db.execute(
            """UPDATE access_invitations SET used=true WHERE digest=%s AND mode=%s AND NOT used
                        AND expires>clock_timestamp() RETURNING tenant,role""",
            (keyed("invite", data.token), mode()),
        ).fetchone()
        if not row:
            raise HTTPException(410, "Invitation expired or already used.")
        tenant, role = row
        member = str(uuid4())
        secret = secrets.token_urlsafe(32)
        db.execute("INSERT INTO members VALUES (%s,%s,%s)", (tenant, member, role))
        db.execute(
            "INSERT INTO invited_logins VALUES (%s,%s,%s,%s)",
            (tenant, member, mode(), keyed("invited-login", secret)),
        )
        audit(db, member, "activate_" + role, tenant)
        return {"member": member, "password": secret}


@router.get("/team")
def team(req: Request):
    with connect() as db:
        tenant, _, _ = actor(db, req, "admin")
        return [
            {"member": m, "role": r}
            for m, r in db.execute(
                "SELECT id,role FROM members WHERE tenant_id=%s ORDER BY id", (tenant,)
            )
        ]


@router.post("/team/invite")
def invite_member(data: Invitation, req: Request):
    with connect() as db:
        tenant, who, _ = actor(db, req, "admin")
        return invite(db, tenant, data.role, who)


@router.post("/team/{member}/role")
def change_role(member: UUID, data: StaffChange, req: Request):
    with connect() as db:
        tenant, who, _ = actor(db, req, "admin")
        row = db.execute(
            """UPDATE members SET role=%s WHERE tenant_id=%s AND id=%s AND role IN ('registrar','auditor','inactive')
                          RETURNING id""",
            (data.role, tenant, str(member)),
        ).fetchone()
        if not row:
            raise HTTPException(404)
        db.execute(
            "DELETE FROM demo_sessions WHERE tenant=%s AND member=%s",
            (tenant, str(member)),
        )
        audit(db, who, "set_role_" + data.role, member)
        return {"role": data.role}


@router.get("/operations")
def operations(req: Request):
    today = datetime.now(UTC).date()
    start = today - timedelta(days=6)
    with connect() as db:
        actor(db, req, "superadmin")
        requests = [
            {"id": k, "name": n, "contact": c, "state": s}
            for k, n, c, s in db.execute(
                """
          SELECT r.id,r.name,r.contact,CASE WHEN r.tenant IS NULL THEN 'pending'
            WHEN EXISTS(SELECT 1 FROM members m WHERE m.tenant_id=r.tenant AND m.role='admin') THEN 'active'
            ELSE 'invited' END FROM institution_requests r WHERE mode=%s ORDER BY submitted DESC""",
                (mode(),),
            )
        ]
        issued = dict(
            db.execute(
                """SELECT (occurred AT TIME ZONE 'UTC')::date,count(DISTINCT e.diploma)
            FROM diploma_events e JOIN diplomas d ON d.id=e.diploma AND d.tenant=e.tenant
            WHERE d.mode=%s AND e.event='evidence_matched' AND (occurred AT TIME ZONE 'UTC')::date BETWEEN %s AND %s
            GROUP BY 1""",
                (mode(), start, today),
            ).fetchall()
        )
        outcomes = dict(
            db.execute(
                "SELECT outcome,sum(total)::bigint FROM verification_counts WHERE mode=%s AND day BETWEEN %s AND %s GROUP BY outcome",
                (mode(), start, today),
            ).fetchall()
        )
    return {
        "requests": requests,
        "mode": mode(),
        "start": start,
        "end": today,
        "issuance": {
            (start + timedelta(days=i)).isoformat(): issued.get(
                start + timedelta(days=i), 0
            )
            for i in range(7)
        },
        "outcomes": outcomes,
    }


@router.get("/health")
def provider_health(req: Request):
    with connect() as db:
        actor(db, req, "superadmin")
    result = {"Registry": "Simulator selected", "Chain": "Simulator selected"}
    if mode() == "compellio-local":
        try:
            swagger = (
                registry.endpoints()[0].split("/api/")[0] + "/swagger/v1/swagger.json"
            )
            with build_opener(ProxyHandler({}), registry.NoRedirect()).open(
                swagger, timeout=3
            ) as response:
                result["Registry"] = (
                    "Swagger reachable" if response.status == 200 else "Unavailable"
                )
        except OSError:
            result["Registry"] = "Unavailable"
        try:
            registry.check_chain()
            result["Chain"] = "Chain 31337 reachable"
        except registry.RegistryError:
            result["Chain"] = "Unavailable or unexpected chain"
    return result
