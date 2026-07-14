#!/usr/bin/env python3
"""Generate ONDC-style Ed25519 signing + X25519 encryption key material (A8).

Writes PEM files + public_metadata.json under --out (gitignored under
aadharchain/gateway/.local/ or data/ondc-keys/).

Encryption public key is ASN.1 DER (SubjectPublicKeyInfo) base64 — required by
ONDC key-format-generation /subscribe. Signing public remains raw 32-byte b64.

Does NOT register with ONDC — operator completes portal whitelist + staging
/subscribe after TLS + on_subscribe hosting.

Usage:
  python3 scripts/ondc_generate_keys.py
  python3 scripts/ondc_generate_keys.py --out aadharchain/gateway/.local/ondc-sandbox/buyer
  python3 scripts/ondc_generate_keys.py --convert-existing aadharchain/gateway/.local/ondc-sandbox/buyer
"""
from __future__ import annotations

import argparse
import base64
import json
from datetime import datetime, timezone
from pathlib import Path


def _encryption_public_der_b64(public_key) -> str:
    from cryptography.hazmat.primitives import serialization

    der = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return base64.b64encode(der).decode("ascii")


def _encryption_private_der_b64(private_key) -> str:
    from cryptography.hazmat.primitives import serialization

    der = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return base64.b64encode(der).decode("ascii")


def convert_existing(out: Path) -> dict:
    """Rewrite public_metadata.json encryption public to ASN.1 DER b64 from PEM."""
    from cryptography.hazmat.primitives import serialization

    encrypt_priv = out / "encryption_private.pem"
    signing_priv = out / "signing_private.pem"
    meta_path = out / "public_metadata.json"
    if not encrypt_priv.is_file() or not signing_priv.is_file():
        raise SystemExit(f"Missing PEMs under {out}")

    encrypt = serialization.load_pem_private_key(encrypt_priv.read_bytes(), password=None)
    signing = serialization.load_pem_private_key(signing_priv.read_bytes(), password=None)

    signing_pub = signing.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "converted_at": datetime.now(timezone.utc).isoformat(),
        "signing_algorithm": "ed25519",
        "encryption_algorithm": "x25519",
        "signing_public_key_b64": base64.b64encode(signing_pub).decode("ascii"),
        "encryption_public_key_b64": _encryption_public_der_b64(encrypt.public_key()),
        "encryption_public_key_format": "asn1_der_spki_b64",
        "encryption_private_key_der_b64": _encryption_private_der_b64(encrypt),
        "signing_private_key_path": str(signing_priv),
        "encryption_private_key_path": str(encrypt_priv),
        "note": (
            "encryption_public_key_b64 is ASN.1 DER SPKI b64 (ONDC /subscribe). "
            "Never commit private PEMs."
        ),
    }
    if meta_path.is_file():
        try:
            old = json.loads(meta_path.read_text(encoding="utf-8"))
            if old.get("generated_at"):
                meta["generated_at"] = old["generated_at"]
            if old.get("encryption_public_key_b64") and old.get(
                "encryption_public_key_format"
            ) != "asn1_der_spki_b64":
                meta["encryption_public_key_raw_b64_previous"] = old[
                    "encryption_public_key_b64"
                ]
        except json.JSONDecodeError:
            pass
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "mode": "convert", "out": str(out), "meta": str(meta_path)}


def generate(out: Path) -> dict:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519, x25519

    out.mkdir(parents=True, exist_ok=True)

    signing = ed25519.Ed25519PrivateKey.generate()
    encrypt = x25519.X25519PrivateKey.generate()

    signing_priv = out / "signing_private.pem"
    encrypt_priv = out / "encryption_private.pem"
    meta_path = out / "public_metadata.json"

    signing_priv.write_bytes(
        signing.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    encrypt_priv.write_bytes(
        encrypt.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )

    signing_pub = signing.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "signing_algorithm": "ed25519",
        "encryption_algorithm": "x25519",
        "signing_public_key_b64": base64.b64encode(signing_pub).decode("ascii"),
        "encryption_public_key_b64": _encryption_public_der_b64(encrypt.public_key()),
        "encryption_public_key_format": "asn1_der_spki_b64",
        "encryption_private_key_der_b64": _encryption_private_der_b64(encrypt),
        "signing_private_key_path": str(signing_priv),
        "encryption_private_key_path": str(encrypt_priv),
        "note": (
            "encryption_public_key_b64 is ASN.1 DER SPKI b64 (ONDC /subscribe). "
            "Never commit private PEMs."
        ),
    }
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "mode": "generate", "out": str(out), "meta": str(meta_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("aadharchain/gateway/data/ondc-keys"),
        help="Output directory for private keys + public metadata",
    )
    parser.add_argument(
        "--convert-existing",
        type=Path,
        default=None,
        help="Convert existing PEMs' encryption public to ASN.1 DER b64 (no regen)",
    )
    args = parser.parse_args()
    if args.convert_existing is not None:
        result = convert_existing(args.convert_existing)
    else:
        result = generate(args.out)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
