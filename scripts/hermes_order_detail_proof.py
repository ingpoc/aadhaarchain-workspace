#!/usr/bin/env python3
"""FQDN: find atta → add → cart → Samantha checkout → order detail Paid+receipt.

Pass only if /orders/{id} page body shows Paid + rcpt_* (not Order detail unavailable).
Hermes WIP. Demo off. $0.
"""
from __future__ import annotations

import json
import pathlib
import shutil
import sys
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
GATEWAY = "https://gateway.aadharcha.in"
BUYER = "https://ondcbuyer.aadharcha.in"
EVIDENCE = ROOT / ".cursor/skills/ondc-testing/references/evidence"
SESSION = "web-order-detail-proof"
TS = time.strftime("%Y%m%d-%H%M%S")
MID = f"W-B-ORDER-DETAIL-{TS}"


def load_handler():
    helper = ROOT / ".cursor/skills/portfolio-browser/scripts"
    sys.path.insert(0, str(helper))
    from wip_hermes import load_handler as _load

    return _load()


def call(handler, args: dict) -> dict:
    helper = ROOT / ".cursor/skills/portfolio-browser/scripts"
    sys.path.insert(0, str(helper))
    from wip_hermes import ensure_wip_env

    ensure_wip_env()
    raw = handler._handle_hermes_chrome_browser(args, task_id="order-detail-proof")
    data = json.loads(raw) if isinstance(raw, str) else raw
    if not data.get("success"):
        raise RuntimeError(data.get("error") or data)
    return data


def jq(s: str) -> str:
    return json.dumps(s)


CLICK_ORB = """
(() => {
  const orb = document.querySelector('[data-testid="samantha-orb"]');
  if (!orb) return { ok: false };
  orb.click();
  return { ok: true };
})()
"""

ENSURE_PANEL = """
(() => {
  const panel = document.querySelector('[data-testid="samantha-orb-panel"]');
  if (panel) return { ok: true, already: true };
  const orb = document.querySelector('[data-testid="samantha-orb"]');
  if (!orb) return { ok: false };
  orb.click();
  return { ok: true, already: false };
})()
"""

SETTLE = """
(() => {
  const panel = document.querySelector('[data-testid="samantha-orb-panel"]');
  const reply = document.querySelector('[data-testid="samantha-orb-reply"]');
  const hint = panel ? (panel.innerText || '') : '';
  const body = document.body.innerText || '';
  const toolsRaw = window.__samanthaTools || [];
  const tools = toolsRaw.slice(-24).map(t => {
    if (!t || typeof t !== 'object') return t;
    return {
      name: t.name || t.tool || t.type,
      ok: t.ok,
      navigateTo: t.navigateTo || t.navTo,
      cartAdds: t.cartAdds,
      navSuperseded: t.navSuperseded,
      message: (t.message || t.error || '') ? String(t.message || t.error).slice(0, 200) : undefined,
      itemId: t.itemId || (t.args && t.args.item_id),
    };
  });
  const localOrders = (() => {
    try {
      const raw = localStorage.getItem('ondc-local-demo-orders');
      if (!raw) return { count: 0, ids: [] };
      const arr = JSON.parse(raw);
      return {
        count: Array.isArray(arr) ? arr.length : 0,
        ids: (Array.isArray(arr) ? arr : []).map(o => o && o.id).filter(Boolean).slice(-5),
        lastStatus: Array.isArray(arr) && arr.length ? (arr[arr.length-1].status || arr[arr.length-1].payment_status) : null,
        lastPaid: Array.isArray(arr) && arr.length ? Boolean(arr[arr.length-1].paid || /paid/i.test(String(arr[arr.length-1].status||'')) || /paid/i.test(String(arr[arr.length-1].payment_status||''))) : false,
        lastReceipt: Array.isArray(arr) && arr.length ? (arr[arr.length-1].receipt_id || arr[arr.length-1].receiptId || (arr[arr.length-1].payment && arr[arr.length-1].payment.receipt_id)) : null,
      };
    } catch (e) {
      return { error: String(e) };
    }
  })();
  const pulling = /Pulling|Searching for|still looking|Thinking|Working/i.test(body + hint);
  return {
    href: location.href,
    pathname: location.pathname,
    search: location.search,
    headings: Array.from(document.querySelectorAll('h1,h2,h3')).map(h => (h.textContent||'').trim()).filter(Boolean).slice(0, 10),
    body_snip: body.slice(0, 2200),
    hint: hint.slice(0, 800),
    reply: reply ? reply.innerText.slice(0, 500) : '',
    tools,
    toolCount: toolsRaw.length,
    pulling,
    has_sign_out: /Sign out/i.test(body),
    has_atta: /atta/i.test(body),
    cart_line: /Robusta|Bananas|Atta|AgentGuard PreProd/i.test(body) && location.pathname === '/cart',
    paid: /\\bPaid\\b/i.test(body),
    receipt: /rcpt_[a-z0-9]+/i.test(body),
    unavailable: /Order detail unavailable/i.test(body),
    ag_card: /Need approval|Denied|AgentGuard/i.test(body),
    localOrders,
  };
})()
"""


