#!/usr/bin/env python3
"""Single entry point for portfolio browser testing.

Usage:
  python3 scripts/portfolio_browser.py lane [burner|solflare] [seller|buyer|all]
  python3 scripts/portfolio_browser.py preflight
  python3 scripts/portfolio_browser.py sso demo [seller|buyer|all]
  python3 scripts/portfolio_browser.py sso burner [seller|buyer|all]
  python3 scripts/portfolio_browser.py sso solflare [seller|buyer]
  python3 scripts/portfolio_browser.py smoke
  python3 scripts/portfolio_browser.py closeout [leave_url]
  python3 scripts/portfolio_browser.py onboarding [--fixture]
  python3 scripts/portfolio_browser.py commerce seller|buyer [--fixture]
  python3 scripts/portfolio_browser.py agentguard seller|buyer [--fixture]
  python3 scripts/portfolio_browser.py two-sided [--fixture]
  python3 scripts/portfolio_browser.py full [burner|solflare]
  python3 scripts/portfolio_browser.py diag [--url URL]
  python3 scripts/portfolio_browser.py status
"""
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import time
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL_SCRIPTS = ROOT / ".cursor/skills/portfolio-browser/scripts"
HERMES_BRIDGE = SKILL_SCRIPTS / "hermes_bridge.py"
PAGE_DIAG = SKILL_SCRIPTS / "page_diag.py"
SSO_SCRIPT = ROOT / "scripts/hermes_portfolio_sso.py"
DEMO_SSO_SCRIPT = ROOT / "scripts/hermes_demo_sso.py"
SOLFLARE_SSO = SKILL_SCRIPTS / "solflare_sso.py"
ONBOARDING_SCRIPT = ROOT / "scripts/hermes_identity_onboarding.py"
COMMERCE_SCRIPT = ROOT / "scripts/hermes_elevated_commerce.py"
AGENTGUARD_SELLER_SCRIPT = ROOT / "scripts/hermes_agentguard_seller.py"
AGENTGUARD_BUYER_SCRIPT = ROOT / "scripts/hermes_agentguard_buyer.py"
TWO_SIDED_SCRIPT = ROOT / "scripts/hermes_two_sided_commerce.py"


def _load_page_diag():
    spec = importlib.util.spec_from_file_location("portfolio_page_diag", PAGE_DIAG)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {PAGE_DIAG}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

SMOKE_URLS = [
    "http://127.0.0.1:43102/results?q=rice",
    "http://127.0.0.1:43103/dashboard",
]


def run(cmd: list[str], *, check: bool = True) -> int:
    proc = subprocess.run(cmd, cwd=ROOT)
    if check and proc.returncode != 0:
        raise SystemExit(proc.returncode)
    return proc.returncode


def load_handler():
    helper = ROOT / ".cursor/skills/portfolio-browser/scripts"
    sys.path.insert(0, str(helper))
    from wip_hermes import load_handler as _load

    return _load()


def hermes_run(actions: list[dict], *, session: str = "portfolio-browser", timeout: int = 45) -> dict:
    """Run Hermes actions with automatic console+UI dump; attach compact page_diag."""
    helper = ROOT / ".cursor/skills/portfolio-browser/scripts"
    sys.path.insert(0, str(helper))
    from wip_hermes import ensure_wip_env

    ensure_wip_env()
    page_diag = _load_page_diag()
    wrapped = page_diag.wrap_actions(actions)
    handler = load_handler()
    raw = handler._handle_hermes_chrome_browser(
        {
            "action": "run",
            "session_name": session,
            "use_selected_tab": False,
            "timeout_seconds": timeout,
            "actions": wrapped,
        },
        task_id="portfolio-browser",
    )
    data = json.loads(raw) if isinstance(raw, str) else raw
    if not data.get("success"):
        raise RuntimeError(data.get("error") or data)
    diag = page_diag.extract_diag(data)
    data["page_diag"] = diag
    if not diag.get("ok"):
        print(json.dumps({"page_diag": diag}, indent=2), flush=True)
    return data


def cmd_preflight(_: list[str]) -> int:
    return run(["bash", str(SKILL_SCRIPTS / "preflight.sh")])


def maybe_preflight() -> None:
    if os.environ.get("PORTFOLIO_SKIP_PREFLIGHT") == "1":
        return
    cmd_preflight([])


