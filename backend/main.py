import os
from pathlib import Path
from typing import Literal

import psycopg
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from store import check_mode, connect, ready
from flows import router
from issuance import mode

check_mode()
app = FastAPI(title="Vertetify local credentials")
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost","127.0.0.1","testserver"])
app.include_router(router)


@app.middleware("http")
async def local_browser_policy(req: Request, call_next):
    if req.method not in ("GET","HEAD","OPTIONS") and (
        req.headers.get("origin") != str(req.base_url).rstrip("/") or req.headers.get("x-vertetify") != "workspace"
    ):
        return JSONResponse({"detail":"Same-origin workspace request required."},status_code=403)
    response = await call_next(req)
    response.headers.update({"Cache-Control":"no-store","Referrer-Policy":"no-referrer",
                             "X-Content-Type-Options":"nosniff","X-Frame-Options":"DENY"})
    return response


class Institution(BaseModel):
    name: str
    members: int


class Workspace(BaseModel):
    mode: Literal["simulator","compellio-local"]
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
    return Workspace(mode=mode(), institutions=[Institution(name=n, members=c) for n, c in rows])


static = Path(os.getenv("WEB_DIST", Path(__file__).resolve().parents[1] / "frontend/dist"))
if static.is_dir():
    @app.get("/verify", include_in_schema=False)
    def verify_page():
        return FileResponse(static / "index.html")

    app.mount("/", StaticFiles(directory=static, html=True), name="web")