def fill_send(message: str) -> str:
    return f"""
(() => {{
  const input = document.querySelector('[data-testid="samantha-orb-text"]');
  const send = document.querySelector('[data-testid="samantha-orb-send"]');
  if (!input || !send) return {{ ok: false, reason: 'missing_controls' }};
  const nativeSet = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
  nativeSet.call(input, {jq(message)});
  input.dispatchEvent(new Event('input', {{ bubbles: true }}));
  if (send.disabled) return {{ ok: false, reason: 'send_disabled', draft: input.value }};
  const before = (window.__samanthaTools || []).length;
  send.click();
  return {{ ok: true, draft: input.value, toolCountBefore: before }};
}})()
"""


def evals(result: dict) -> list[dict]:
    out = []
    for step in result.get("results", []):
        if step.get("type") != "evaluate":
            continue
        val = step.get("value") or step.get("result")
        if isinstance(val, dict):
            out.append(val)
    return out


def shot_paths(result: dict, prefix: str) -> list[str]:
    saved = []
    idx = 0
    for step in result.get("results", []):
        if step.get("type") != "screenshot":
            continue
        src = step.get("path") or step.get("file") or step.get("screenshot_path")
        if not src:
            continue
        src_p = pathlib.Path(src)
        if not src_p.exists():
            continue
        dest = EVIDENCE / f"{prefix}-{idx}{src_p.suffix or '.jpeg'}"
        shutil.copy2(src_p, dest)
        saved.append(str(dest.relative_to(ROOT)))
        idx += 1
    return saved


def tool_names(st: dict) -> list[str]:
    return [t.get("name") for t in (st.get("tools") or []) if isinstance(t, dict) and t.get("name")]


def wake():
    for path in ("/health", "/api/ondc/status"):
        try:
            urllib.request.urlopen(f"{GATEWAY}{path}", timeout=90).read()
        except Exception as e:
            print("wake warn", path, e)
    try:
        req = urllib.request.Request(
            f"{GATEWAY}/api/ondc/bpp/ensure-demo-item",
            method="POST",
            data=b"{}",
            headers={"Content-Type": "application/json"},
        )
        print("ensure-demo", urllib.request.urlopen(req, timeout=90).read()[:200])
    except Exception as e:
        print("ensure-demo warn", e)


def goto_orb(handler) -> dict:
    return call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 90,
            "actions": [
                {"type": "goto", "url": f"{BUYER}/search"},
                {"type": "wait", "ms": 2500},
                {"type": "evaluate", "expression": CLICK_ORB},
                {"type": "wait", "ms": 2500},
                {"type": "evaluate", "expression": ENSURE_PANEL},
                {"type": "wait", "ms": 2000},
                {"type": "evaluate", "expression": SETTLE},
            ],
        },
    )


