#!/usr/bin/env python3
"""Materialize ONDC portal keys.json into PEM + public_metadata (gitignored).

Does not print private key material. Safe to run in agent sessions.

Usage:
  python3 scripts/ondc_materialize_portal_keys.py
  python3 scripts/ondc_materialize_portal_keys.py --role buyer
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, x25519

ROOT = Path(__file__).resolve().parents[1]
PORTAL = ROOT / "aadharchain/gateway/.local/ondc-sandbox/portal-download"

# Portal UI unique_key_id (not inside keys.json)
UK_IDS = {
    "buyer": "1aee68ad-bc2a-4fc4-b233-7e14c6abba9b",
    "seller": "baf58086-7024-438a-becf-4cfa056ec8d9",
}
SUBSCRIBERS = {
    "buyer": "ondcbuyer.aadharcha.in",
    "seller": "ondcseller.aadharcha.in",
}


def _fp16(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def _load_signing_private(b64: str):
    raw = base64.b64decode(b64)
    if len(raw) == 32:
        return ed25519.Ed25519PrivateKey.from_private_bytes(raw)
    if len(raw) == 64:
        return ed25519.Ed25519PrivateKey.from_private_bytes(raw[:32])
    return serialization.load_der_private_key(raw, password=None)


def _load_encryption_private(b64: str):
    raw = base64.b64decode(b64)
    if len(raw) == 32:
        return x25519.X25519PrivateKey.from_private_bytes(raw)
    return serialization.load_der_private_key(raw, password=None)


def materialize(role: str) -> dict:
    role = role.lower().strip()
    src = PORTAL / role / "keys.json"
    if not src.is_file():
        raise FileNotFoundError(f"missing {src}")
    data = json.loads(src.read_text(encoding="utf-8"))
    required = (
        "signing_private_key",
        "signing_public_key",
        "encryption_private_key",
        "encryption_public_key",
    )
    for k in required:
        if k not in data or not isinstance(data[k], str):
            raise ValueError(f"{src}: missing {k}")

    signing = _load_signing_private(data["signing_private_key"])
    encryption = _load_encryption_private(data["encryption_private_key"])

    signing_pub = base64.b64encode(
        signing.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
    ).decode("ascii")
    enc_pub = base64.b64encode(
        encryption.public_key().public_bytes(
            serialization.Encoding.DER,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    ).decode("ascii")
    if signing_pub != data["signing_public_key"]:
        raise ValueError(f"{role}: signing public mismatch after load")
    if enc_pub != data["encryption_public_key"]:
        raise ValueError(f"{role}: encryption public mismatch after load")

    out_dir = PORTAL / role
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "signing_private.pem").write_bytes(
        signing.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    (out_dir / "encryption_private.pem").write_bytes(
        encryption.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )

    uk = UK_IDS[role]
    meta = {
        "source": "portal-download",
        "role": role,
        "subscriber_id": SUBSCRIBERS[role],
        "unique_key_id": uk,
        "registry_env_ui": "preprod",
        "materialized_at": datetime.now(timezone.utc).isoformat(),
        "signing_algorithm": "ed25519",
        "encryption_algorithm": "x25519",
        "encryption_public_key_format": "asn1_der_spki_b64",
        "signing_public_key_b64": signing_pub,
        "encryption_public_key_b64": enc_pub,
        "signing_public_fp16": _fp16(signing_pub),
        "encryption_public_fp16": _fp16(enc_pub),
        "note": "Portal PreProd Subscribed keypair. Prefer for PreProd /on_subscribe. Local DER under ../{role}/ remains for optional Staging.",
    }
    (out_dir / "public_metadata.json").write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "unique_key_id.txt").write_text(uk + "\n", encoding="utf-8")
    req = out_dir / "request_id.txt"
    if not req.is_file() or not req.read_text(encoding="utf-8").strip():
        req.write_text(f"aadhaar-portal-{role}-{uk[:8]}\n", encoding="utf-8")

    return {
        "role": role,
        "dir": str(out_dir),
        "source": str(src),
        "unique_key_id": uk,
        "signing_public_fp16": meta["signing_public_fp16"],
        "encryption_public_fp16": meta["encryption_public_fp16"],
        "pem_written": True,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--role", choices=("buyer", "seller", "both"), default="both")
    args = ap.parse_args()
    roles = ("buyer", "seller") if args.role == "both" else (args.role,)
    results = []
    for role in roles:
        results.append(materialize(role))
    print(json.dumps({"ok": True, "results": results}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"}), file=sys.stderr)
        raise SystemExit(1)