def cmd_closeout(args: list[str]) -> int:
    leave = args[0] if args else "http://127.0.0.1:43102/search"
    return run(["bash", str(SKILL_SCRIPTS / "closeout.sh"), leave])


def cmd_urls(_: list[str]) -> int:
    return run([sys.executable, str(HERMES_BRIDGE), "urls"], check=False)


def cmd_status(_: list[str]) -> int:
    return run([sys.executable, str(HERMES_BRIDGE), "status"], check=False)


def cmd_diag(args: list[str]) -> int:
    """Compact UI + console + backend issues for the active Hermes page."""
    cmd = [sys.executable, str(PAGE_DIAG)]
    if args and args[0] == "--url" and len(args) > 1:
        cmd.extend(["--url", args[1]])
    elif args:
        cmd.extend(["--url", args[0]])
    return run(cmd, check=False)


def cmd_sso(args: list[str]) -> int:
    if not args:
        print("Usage: sso demo|burner|solflare [seller|buyer|all]", file=sys.stderr)
        return 2
    maybe_preflight()
    wallet = args[0].lower()
    app = (args[1] if len(args) > 1 else "all").lower()

    if wallet == "solflare":
        if app not in {"seller", "buyer"}:
            print("Solflare SSO: use seller or buyer (not all)", file=sys.stderr)
            return 2
        return run([sys.executable, str(SOLFLARE_SSO), app])

    if wallet == "demo":
        apps = ["seller", "buyer"] if app == "all" else [app]
        for name in apps:
            if name not in {"seller", "buyer"}:
                print(f"Unknown app {name!r}. Use seller, buyer, or all.", file=sys.stderr)
                return 2
            code = run([sys.executable, str(DEMO_SSO_SCRIPT), name])
            if code != 0:
                return code
        return 0

    if wallet != "burner":
        print(f"Unknown mode {wallet!r}. Use: demo | burner | solflare", file=sys.stderr)
        return 2

    apps = ["seller", "buyer"] if app == "all" else [app]
    for name in apps:
        if name not in {"seller", "buyer"}:
            print(f"Unknown app {name!r}. Use seller, buyer, or all.", file=sys.stderr)
            return 2
        sso_args = [name]
        if name == "buyer" and "--checkout" in args:
            sso_args.append("--checkout")
        code = run([sys.executable, str(SSO_SCRIPT), *sso_args])
        if code != 0:
            return code
    return 0


def cmd_smoke(_: list[str]) -> int:
    maybe_preflight()
    actions: list[dict] = []
    for url in SMOKE_URLS:
        actions.extend(
            [
                {"type": "goto", "url": url},
                {"type": "wait", "ms": 1500},
                {"type": "page_context"},
            ]
        )
    result = hermes_run(actions, timeout=60)
    contexts = [r for r in result.get("results", []) if r.get("type") == "page_context"]
    pages = [
        {"url": c.get("url"), "title": c.get("title"), "buttons": (c.get("buttons") or [])[:5]}
        for c in contexts
    ]
    titles = [p.get("title") or "" for p in pages]
    buyer_ok = any("ONDC Buyer" in title for title in titles)
    seller_ok = any("ONDC Seller" in title for title in titles)
    out = {
        "success": buyer_ok and seller_ok,
        "method": "hermes",
        "signals": {
            "buyer_title_ok": buyer_ok,
            "seller_title_ok": seller_ok,
        },
        "final_url": result.get("final_url"),
        "pages": pages,
    }
    print(json.dumps(out, indent=2))
    if not out["success"]:
        print("✗ Smoke failed — expected ONDC Buyer and ONDC Seller page titles", file=sys.stderr)
        return 1
    return 0


def cmd_onboarding(args: list[str]) -> int:
    maybe_preflight()
    cmd = [sys.executable, str(ONBOARDING_SCRIPT)]
    if "--fixture" in args or not args:
        cmd.append("--fixture")
    return run(cmd)


def cmd_commerce(args: list[str]) -> int:
    if not args:
        print("Usage: commerce seller|buyer [--fixture]", file=sys.stderr)
        return 2
    maybe_preflight()
    app = args[0].lower()
    extra = ["--fixture"]
    env = os.environ.copy()
    if app == "buyer" and os.environ.get("COMMERCE_SKIP_SSO") != "1":
        # Standalone buyer commerce includes dev_auto SSO.
        pass
    proc = subprocess.run([sys.executable, str(COMMERCE_SCRIPT), app, *extra], cwd=ROOT, env=env)
    return proc.returncode