def ask(handler, message: str, settle_rounds: int = 16, allow_pulling: bool = False) -> tuple[dict, list[str]]:
    actions = [
        {"type": "evaluate", "expression": ENSURE_PANEL},
        {"type": "wait", "ms": 800},
        {"type": "evaluate", "expression": fill_send(message)},
        {"type": "wait", "ms": 2500},
    ]
    for _ in range(settle_rounds):
        actions.extend(
            [
                {"type": "evaluate", "expression": SETTLE},
                {"type": "wait", "ms": 2000},
            ]
        )
    actions.append({"type": "screenshot"})
    actions.append({"type": "evaluate", "expression": SETTLE})
    result = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 180,
            "actions": actions,
        },
    )
    states = evals(result)
    shots = shot_paths(result, MID)
    # Prefer last non-pulling settle if available
    final = states[-1] if states else {}
    for st in reversed(states):
        if not st.get("pulling") or allow_pulling:
            # prefer states that advanced path/tools
            if st.get("tools") or st.get("pathname"):
                final = st
                break
    # better: last settle after screenshot
    if states:
        final = states[-1]
    return final, shots


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    wake()
    handler = load_handler()
    ledger: dict = {
        "stamp": TS,
        "alias": "ondcbuyer-archive-deploy-3i99740un → ondcbuyer.aadharcha.in",
        "bundle": "index-BaIfxHlR.js",
        "demo_mode": False,
        "steps": [],
    }

    boot = goto_orb(handler)
    boot_st = evals(boot)[-1] if evals(boot) else {}
    ledger["boot"] = {
        "signed_in": boot_st.get("has_sign_out"),
        "path": boot_st.get("pathname"),
        "hint": (boot_st.get("hint") or "")[:200],
    }
    if not boot_st.get("has_sign_out"):
        ledger["result"] = "Fail"
        ledger["reason"] = "Auth0 session missing (no Sign out)"
        (EVIDENCE / f"usp-order-detail-{TS}.json").write_text(json.dumps(ledger, indent=2))
        print(json.dumps(ledger, indent=2))
        return 2

    # 1 find atta
    find_st, find_shots = ask(handler, "find atta", settle_rounds=18)
    find_ok = find_st.get("pathname") == "/results" and "search_catalog" in tool_names(find_st)
    ledger["steps"].append(
        {
            "id": "B-FIND-ATTA",
            "result": "Pass" if find_ok else "Fail",
            "shots": find_shots,
            "state": {
                "pathname": find_st.get("pathname"),
                "has_atta": find_st.get("has_atta"),
                "pulling": find_st.get("pulling"),
                "tools": find_st.get("tools"),
                "hint": (find_st.get("hint") or "")[:300],
            },
        }
    )
    if not find_ok:
        ledger["result"] = "Fail"
        ledger["reason"] = "find atta did not settle on /results + search_catalog"
        (EVIDENCE / f"usp-order-detail-{TS}.json").write_text(json.dumps(ledger, indent=2))
        print(json.dumps(ledger, indent=2)[:5000])
        return 1

    time.sleep(2)
    # 2 add to cart
    add_st, add_shots = ask(handler, "add the atta to my cart", settle_rounds=14, allow_pulling=True)
    add_ok = "add_to_cart" in tool_names(add_st) and (
        add_st.get("pathname") == "/cart" or add_st.get("cart_line") or any(
            t.get("name") == "add_to_cart" and t.get("ok") for t in (add_st.get("tools") or []) if isinstance(t, dict)
        )
    )
    # if still on results but tool ok, navigate check via cart goto
    if add_ok and add_st.get("pathname") != "/cart":
        cart = call(
            handler,
            {
                "action": "run",
                "session_name": SESSION,
                "use_selected_tab": False,
                "timeout_seconds": 60,
                "actions": [
                    {"type": "goto", "url": f"{BUYER}/cart"},
                    {"type": "wait", "ms": 2500},
                    {"type": "evaluate", "expression": SETTLE},
                    {"type": "screenshot"},
                ],
            },
        )
        cart_st = evals(cart)[-1] if evals(cart) else {}
        add_shots.extend(shot_paths(cart, f"{MID}-cart"))
        add_st = {**add_st, "cart_check": cart_st}
        add_ok = bool(cart_st.get("cart_line") or cart_st.get("has_atta")) and cart_st.get("pathname") == "/cart"

    ledger["steps"].append(
        {
            "id": "B-ADD-ATTA",
            "result": "Pass" if add_ok else "Fail",
            "shots": add_shots,
            "state": {
                "pathname": add_st.get("pathname"),
                "cart_line": add_st.get("cart_line"),
                "tools": add_st.get("tools"),
                "cart_check": add_st.get("cart_check"),
                "hint": (add_st.get("hint") or "")[:300],
            },
        }
    )
    if not add_ok:
        ledger["result"] = "Fail"
        ledger["reason"] = "add→cart failed"
        (EVIDENCE / f"usp-order-detail-{TS}.json").write_text(json.dumps(ledger, indent=2))
        print(json.dumps(ledger, indent=2)[:6000])
        return 1

    time.sleep(2)
    # 3 checkout via Samantha
    chk_st, chk_shots = ask(handler, "checkout and pay for my cart", settle_rounds=16, allow_pulling=True)
    chk_tool = "checkout_commit" in tool_names(chk_st)
    order_path = chk_st.get("pathname") or ""
    on_order = order_path.startswith("/orders/")
    detail_pass = bool(
        on_order
        and chk_st.get("paid")
        and chk_st.get("receipt")
        and not chk_st.get("unavailable")
    )
    # If tool navigated but page still loading, hard refresh order URL from tool navigateTo
    if chk_tool and not detail_pass:
        nav = None
        for t in reversed(chk_st.get("tools") or []):
            if isinstance(t, dict) and t.get("name") == "checkout_commit" and t.get("navigateTo"):
                nav = t["navigateTo"]
                break
        if nav:
            url = nav if str(nav).startswith("http") else f"{BUYER}{nav}"
            refresh = call(
                handler,
                {
                    "action": "run",
                    "session_name": SESSION,
                    "use_selected_tab": False,
                    "timeout_seconds": 60,
                    "actions": [
                        {"type": "goto", "url": url},
                        {"type": "wait", "ms": 3000},
                        {"type": "evaluate", "expression": SETTLE},
                        {"type": "screenshot"},
                        {"type": "evaluate", "expression": SETTLE},
                    ],
                },
            )
            refresh_st = evals(refresh)[-1] if evals(refresh) else {}
            chk_shots.extend(shot_paths(refresh, f"{MID}-detail"))
            chk_st = {**chk_st, "detail_refresh": refresh_st}
            order_path = refresh_st.get("pathname") or order_path
            on_order = order_path.startswith("/orders/")
            detail_pass = bool(
                on_order
                and refresh_st.get("paid")
                and refresh_st.get("receipt")
                and not refresh_st.get("unavailable")
            )

    if detail_pass:
        result = "Pass"
    elif chk_tool and on_order and chk_st.get("unavailable"):
        result = "Fail"
    elif chk_tool:
        result = "Partial"
    else:
        result = "Fail"

    ledger["steps"].append(
        {
            "id": "W-B-CHECKOUT",
            "result": result,
            "shots": chk_shots,
            "state": {
                "pathname": order_path,
                "paid": chk_st.get("paid") or (chk_st.get("detail_refresh") or {}).get("paid"),
                "receipt": chk_st.get("receipt") or (chk_st.get("detail_refresh") or {}).get("receipt"),
                "unavailable": chk_st.get("unavailable")
                if "unavailable" in chk_st
                else (chk_st.get("detail_refresh") or {}).get("unavailable"),
                "tools": chk_st.get("tools"),
                "localOrders": chk_st.get("localOrders") or (chk_st.get("detail_refresh") or {}).get("localOrders"),
                "body_snip": (chk_st.get("detail_refresh") or chk_st).get("body_snip", "")[:1200],
                "hint": (chk_st.get("hint") or "")[:400],
            },
        }
    )
    ledger["result"] = result
    ledger["pass_gate"] = {
        "order_detail_paid_receipt": detail_pass,
        "checkout_commit": chk_tool,
        "unavailable": bool(
            (chk_st.get("detail_refresh") or chk_st).get("unavailable")
        ),
    }
    out = EVIDENCE / f"usp-order-detail-{TS}.json"
    out.write_text(json.dumps(ledger, indent=2))
    print(json.dumps(ledger, indent=2)[:8000])
    print("EVIDENCE", out)
    return 0 if result == "Pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
