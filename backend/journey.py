"""Functional HTTP rehearsal with synthetic accounts. Emits only sanitized proof metadata."""

import argparse
import hashlib

import rfc8785
import http.cookiejar
import json
import time
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPCookieProcessor, ProxyHandler, Request, build_opener

from flows import password
from issuance import mode
from proof import commitment
from store import connect
import registry


class Browser:
    def __init__(self, origin):
        target = urlsplit(origin)
        if (
            target.scheme != "http"
            or target.hostname not in ("127.0.0.1", "localhost")
            or target.username
            or target.password
            or target.path
            or target.query
            or target.fragment
        ):
            raise ValueError("Fixture sign-in requires a local loopback origin.")
        self.origin = origin
        self.client = build_opener(
            ProxyHandler({}),
            registry.NoRedirect(),
            HTTPCookieProcessor(http.cookiejar.CookieJar()),
        )

    def call(self, path, method="GET", data=None, expected=200):
        request = Request(
            self.origin + "/api/v1/" + path,
            method=method,
            headers={
                "Origin": self.origin,
                "X-Vertetify": "workspace",
                "Content-Type": "application/json",
            },
            data=None if data is None else json.dumps(data).encode(),
        )
        try:
            with self.client.open(request, timeout=35) as response:
                status, result = response.status, json.load(response)
        except HTTPError as exc:
            status, result = exc.code, None
        if status != expected:
            raise RuntimeError(f"{method} {path} expected {expected}, got {status}")
        return result

    def login(self, member):
        self.call("session", "POST", {"member": member, "password": password(member)})


def rehearse(origin):
    registrar, holder, guest, auditor = [Browser(origin) for _ in range(4)]
    guest.call("diplomas", expected=401)
    registrar.login("fixture-registrar")
    holder.login("fixture-holder")
    auditor.login("fixture-auditor")
    fields = dict(
        subject_display_name="Drita Demo",
        program_name="Shkencë Kompjuterike",
        award_name="BSc",
        award_date="2026-06-30",
    )
    key = registrar.call("diplomas", "POST", fields, 201)["id"]
    route = f"diplomas/{key}"
    for client in (holder, auditor):
        client.call(route + "/issue", "POST", expected=403)
    for _ in range(2):
        registrar.call(route + "/issue", "POST", expected=202)
    deadline = time.monotonic() + 75
    while time.monotonic() < deadline:
        item = next(i for i in registrar.call("diplomas")["items"] if i["id"] == key)
        if item["state"] == "issued":
            break
        if item["state"] == "review":
            raise RuntimeError(
                "Write requires reconciliation. Inspect the local operation before any new issuance."
            )
        time.sleep(1)
    else:
        raise RuntimeError("Timed out waiting for matched evidence.")
    existing_ids = {entry["id"] for entry in holder.call("shares")}
    share = holder.call(route + "/share", "POST", expected=201)
    created = [entry for entry in holder.call("shares") if entry["id"] not in existing_ids]
    if len(created) != 1 or set(created[0]) != {"id", "programme", "expires"}:
        raise RuntimeError("Unexpected share management projection.")
    management_path = "shares/" + created[0]["id"]
    result = guest.call("public/verify", "POST", share)
    expected = (
        "verified_local_chain" if mode() == "compellio-local" else "matched_simulator"
    )
    if (
        result["status"] != expected
        or result["source"] != mode()
        or set(result["diploma"])
        != {"issuer_id", "award_name", "award_date", "program_name"}
    ):
        raise RuntimeError("Public projection or proof source failed.")
    sibling = holder.call(route + "/share", "POST", expected=201)
    holder.call("session", "DELETE")
    holder.login("fixture-holder")
    guest.call(management_path, "DELETE", expected=401)
    auditor.call(management_path, "DELETE", expected=403)
    holder.call(management_path, "DELETE")
    if guest.call("public/verify", "POST", sibling)["status"] != expected:
        raise RuntimeError("Disabling one share affected another share.")
    holder.call("shares/disable", "POST", sibling)
    disabled = guest.call("public/verify", "POST", share)
    if disabled["status"] != "link_unavailable" or "diploma" in disabled:
        raise RuntimeError("Disabled share disclosed evidence.")
    registrar.call("session", "DELETE")
    registrar.call("diplomas", expected=401)
    evidence = dict(
        source=mode(),
        reference=item["reference"],
        credential_id=key,
        status=expected,
        checked_at=result["checked_at"],
        version=1,
    )
    if mode() == "compellio-local":
        with connect() as db:
            snapshot, nonce, profile = db.execute(
                "SELECT snapshot,nonce,registry_profile FROM diplomas WHERE id=%s", (key,)
            ).fetchone()
        evidence["institution"] = snapshot["issuer_id"]
        evidence["application_commitment"] = commitment(snapshot, nonce)
        record = registry.request(f"{registry.endpoints()[0]}/version/{item['reference']}:1")
        if not profile or record["data"].get("@context") != profile:
            raise RuntimeError("Fresh diploma did not reference its registered profile.")
        evidence["profile_tar"] = profile
        evidence["profile_checksum"] = registry.verify_record(profile, registry.PROFILE)
        evidence["version"] = record["version"]
        evidence["receipt"] = record.get("receipt")
        evidence["jcs_payload_sha256"] = hashlib.sha256(rfc8785.dumps(record["data"])).hexdigest()
        evidence["registry_checksum"] = record["checksum"][2:].lower()
        evidence["contract_checksum"] = registry.contract_checksum(registry.TAR.fullmatch(item["reference"])[1], 1)
        evidence["envelope_sha256"] = registry.verify(
            item["reference"], commitment(snapshot, nonce), profile
        )
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--origin", default="http://127.0.0.1:8000")
    rehearse(parser.parse_args().origin)
