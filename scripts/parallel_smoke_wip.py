#!/usr/bin/env python3
"""Deterministic parallel portfolio smoke via Hermes WIP leases (no LLM).

Quality: UI title + page console errors per app, in parallel windows.
Cost: $0 model tokens for the scout wave; agents only for unique issues.

  export HERMES_CHROME_BRIDGE_SOCKET=…/hermes-chrome-cursor-wip/run/chrome-bridge.sock
  python3 scripts/parallel_smoke_wip.py
  python3 scripts/parallel_smoke_wip.py --apps web,buyer,seller
  python3 scripts/parallel_smoke_wip.py --json   # machine packet for fixers

Exit 0 if all apps pass (HTTP + title). Console issues are reported but do not
fail the run unless --strict-console.
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

DEFAULT_SOCK = (
    "/Users/gurusharan/plugins/hermes-chrome-cursor-wip/run/chrome-bridge.sock"
)

APPS = {
    "web": {
        "url": "http://127.0.0.1:43100/",
        "paths": ["/", "/login"],
        "title_any": ["AadhaarChain", "Sign in"],
        "label": "Web",
    },
    "buyer": {
        "url": "http://127.0.0.1:43102/",
        "paths": ["/"],
        "title_any": ["ONDC Buyer", "Buyer"],
        "label": "Buyer",
    },
    "seller": {
        "url": "http://127.0.0.1:43103/",
        "paths": ["/"],
        "title_any": ["ONDC Seller", "Seller"],
        "label": "Seller",
    },
}

NOISE = (
    "ObjectMultiplex",
    "MaxListenersExceeded",
    "Lit is in dev mode",
    "externalized for browser compatibility",
    "registered as a Standard Wallet",
    "React Router Future Flag",
    "solflare-detect-metamask",
    "StreamMiddleware",
)

_bridge_lock = threading.Lock()


def bridge(payload: dict, timeout: float = 60) -> dict:
    sock = Path(os.environ.get("HERMES_CHROME_BRIDGE_SOCKET", DEFAULT_SOCK))
    raw = json.dumps(payload).encode()
    with _bridge_lock:
        c = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        c.settimeout(timeout)
        try:
            c.connect(str(sock))
            c.sendall(raw)
            chunks: list[bytes] = []
            while True:
                b = c.recv(65536)
                if not b:
                    break
                chunks.append(b)
        finally:
            c.close()
    return json.loads(b"".join(chunks))


def http_code(url: str, timeout: float = 3) -> int:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return int(r.status)
    except Exception:
        return 0


def rpc_ok(timeout: float = 3) -> bool:
    """Solana JSON-RPC getHealth (GET / on :8899 is not a valid probe)."""
    req = urllib.request.Request(
        "http://127.0.0.1:8899/",
        data=b'{"jsonrpc":"2.0","id":1,"method":"getHealth"}',
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode()
            return '"ok"' in body
    except Exception:
        return False


def is_noise(text: str) -> bool:
    return any(n in text for n in NOISE)


def unique_page_errors(entries: list[dict]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for e in entries or []:
        level = e.get("level") or ""
        if level not in ("error", "page_error", "unhandledrejection", "assert"):
            continue
        text = (e.get("text") or "").strip()
        if not text or is_noise(text):
            continue
        key = text[:160]
        if key in seen:
            continue
        seen.add(key)
        out.append(text[:240])
    return out


def smoke_app(name: str, cfg: dict) -> dict:
    sid = f"psmoke-{name}-{uuid.uuid4().hex[:8]}"
    label = cfg["label"]
    result: dict = {
        "app": name,
        "ok": False,
        "window_id": None,
        "pages": [],
        "issues": [],
        "error": None,
    }
    tok = None
    try:
        pre = bridge(
            {
                "type": "session_preflight",
                "sessionId": sid,
                "agentLabel": label,
                "url": cfg["url"],
                "isolation": "window",
                "ttlSeconds": 120,
            },
            timeout=45,
        )
        if not pre.get("success"):
            result["error"] = pre.get("error") or "preflight failed"
            return result
        tok = pre.get("lease_token")
        result["window_id"] = pre.get("window_id")
        actions: list[dict] = []
        for path in cfg["paths"]:
            base = cfg["url"].rstrip("/")
            url = base if path == "/" else f"{base}{path}"
            actions.extend(
                [
                    {"type": "goto", "url": url, "waitMs": 1200},
                    {"type": "page_context"},
                    {"type": "console_tail", "max": 40},
                ]
            )
        run = bridge(
            {
                "type": "run",
                "sessionId": sid,
                "leaseToken": tok,
                "agentLabel": label,
                "actions": actions,
                "timeoutSeconds": 50,
            },
            timeout=70,
        )
        if not run.get("success"):
            result["error"] = run.get("error") or "run failed"
            return result
        title_ok = False
        for item in run.get("results") or []:
            t = item.get("type")
            if t == "page_context":
                page = {
                    "url": item.get("url"),
                    "title": item.get("title"),
                    "console_error_count": item.get("console_error_count", 0),
                }
                result["pages"].append(page)
                title = item.get("title") or ""
                if any(s in title for s in cfg["title_any"]):
                    title_ok = True
            elif t == "console_tail":
                result["issues"].extend(unique_page_errors(item.get("entries") or []))
        # dedupe issues
        seen: set[str] = set()
        deduped = []
        for i in result["issues"]:
            k = i[:160]
            if k not in seen:
                seen.add(k)
                deduped.append(i)
        result["issues"] = deduped
        result["ok"] = bool(title_ok)
        if not title_ok:
            result["error"] = "title mismatch"
        return result
    except Exception as e:
        result["error"] = str(e)
        return result
    finally:
        if tok:
            try:
                bridge(
                    {
                        "type": "session_closeout",
                        "sessionId": sid,
                        "leaseToken": tok,
                    },
                    timeout=20,
                )
            except Exception:
                pass


def preflight_http(apps: list[str]) -> dict:
    checks = {
        "web": "http://127.0.0.1:43100/",
        "buyer": "http://127.0.0.1:43102/",
        "seller": "http://127.0.0.1:43103/",
        "gateway": "http://127.0.0.1:43101/",
        "rpc": "http://127.0.0.1:8899/",
    }
    out = {}
    for k, url in checks.items():
        if k in ("web", "buyer", "seller") and k not in apps:
            continue
        if k == "gateway" and "web" not in apps:
            continue
        if k == "rpc":
            out[k] = 200 if rpc_ok() else 0
        else:
            out[k] = http_code(url)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apps", default="web,buyer,seller", help="comma list")
    ap.add_argument("--json", action="store_true", help="print JSON only")
    ap.add_argument(
        "--strict-console",
        action="store_true",
        help="fail if any non-noise console error",
    )
    ap.add_argument("--require-rpc", action="store_true", help="require :8899 2xx")
    args = ap.parse_args()
    apps = [a.strip() for a in args.apps.split(",") if a.strip()]
    for a in apps:
        if a not in APPS:
            print(f"unknown app: {a}", file=sys.stderr)
            return 2

    os.environ.setdefault("HERMES_CHROME_BRIDGE_SOCKET", DEFAULT_SOCK)
    t0 = time.perf_counter()
    if args.require_rpc:
        ensure = (
            Path(__file__).resolve().parents[1]
            / "aadharsolana"
            / "scripts"
            / "ensure-validator.sh"
        )
        if ensure.is_file():
            subprocess.run(
                ["bash", str(ensure)],
                check=False,
                stdout=sys.stderr,
            )
    http = preflight_http(apps)
    if args.require_rpc and http.get("rpc", 0) == 0:
        packet = {
            "ok": False,
            "error": "Solana RPC :8899 down — run ./aadharsolana/scripts/ensure-validator.sh",
            "http": http,
            "apps": [],
            "fixer_packets": [],
        }
        print(json.dumps(packet, indent=2 if not args.json else None))
        return 1

    for a in apps:
        code = http.get(a, 0)
        if code == 0 or code >= 500:
            packet = {
                "ok": False,
                "error": f"{a} HTTP {code} — start stack ./scripts/start-dev.sh",
                "http": http,
                "apps": [],
                "fixer_packets": [],
            }
            print(json.dumps(packet, indent=None if args.json else 2))
            return 1

    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=len(apps)) as ex:
        futs = {ex.submit(smoke_app, a, APPS[a]): a for a in apps}
        for fut in as_completed(futs):
            results.append(fut.result())
    results.sort(key=lambda r: apps.index(r["app"]))

    fixer_packets = []
    for r in results:
        if r.get("issues"):
            fixer_packets.append(
                {
                    "app": r["app"],
                    "urls": [p.get("url") for p in r.get("pages") or []],
                    "issues": r["issues"],
                    "hint": "env vs product — check :8899 before code change if balance/RPC",
                }
            )

    all_ok = all(r.get("ok") for r in results)
    if args.strict_console and fixer_packets:
        all_ok = False

    packet = {
        "ok": all_ok,
        "seconds": round(time.perf_counter() - t0, 2),
        "http": http,
        "apps": results,
        "fixer_packets": fixer_packets,
        "policy": "deterministic scout; spawn LLM fixer only on fixer_packets",
    }
    print(json.dumps(packet, indent=None if args.json else 2))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
