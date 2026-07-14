#!/usr/bin/env python3
"""Local smoke: portal PEM load + X25519 shared secret + Ed25519 site-verification sign.

No network. No secret printing. Exit 0 on pass.
"""
from __future__ import annotations

import base64
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "aadharchain/gateway"))
os.environ.setdefault("ONDC_REGISTRY_ENV", "preprod")

from cryptography.hazmat.primitives import serialization  # noqa: E402

from app import ondc_onboard_routes as r  # noqa: E402


def main() -> int:
    results = []
    for role in ("buyer", "seller"):
        paths = r._role_paths(role)
        if "portal-download" not in str(paths["base"]):
            raise SystemExit(f"expected portal-download for {role}, got {paths['base']}")
        enc = r._load_encryption_private(paths)
        ondc_pub = serialization.load_der_public_key(
            base64.b64decode(r.ONDC_ENC_PUBLIC_KEYS["preprod"])
        )
        shared = enc.exchange(ondc_pub)
        if len(shared) != 32:
            raise SystemExit(f"{role}: bad shared len")
        sig = r._sign_request_id("smoke-test-request-id", r._load_signing_private(paths))
        if len(base64.b64decode(sig)) != 64:
            raise SystemExit(f"{role}: bad signature len")
        meta = json.loads(paths["meta"].read_text(encoding="utf-8"))
        html = r._verification_html(role)
        body = html.body.decode("utf-8") if isinstance(html.body, (bytes, bytearray)) else str(html.body)
        if "ondc-site-verification" not in body:
            raise SystemExit(f"{role}: missing meta tag")
        results.append(
            {
                "role": role,
                "unique_key_id": meta.get("unique_key_id"),
                "signing_public_fp16": meta.get("signing_public_fp16"),
                "encryption_public_fp16": meta.get("encryption_public_fp16"),
                "ok": True,
            }
        )
    print(json.dumps({"ok": True, "smoke": "ondc_onboard_portal_keys", "results": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
