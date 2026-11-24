"""Adapter for the organizer's local DCAP.Web and EVM chain. No write retries."""

import hashlib
import json
import os
import re
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

import rfc8785
from Crypto.Hash import keccak

TAR = re.compile(r"urn:tar:eip155\.31337:(?:0x)?([0-9a-fA-F]{40})")
DIGEST = re.compile(r"[0-9a-f]{64}")


class RegistryError(Exception):
    """Safe outcome suitable for a local operation record."""


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None


def request(url, body=None, expected=200):
    data = None if body is None else rfc8785.dumps(body)
    req = Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    try:
        with build_opener(ProxyHandler({}), NoRedirect()).open(
            req, timeout=8
        ) as response:
            if response.status != expected:
                raise RegistryError("unexpected_response")
            raw = response.read(65537)
            if len(raw) > 65536:
                raise RegistryError("invalid_evidence")
            result = json.loads(raw)
            if not isinstance(result, dict):
                raise RegistryError("invalid_evidence")
            return result
    except HTTPError as exc:
        raise RegistryError(
            "not_found" if exc.code == 404 else "registry_unavailable"
        ) from None
    except (OSError, URLError, ValueError, HTTPException):
        raise RegistryError("registry_unavailable") from None


def endpoints():
    if os.getenv("REGISTRY_NETWORK", "loopback") == "compose":
        return "http://registry-api:8080/api/v1/TAR", "http://ethereum:8545"
    return "http://127.0.0.1:18660/api/v1/TAR", "http://127.0.0.1:18545"


def envelope(digest):
    if not DIGEST.fullmatch(digest):
        raise ValueError("Expected diploma commitment")
    return {"type": "VertetifyDiplomaCommitmentV1", "commitment": digest}


def rpc(method, params):
    response = request(
        endpoints()[1], {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    )
    if (
        response.get("id") != 1
        or not isinstance(response.get("result"), str)
        or "error" in response
    ):
        raise RegistryError("chain_unavailable")
    return response["result"]


def check_chain():
    if rpc("eth_chainId", []) != hex(31337):
        raise RegistryError("wrong_chain")


def register(digest):
    check_chain()
    result = request(endpoints()[0], envelope(digest), 201)
    ref = result.get("id")
    if not isinstance(ref, str) or not TAR.fullmatch(ref):
        raise RegistryError("invalid_evidence")
    return ref


def contract_checksum(address, version):
    # The local deployment numbers REST versions from 1 and contract slots from 0.
    block = rpc("eth_blockNumber", [])
    total_selector = keccak.new(digest_bits=256, data=b"totalVersions()").hexdigest()[
        :8
    ]
    count = rpc(
        "eth_call", [{"to": "0x" + address, "data": "0x" + total_selector}, block]
    )
    if count.lower() != "0x" + format(version, "064x"):
        raise RegistryError("evidence_mismatch")
    selector = keccak.new(digest_bits=256, data=b"getChecksum(uint256)").hexdigest()[:8]
    raw = rpc(
        "eth_call",
        [
            {
                "to": "0x" + address,
                "data": "0x" + selector + format(version - 1, "064x"),
            },
            block,
        ],
    )
    if not re.fullmatch(r"0x[0-9a-fA-F]{64}", raw):
        raise RegistryError("invalid_chain_evidence")
    return raw[2:].lower()


def verify(reference, digest):
    match = TAR.fullmatch(reference)
    if not match:
        raise RegistryError("invalid_reference")
    check_chain()
    payload = envelope(digest)
    expected = hashlib.sha256(rfc8785.dumps(payload)).hexdigest()
    latest = request(f"{endpoints()[0]}/{reference}")
    historical = request(f"{endpoints()[0]}/version/{reference}:1")
    for record in (latest, historical):
        if (
            record.get("id") != reference
            or type(record.get("version")) is not int
            or record["version"] != 1
            or record.get("data") != payload
            or str(record.get("checksum")).lower() != "0x" + expected
        ):
            raise RegistryError("evidence_mismatch")
    if contract_checksum(match[1], 1) != expected:
        raise RegistryError("evidence_mismatch")
    return expected