def cmd_agentguard(args: list[str]) -> int:
    """AgentGuard vertical slice (Hermes mutex / Token Nxt demo)."""
    app = (args[0] if args else "seller").lower()
    if app not in {"seller", "buyer"}:
        print("Usage: agentguard seller|buyer [--fixture]", file=sys.stderr)
        return 2
    maybe_preflight()
    if os.environ.get("AGENTGUARD_SKIP_SSO") != "1":
        if cmd_sso(["demo", app]) != 0:
            return 1
    env = os.environ.copy()
    env["AGENTGUARD_SKIP_SSO"] = "1"
    script = AGENTGUARD_SELLER_SCRIPT if app == "seller" else AGENTGUARD_BUYER_SCRIPT
    return subprocess.run(
        [sys.executable, str(script), "--fixture"],
        cwd=ROOT,
        env=env,
    ).returncode


def cmd_two_sided(args: list[str]) -> int:
    """Two-sided local commerce proof with unique run-scoped evidence."""
    cmd = [sys.executable, str(TWO_SIDED_SCRIPT)]
    if "--fixture" in args or not args:
        cmd.append("--fixture")
    # Always mint a unique run-id unless caller already passed --run-id.
    if "--run-id" not in args:
        cmd.extend(["--run-id", f"ag-{int(time.time())}-{uuid.uuid4().hex[:6]}"])
    else:
        # Forward explicit --run-id VALUE from args
        i = args.index("--run-id")
        if i + 1 < len(args):
            cmd.extend(["--run-id", args[i + 1]])
    return subprocess.run(cmd, cwd=ROOT, env=os.environ.copy()).returncode


def cmd_full(args: list[str]) -> int:
    """Full portfolio validation: onboarding → SSO seller/buyer → commerce → closeout."""
    wallet = (args[0] if args else "burner").lower()
    if wallet not in {"burner", "solflare"}:
        print(f"Unknown wallet {wallet!r}. Use: burner | solflare", file=sys.stderr)
        return 2

    cmd_preflight([])
    os.environ["PORTFOLIO_SKIP_PREFLIGHT"] = "1"
    try:
        print("→ Identity onboarding (/verify wizard)", flush=True)
        if cmd_onboarding(["--fixture"]) != 0:
            return 1
        for app in ("seller", "buyer"):
            if app == "buyer":
                print(f"→ SSO {wallet} {app} + checkout", flush=True)
                if cmd_sso([wallet, app, "--checkout"]) != 0:
                    return 1
                continue
            print(f"→ SSO {wallet} {app}", flush=True)
            if cmd_sso([wallet, app]) != 0:
                return 1
            print(f"→ Commerce {app}", flush=True)
            if cmd_commerce([app, "--fixture"]) != 0:
                return 1
        return cmd_closeout([])
    finally:
        os.environ.pop("PORTFOLIO_SKIP_PREFLIGHT", None)


def cmd_lane(args: list[str]) -> int:
    """Validated browser lane: preflight → smoke → sso → closeout (one preflight)."""
    wallet = (args[0] if args else "burner").lower()
    app = (args[1] if len(args) > 1 else "seller").lower()
    if wallet not in {"burner", "solflare"}:
        print(f"Unknown wallet {wallet!r}. Use: burner | solflare", file=sys.stderr)
        return 2

    cmd_preflight([])
    os.environ["PORTFOLIO_SKIP_PREFLIGHT"] = "1"
    try:
        if cmd_smoke([]) != 0:
            return 1
        if cmd_sso([wallet, app]) != 0:
            return 1
        return cmd_closeout([])
    finally:
        os.environ.pop("PORTFOLIO_SKIP_PREFLIGHT", None)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    cmd = sys.argv[1].lower()
    args = sys.argv[2:]
    handlers = {
        "lane": cmd_lane,
        "full": cmd_full,
        "onboarding": cmd_onboarding,
        "commerce": cmd_commerce,
        "agentguard": cmd_agentguard,
        "two-sided": cmd_two_sided,
        "preflight": cmd_preflight,
        "closeout": cmd_closeout,
        "urls": cmd_urls,
        "status": cmd_status,
        "diag": cmd_diag,
        "sso": cmd_sso,
        "smoke": cmd_smoke,
    }
    fn = handlers.get(cmd)
    if fn is None:
        print(f"Unknown command {cmd!r}. Use: {' | '.join(handlers)}", file=sys.stderr)
        return 2
    return fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
