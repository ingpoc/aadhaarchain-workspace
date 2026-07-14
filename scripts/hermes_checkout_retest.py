#!/usr/bin/env python3
"""Focused Buyer checkout retest with screenshots after host auto-fill fix."""
from __future__ import annotations

import json
import pathlib
import shutil
import sys
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".cursor/skills/portfolio-browser/scripts"))
from wip_hermes import ensure_wip_env, load_handler  # noqa: E402

GATEWAY = "http://127.0.0.1:43101"
BUYER = "http://127.0.0.1:43102"
EVIDENCE = ROOT / ".cursor/skills/ondc-testing/references/evidence"
SESSION = "ondc-checkout-retest"
TS = time.strftime("%Y%m%d-%H%M%S")


def call(handler, args):
    ensure_wip_env()
    raw = handler._handle_hermes_chrome_browser(args, task_id="checkout-retest")
    data = json.loads(raw) if isinstance(raw, str) else raw
    if not data.get("success"):
        raise RuntimeError(data.get("error") or data)
    return data


def save(mid, result):
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    saved = []
    for i, step in enumerate(result.get("results", [])):
        if step.get("type") == "screenshot" and step.get("screenshot_path"):
            src = pathlib.Path(step["screenshot_path"])
            if src.exists():
                dest = EVIDENCE / f"{mid}-{TS}-{i}{src.suffix}"
                shutil.copy2(src, dest)
                saved.append(str(dest))
    return saved


CLICK = "(() => { const o=document.querySelector('[data-testid=\"samantha-orb\"]'); if(!o)return{ok:false}; o.click(); return{ok:true}; })()"
ENSURE = "(() => { if(document.querySelector('[data-testid=\"samantha-orb-panel\"]'))return{ok:true}; const o=document.querySelector('[data-testid=\"samantha-orb\"]'); if(o)o.click(); return{ok:true}; })()"

def fill(msg):
    return f"""(() => {{
  const input=document.querySelector('[data-testid="samantha-orb-text"]');
  const send=document.querySelector('[data-testid="samantha-orb-send"]');
  if(!input||!send)return{{ok:false}};
  Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set.call(input,{json.dumps(msg)});
  input.dispatchEvent(new Event('input',{{bubbles:true}}));
  send.click();
  return{{ok:true}};
}})()"""

EVAL = """(() => {
  const panel=document.querySelector('[data-testid="samantha-orb-panel"]');
  const reply=document.querySelector('[data-testid="samantha-orb-reply"]');
  const body=document.body.innerText||'';
  return {
    href: location.href,
    pathname: location.pathname,
    hint: panel?panel.innerText.slice(0,700):'',
    reply: reply?reply.innerText.slice(0,400):'',
    body_snip: body.slice(0,900),
    has_banana: /banana/i.test(body),
    has_receipt: /receipt/i.test(body),
    has_approval: /need.?approval|approve once|approval/i.test(body),
    has_committed: /committed|checkout committed|allow/i.test(body),
    tools: (window.__samanthaTools||[]).slice(-10),
  };
})()"""

MANDATE = """(async () => {
  await fetch('http://127.0.0.1:43101/api/agentguard/agents/ensure',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({role:'buyer'})}).then(r=>r.json());
  const compile=await fetch('http://127.0.0.1:43101/api/agentguard/mandates/compile',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({role:'buyer',template:'buyer_shop_v1',limits:{auto_approve_max_inr:{'buyer.checkout.commit':5000}},allowed_actions:['buyer.catalog.search','buyer.cart.add','buyer.cart.update','buyer.checkout.commit']})}).then(r=>r.json());
  const mid=compile?.data?.mandate?.mandate_id;
  if(mid) await fetch('http://127.0.0.1:43101/api/agentguard/mandates/'+mid+'/confirm',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({})});
  return {mandate_id: mid||null};
})()"""


def last_eval(result):
    for step in reversed(result.get("results", [])):
        if step.get("type") == "evaluate":
            val = step.get("value") or step.get("result")
            if isinstance(val, dict) and "pathname" in val:
                return val
    return {}


