#!/usr/bin/env python3
"""Visible banana journey: Samantha text → search UI → cart update (Hermes WIP)."""
from __future__ import annotations

import json
import pathlib
import sys
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
GATEWAY = "http://127.0.0.1:43101"
BUYER = "http://127.0.0.1:43102"
SESSION = "samantha-banana-visible"


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
    raw = handler._handle_hermes_chrome_browser(args, task_id="samantha-banana")
    data = json.loads(raw) if isinstance(raw, str) else raw
    if not data.get("success"):
        raise RuntimeError(data.get("error") or data)
    return data


def js_quote(s: str) -> str:
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


def fill_send(message: str) -> str:
    return f"""
(() => {{
  const input = document.querySelector('[data-testid="samantha-orb-text"]');
  const send = document.querySelector('[data-testid="samantha-orb-send"]');
  if (!input || !send) return {{ ok: false, reason: 'missing_controls' }};
  const nativeSet = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
  nativeSet.call(input, {js_quote(message)});
  input.dispatchEvent(new Event('input', {{ bubbles: true }}));
  send.click();
  return {{ ok: true }};
}})()
"""

# Compact visible evidence — URL, cart, product names, orb hint/reply
EVAL_VISIBLE = """
(async () => {
  const panel = document.querySelector('[data-testid="samantha-orb-panel"]');
  const reply = document.querySelector('[data-testid="samantha-orb-reply"]');
  const hint = panel ? panel.innerText : '';
  const body = document.body.innerText || '';
  const cartLink = Array.from(document.querySelectorAll('a,button,[role="link"]'))
    .find((el) => /cart/i.test(el.textContent || '') || /\\/cart/.test(el.getAttribute('href') || ''));
  const cartBadgeText = cartLink ? (cartLink.textContent || '').trim().slice(0, 80) : '';
  let cartCount = null;
  const badgeMatch = cartBadgeText.match(/(\\d+)/);
  if (badgeMatch) cartCount = Number(badgeMatch[1]);
  const headings = Array.from(document.querySelectorAll('h1,h2,h3'))
    .map((h) => (h.textContent || '').trim())
    .filter(Boolean)
    .slice(0, 12);
  const bananaOnPage = /banana/i.test(body);
  const resultsUrl = /\\/results/i.test(location.pathname);
  const cartUrl = /\\/cart/i.test(location.pathname);
  const tools = (window.__samanthaTools || []).slice(-8);
  const events = (window.__samanthaEvents || []).slice(-40);
  return {
    href: location.href,
    pathname: location.pathname,
    search: location.search,
    results_url: resultsUrl,
    cart_url: cartUrl,
    banana_on_page: bananaOnPage,
    headings,
    cart_badge: cartBadgeText,
    cart_count: cartCount,
    hint: hint.slice(0, 500),
    reply: reply ? reply.innerText.slice(0, 400) : '',
    body_snip: body.slice(0, 700),
    tools,
    event_types: events,
  };
})()
"""


def eval_results(result: dict) -> list[dict]:
    out = []
    for step in result.get("results", []):
        if step.get("type") != "evaluate":
            continue
        val = step.get("value") or step.get("result")
        if isinstance(val, dict) and ("href" in val or "pathname" in val or "ok" in val):
            out.append(val)
    return out


