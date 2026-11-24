"""Vertetify diploma commitment v1. All snapshot fields are private."""

import hashlib
import unicodedata

import rfc8785

FIELDS = {
    "award_date",
    "award_name",
    "credential_id",
    "issuer_id",
    "profile_version",
    "program_name",
    "subject_display_name",
}


def commitment(payload, nonce):
    if (
        set(payload) != FIELDS
        or len(nonce) != 32
        or payload["profile_version"] != "vertetify-diploma-v1"
    ):
        raise ValueError("Invalid diploma snapshot")
    normalized = {
        key: unicodedata.normalize("NFC", value) for key, value in payload.items()
    }
    return hashlib.sha256(
        b"vertetify:diploma:v1\x00" + nonce + rfc8785.dumps(normalized)
    ).hexdigest()