def main():
    status = json.loads(urllib.request.urlopen(f"{GATEWAY}/api/realtime/status", timeout=10).read())
    if not status.get("data", {}).get("configured"):
        print(json.dumps({"error": "realtime not configured"})); return 1
    handler = load_handler()
    # Avoid chrome://extensions active-tab injection failure — jump to buyer first.
    try:
        call(
            handler,
            {
                "action": "run",
                "session_name": SESSION,
                "use_selected_tab": False,
                "timeout_seconds": 40,
                "actions": [
                    {"type": "goto", "url": f"{BUYER}/search"},
                    {"type": "wait", "ms": 1500},
                ],
            },
        )
    except Exception as e:
        print("warmup goto:", e)
    pre = call(handler, {"action": "preflight", "timeout_seconds": 20})
    if not pre.get("ready"):
        print(json.dumps({"error": "bridge", "preflight": pre}))
        return 1

    demo = f"{GATEWAY}/api/auth/demo-continue?" + urllib.parse.urlencode(
        {"aud": "ondcbuyer", "return": f"{BUYER}/search", "display_name": "Checkout Retest"}
    )
    boot = call(handler, {"action": "run", "session_name": SESSION, "use_selected_tab": False, "timeout_seconds": 100, "actions": [
        {"type": "goto", "url": demo}, {"type": "wait", "ms": 2200},
        {"type": "goto", "url": f"{BUYER}/search"}, {"type": "wait", "ms": 2200},
        {"type": "evaluate", "expression": MANDATE}, {"type": "wait", "ms": 800},
        {"type": "evaluate", "expression": CLICK}, {"type": "wait", "ms": 12000},
        {"type": "evaluate", "expression": EVAL},
    ]})

    # seed cart
    add = call(handler, {"action": "run", "session_name": SESSION, "use_selected_tab": False, "timeout_seconds": 120, "actions": [
        {"type": "evaluate", "expression": ENSURE}, {"type": "wait", "ms": 800},
        {"type": "evaluate", "expression": fill("add banana to my cart")},
        {"type": "wait", "ms": 26000},
        {"type": "evaluate", "expression": EVAL},
        {"type": "screenshot", "format": "jpeg", "quality": 70},
    ]})
    add_st = last_eval(add)
    add_shots = save("B-CHECKOUT-RETEST-CART", add)

    # checkout
    chk = call(handler, {"action": "run", "session_name": SESSION, "use_selected_tab": False, "timeout_seconds": 120, "actions": [
        {"type": "evaluate", "expression": ENSURE}, {"type": "wait", "ms": 800},
        {"type": "evaluate", "expression": fill("please checkout and pay for my cart now")},
        {"type": "wait", "ms": 28000},
        {"type": "evaluate", "expression": EVAL},
        {"type": "screenshot", "format": "jpeg", "quality": 70},
        {"type": "goto", "url": f"{BUYER}/checkout"}, {"type": "wait", "ms": 2000},
        {"type": "evaluate", "expression": EVAL},
        {"type": "screenshot", "format": "jpeg", "quality": 70},
    ]})
    states = [last_eval(chk)]
    # get both evals
    evals = []
    for step in chk.get("results", []):
        if step.get("type") == "evaluate":
            val = step.get("value") or step.get("result")
            if isinstance(val, dict) and "pathname" in val:
                evals.append(val)
    after = evals[0] if evals else {}
    page = evals[-1] if len(evals) > 1 else after
    shots = save("B-CHECKOUT-RETEST", chk)
    tools = [t.get("name") for t in (after.get("tools") or []) if isinstance(t, dict)]
    details = [t for t in (after.get("tools") or []) if isinstance(t, dict) and t.get("name") == "checkout_commit"]
    last_chk = details[-1] if details else {}
    blob = f"{after.get('hint','')} {after.get('reply','')} {page.get('body_snip','')}".lower()
    tool_hit = "checkout_commit" in tools
    tool_ok = bool(last_chk.get("ok")) or bool(last_chk.get("receiptId")) or (
        str(last_chk.get("decision") or "") in ("allow", "need_approval")
    )
    ag_visible = any(
        k in blob
        for k in (
            "receipt",
            "committed",
            "need_approval",
            "need approval",
            "denied",
            "deny",
            "checkout allowed",
            "approval",
        )
    )
    # Hard pass: checkout_commit succeeded (or honest need_approval) + screenshot + AG text visible
    ok = bool(shots) and tool_hit and tool_ok and ag_visible
    out = {
        "success": ok,
        "tool_hit": tool_hit,
        "tool_ok": tool_ok,
        "ag_visible": ag_visible,
        "checkout_tool": last_chk,
        "tools": tools,
        "after_ask": {
            "pathname": after.get("pathname"),
            "reply": (after.get("reply") or "")[:240],
            "hint": (after.get("hint") or "")[:300],
            "tools_detail": after.get("tools"),
        },
        "checkout_page": {
            "pathname": page.get("pathname"),
            "has_receipt": page.get("has_receipt"),
            "has_approval": page.get("has_approval"),
            "body_snip": (page.get("body_snip") or "")[:400],
        },
        "cart_seed": {"pathname": add_st.get("pathname"), "has_banana": add_st.get("has_banana"), "shots": add_shots},
        "screenshots": shots,
    }
    path = EVIDENCE / f"checkout-retest-{TS}.json"
    path.write_text(json.dumps(out, indent=2, default=str))
    print(json.dumps(out, indent=2, default=str))
    print("Wrote", path)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
