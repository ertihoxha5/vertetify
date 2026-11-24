import os
from pathlib import Path
from typing import Literal

import psycopg
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from store import check_mode, connect, ready

check_mode()
app = FastAPI(title="Vertetify local simulator")


class Institution(BaseModel):
    name: str
    members: int


class Workspace(BaseModel):
    mode: Literal["simulator"]
    institutions: list[Institution]


@app.get("/api/health/live")
def live():
    return {"status": "alive"}


@app.get("/api/health/ready")
def readiness():
    try:
        with connect() as db:
            if ready(db):
                return {"status": "ready"}
    except psycopg.Error:
        pass
    raise HTTPException(503, "Database unavailable or migration pending")


@app.get("/api/workspace", response_model=Workspace)
def workspace():
    try:
        with connect() as db:
            rows = db.execute(
                """SELECT t.name, count(m.id) FROM tenants t LEFT JOIN members m
                   ON t.id = m.tenant_id GROUP BY t.id, t.name ORDER BY t.name"""
            ).fetchall()
    except psycopg.Error:
        raise HTTPException(503, "Workspace unavailable") from None
    return Workspace(mode="simulator", institutions=[Institution(name=n, members=c) for n, c in rows])


static = Path(os.getenv("WEB_DIST", Path(__file__).resolve().parents[1] / "frontend/dist"))
if static.is_dir():
    app.mount("/", StaticFiles(directory=static, html=True), name="web")