def main() -> int:
    status = json.loads(urllib.request.urlopen(f"{GATEWAY}/api/realtime/status", timeout=10).read())
    if not status.get("data", {}).get("configured"):
        print(json.dumps({"error": "realtime not configured", "status": status}, indent=2))
        return 1

    demo = (
        f"{GATEWAY}/api/auth/demo-continue?"
        + urllib.parse.urlencode(
            {
                "aud": "ondcbuyer",
                "return": f"{BUYER}/search",
                "display_name": "Banana Visible Test",
            }
        )
    )

    handler = load_handler()
    pre = call(handler, {"action": "preflight", "timeout_seconds": 20})
    if not pre.get("ready"):
        print(json.dumps({"error": "bridge not ready", "preflight": pre}, indent=2))
        return 1

    # Bootstrap: demo SSO + open orb + wait for text mode
    boot = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 90,
            "actions": [
                {"type": "goto", "url": demo},
                {"type": "wait", "ms": 2500},
                {"type": "goto", "url": f"{BUYER}/search"},
                {"type": "wait", "ms": 2500},
                {"type": "evaluate", "expression": CLICK_ORB},
                {"type": "wait", "ms": 12000},
                {"type": "evaluate", "expression": EVAL_VISIBLE},
            ],
        },
    )
    boot_states = [e for e in eval_results(boot) if "href" in e]
    boot_state = boot_states[-1] if boot_states else {}

    # Spot-check: hi should not fire tools / navigate away from /search
    hi = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 90,
            "actions": [
                {"type": "evaluate", "expression": ENSURE_PANEL},
                {"type": "wait", "ms": 2000},
                {"type": "evaluate", "expression": fill_send("hi")},
                {"type": "wait", "ms": 12000},
                {"type": "evaluate", "expression": EVAL_VISIBLE},
            ],
        },
    )
    hi_states = [e for e in eval_results(hi) if "href" in e]
    hi_state = hi_states[-1] if hi_states else {}
    hi_still_search = "/search" in (hi_state.get("pathname") or "")
    hi_no_results_nav = not hi_state.get("results_url")
    hi_hint = f"{hi_state.get('hint','')} {hi_state.get('reply','')}".lower()
    hi_toolish = any(
        k in hi_hint
        for k in (
            "found ",
            "navigating",
            "added ",
            "search_catalog",
            "add_to_cart",
            "/results",
        )
    )
    hi_pass = hi_still_search and hi_no_results_nav and not hi_toolish

    # Primary: add banana to cart — expect visible search then cart change
    banana = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 180,
            "actions": [
                {"type": "evaluate", "expression": ENSURE_PANEL},
                {"type": "wait", "ms": 1500},
                {
                    "type": "evaluate",
                    "expression": fill_send("add banana to my cart"),
                },
                {"type": "wait", "ms": 28000},
                {"type": "evaluate", "expression": EVAL_VISIBLE},
                {"type": "page_context"},
                # Cart page proof
                {"type": "goto", "url": f"{BUYER}/cart"},
                {"type": "wait", "ms": 2500},
                {"type": "evaluate", "expression": EVAL_VISIBLE},
            ],
        },
    )
    banana_states = [e for e in eval_results(banana) if "href" in e]
    # First post-utterance state (before forced cart goto), last is cart page
    after_ask = banana_states[0] if banana_states else {}
    cart_page = banana_states[-1] if len(banana_states) > 1 else {}

    after_url = after_ask.get("href") or ""
    saw_results = bool(after_ask.get("results_url")) or "/results" in after_url
    banana_visible_after = bool(after_ask.get("banana_on_page"))
    hint_blob = f"{after_ask.get('hint','')} {after_ask.get('reply','')}".lower()
    tool_claim = any(
        k in hint_blob
        for k in ("found", "added", "cart", "banana", "search", "navigat")
    )
    cart_has_banana = bool(cart_page.get("banana_on_page"))
    cart_count = cart_page.get("cart_count")
    if cart_count is None and cart_has_banana:
        cart_count = 1

    # Strict: must see results OR cart update with banana; talk-only fails
    talk_only = (
        not saw_results
        and not cart_has_banana
        and ("banana" in hint_blob or "cart" in hint_blob)
        and "added" not in hint_blob
        and "found" not in hint_blob
    )
    # Pass: results page showed banana OR cart page has banana after tools
    search_pass = saw_results and banana_visible_after
    cart_pass = cart_has_banana
    tools = after_ask.get("tools") or []
    tool_names = [t.get("name") for t in tools if isinstance(t, dict)]
    tools_ok = "search_catalog" in tool_names or "add_to_cart" in tool_names
    # Prefer tools + visible cart; results may flash then cart navigate
    banana_pass = cart_pass and tools_ok and not talk_only
    strong_pass = banana_pass and (search_pass or any(t.get("navigateTo") for t in tools))

    out = {
        "success": banana_pass,
        "strong_pass": strong_pass,
        "realtime_model": status.get("data", {}).get("model"),
        "steps": {
            "preflight": True,
            "hi_no_tools": hi_pass,
            "search_visible": search_pass,
            "cart_visible": cart_pass,
            "talk_only_fail": talk_only,
        },
        "boot": {
            "href": boot_state.get("href"),
            "hint": (boot_state.get("hint") or "")[:200],
        },
        "hi": {
            "pass": hi_pass,
            "href": hi_state.get("href"),
            "hint": (hi_state.get("hint") or "")[:200],
            "reply": (hi_state.get("reply") or "")[:200],
            "toolish": hi_toolish,
        },
        "after_banana_ask": {
            "href": after_ask.get("href"),
            "results_url": after_ask.get("results_url"),
            "banana_on_page": after_ask.get("banana_on_page"),
            "headings": after_ask.get("headings"),
            "cart_badge": after_ask.get("cart_badge"),
            "cart_count": after_ask.get("cart_count"),
            "hint": (after_ask.get("hint") or "")[:300],
            "reply": (after_ask.get("reply") or "")[:300],
            "body_snip": (after_ask.get("body_snip") or "")[:400],
            "tools": after_ask.get("tools"),
            "event_types": (after_ask.get("event_types") or [])[-20:],
        },
        "cart_page": {
            "href": cart_page.get("href"),
            "banana_on_page": cart_page.get("banana_on_page"),
            "cart_count": cart_count,
            "body_snip": (cart_page.get("body_snip") or "")[:400],
        },
        "page_diag": banana.get("page_diag"),
    }
    print(json.dumps(out, indent=2, default=str))
    return 0 if banana_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
