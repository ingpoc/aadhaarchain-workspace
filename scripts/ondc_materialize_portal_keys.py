#!/usr/bin/env python3
"""Materialize ONDC portal keys.json into PEM + public_metadata (gitignored).

Does not print private key material. Safe to run in agent sessions.

Usage:
  python3 scripts/ondc_materialize_portal_keys.py
  python3 scripts/ondc_materialize_portal_keys.py --role buyer
  python3 scripts/ondc_materialize_portal_keys.py --role lbnp --latest-download \
    --unique-key-id <portal-readback-id> --out-dir <gitignored-dir>
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import stat
import sys
import tempfile
import uuid
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
    "lbnp": None,
}
SUBSCRIBERS = {
    "buyer": "ondcbuyer.aadharcha.in",
    "seller": "ondcseller.aadharcha.in",
    "lbnp": "ondclbnp.aadharcha.in",
}
REQUIRED_FIELDS = (
    "signing_private_key",
    "signing_public_key",
    "encryption_private_key",
    "encryption_public_key",
)


def _fp16(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def _secure_existing(path: Path) -> None:
    path.chmod(0o600)
    if stat.S_IMODE(path.stat().st_mode) != 0o600:
        raise PermissionError(f"sensitive key file permissions are not 0600: {path}")


def _write_sensitive(path: Path, data: bytes) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
    _secure_existing(path)


def _latest_valid_download() -> Path:
    matches: list[tuple[float, Path]] = []
    for path in (Path.home() / "Downloads").glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        if isinstance(data, dict) and all(
            isinstance(data.get(key), str) for key in REQUIRED_FIELDS
        ):
            matches.append((path.stat().st_mtime, path))
    if not matches:
        raise FileNotFoundError("no valid ONDC portal key download found")
    return max(matches, key=lambda item: item[0])[1]


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


def materialize(
    role: str,
    *,
    source: Path | None = None,
    out_dir: Path | None = None,
    unique_key_id: str | None = None,
) -> dict:
    role = role.lower().strip()
    src = source or PORTAL / role / "keys.json"
    if not src.is_file():
        raise FileNotFoundError(f"missing {src}")
    _secure_existing(src)
    source_bytes = src.read_bytes()
    data = json.loads(source_bytes.decode("utf-8"))
    for k in REQUIRED_FIELDS:
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

    out_dir = out_dir or PORTAL / role
    out_dir.mkdir(parents=True, exist_ok=True)
    key_json = out_dir / "keys.json"
    if src.resolve() != key_json.resolve():
        _write_sensitive(key_json, source_bytes)
    else:
        _secure_existing(key_json)
    _write_sensitive(
        out_dir / "signing_private.pem",
        signing.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ),
    )
    _write_sensitive(
        out_dir / "encryption_private.pem",
        encryption.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ),
    )

    uk = unique_key_id or UK_IDS[role]
    if uk:
        uk = str(uuid.UUID(uk))
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
    if uk:
        (out_dir / "unique_key_id.txt").write_text(uk + "\n", encoding="utf-8")
        req = out_dir / "request_id.txt"
        if not req.is_file() or not req.read_text(encoding="utf-8").strip():
            req.write_text(f"aadhaar-portal-{role}-{uk[:8]}\n", encoding="utf-8")

    return {
        "role": role,
        "dir": f"portal-download/{role}",
        "source": "portal-download",
        "unique_key_id": uk,
        "signing_public_fp16": meta["signing_public_fp16"],
        "encryption_public_fp16": meta["encryption_public_fp16"],
        "pem_written": True,
        "sensitive_file_mode": "0600",
    }


def self_test() -> None:
    signing = ed25519.Ed25519PrivateKey.generate()
    encryption = x25519.X25519PrivateKey.generate()
    payload = {
        "signing_private_key": base64.b64encode(
            signing.private_bytes(
                serialization.Encoding.Raw,
                serialization.PrivateFormat.Raw,
                serialization.NoEncryption(),
            )
        ).decode("ascii"),
        "signing_public_key": base64.b64encode(
            signing.public_key().public_bytes(
                serialization.Encoding.Raw,
                serialization.PublicFormat.Raw,
            )
        ).decode("ascii"),
        "encryption_private_key": base64.b64encode(
            encryption.private_bytes(
                serialization.Encoding.Raw,
                serialization.PrivateFormat.Raw,
                serialization.NoEncryption(),
            )
        ).decode("ascii"),
        "encryption_public_key": base64.b64encode(
            encryption.public_key().public_bytes(
                serialization.Encoding.DER,
                serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        ).decode("ascii"),
    }
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        source = root / "download.json"
        source.write_text(json.dumps(payload), encoding="utf-8")
        portal_uk_id = "9e7388f4-c68e-4006-ac5a-e7517382999f"
        result = materialize(
            "lbnp",
            source=source,
            out_dir=root / "out",
            unique_key_id=portal_uk_id,
        )
        for name in ("keys.json", "signing_private.pem", "encryption_private.pem"):
            if stat.S_IMODE((root / "out" / name).stat().st_mode) != 0o600:
                raise AssertionError(f"{name} is not 0600")
        if result["unique_key_id"] != portal_uk_id:
            raise AssertionError("lbnp unique_key_id must match portal readback")
        if (root / "out" / "unique_key_id.txt").read_text().strip() != portal_uk_id:
            raise AssertionError("lbnp unique_key_id.txt must match portal readback")
    print(json.dumps({"ok": True, "self_test": "lbnp-portal-key-materialization"}))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--role", choices=("buyer", "seller", "lbnp", "both"), default="both")
    ap.add_argument("--latest-download", action="store_true")
    ap.add_argument("--out-dir", type=Path)
    ap.add_argument("--unique-key-id")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return 0
    if (args.latest_download or args.out_dir or args.unique_key_id) and args.role == "both":
        ap.error("--latest-download/--out-dir/--unique-key-id require a single role")
    source = _latest_valid_download() if args.latest_download else None
    roles = ("buyer", "seller") if args.role == "both" else (args.role,)
    results = []
    for role in roles:
        results.append(
            materialize(
                role,
                source=source,
                out_dir=args.out_dir,
                unique_key_id=args.unique_key_id,
            )
        )
    print(json.dumps({"ok": True, "results": results}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"}), file=sys.stderr)
        raise SystemExit(1)
