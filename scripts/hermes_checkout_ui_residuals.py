#!/usr/bin/env python3
"""Buyer residuals: checkout paid UI, over-limit AG UI, long-task handoff.

Doctrine: claim → screenshot → Pass. Page must show paid/receipt (not orb-only).
"""
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
SESSION = "ondc-checkout-ui-residuals"
TS = time.strftime("%Y%m%d-%H%M%S")


def call(handler, args):
    ensure_wip_env()
    raw = handler._handle_hermes_chrome_browser(args, task_id="checkout-ui-residuals")
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
                saved.append(str(dest.relative_to(EVIDENCE.parent)))
    return saved


CLICK = "(() => { const o=document.querySelector('[data-testid=\"samantha-orb\"]'); if(!o)return{ok:false}; o.click(); return{ok:true}; })()"
ENSURE = "(() => { if(document.querySelector('[data-testid=\"samantha-orb-panel\"]'))return{ok:true}; const o=document.querySelector('[data-testid=\"samantha-orb\"]'); if(o)o.click(); return{ok:true}; })()"


def fill(msg):
    """Set orb input value (React may lag); pair with SEND after a short wait."""
    return f"""(() => {{
  const input=document.querySelector('[data-testid="samantha-orb-text"]');
  if(!input)return{{ok:false,reason:'no-input'}};
  Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set.call(input,{json.dumps(msg)});
  input.dispatchEvent(new Event('input',{{bubbles:true}}));
  input.dispatchEvent(new Event('change',{{bubbles:true}}));
  return{{ok:true,value:input.value}};
}})()"""


SEND = """(() => {
  const input=document.querySelector('[data-testid="samantha-orb-text"]');
  const send=document.querySelector('[data-testid="samantha-orb-send"]');
  const form=input&&input.closest('form');
  if(!input)return{ok:false,reason:'no-input'};
  // React controlled: re-dispatch so draft state catches up before submit.
  input.dispatchEvent(new Event('input',{bubbles:true}));
  if(form){
    try { form.requestSubmit(); return {ok:true,via:'form',value:input.value}; } catch(e) {}
  }
  if(send){ send.disabled=false; send.click(); return {ok:true,via:'click',value:input.value}; }
  return {ok:false,reason:'no-send'};
})()"""


def ask_actions(msg, wait_ms=28000):
    return [
        {"type": "evaluate", "expression": ENSURE},
        {"type": "wait", "ms": 1000},
        {"type": "evaluate", "expression": fill(msg)},
        {"type": "wait", "ms": 600},
        {"type": "evaluate", "expression": SEND},
        {"type": "wait", "ms": wait_ms},
        {"type": "evaluate", "expression": EVAL},
        {"type": "screenshot", "format": "jpeg", "quality": 70},
    ]


EVAL = """(() => {
  const panel=document.querySelector('[data-testid="samantha-orb-panel"]');
  const reply=document.querySelector('[data-testid="samantha-orb-reply"]');
  const body=document.body.innerText||'';
  const outcome=document.querySelector('[data-testid="buyer-checkout-outcome"]');
  const paid=document.querySelector('[data-testid="order-payment-paid"], [data-testid="order-payment-status"]');
  const receiptEl=document.querySelector('[data-testid="order-receipt-id"], [data-testid="order-payment-receipt"], [data-testid="buyer-checkout-receipt"]');
  return {
    href: location.href,
    pathname: location.pathname,
    hint: panel?panel.innerText.slice(0,700):'',
    reply: reply?reply.innerText.slice(0,400):'',
    body_snip: body.slice(0,1200),
    has_banana: /banana/i.test(body),
    has_receipt: /rcpt_|receipt/i.test(body),
    has_paid: /\\bPAID\\b|Payment succeeded|\\bPaid\\b/i.test(body),
    has_approval: /need.?approval|Need approval|approve once|one-time approval/i.test(body),
    has_denied: /\\bdenied\\b|Checkout denied/i.test(body),
    has_handoff: /started|I.?ll let you know|working on that|let you know when/i.test(
      (panel?panel.innerText:'') + ' ' + (reply?reply.innerText:'')
    ),
    outcome_visible: Boolean(outcome),
    paid_ui: Boolean(paid) || /\\bPAID\\b/.test(body),
    receipt_ui: Boolean(receiptEl) || /rcpt_[a-z0-9]+/i.test(body),
    tools: (window.__samanthaTools||[]).slice(-12),
  };
})()"""

MANDATE = """(async () => {
  await fetch('http://127.0.0.1:43101/api/agentguard/agents/ensure',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({role:'buyer'})}).then(r=>r.json());
  const compile=await fetch('http://127.0.0.1:43101/api/agentguard/mandates/compile',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({role:'buyer',template:'buyer_shop_v1',limits:{auto_approve_max_inr:{'buyer.checkout.commit':5000}},allowed_actions:['buyer.catalog.search','buyer.cart.add','buyer.cart.update','buyer.checkout.commit']})}).then(r=>r.json());
  const mid=compile?.data?.mandate?.mandate_id;
  if(mid) await fetch('http://127.0.0.1:43101/api/agentguard/mandates/'+mid+'/confirm',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({})});
  return {mandate_id: mid||null};
})()"""


def evals(result):
    out = []
    for step in result.get("results", []):
        if step.get("type") == "evaluate":
            val = step.get("value") or step.get("result")
            if isinstance(val, dict) and "pathname" in val:
                out.append(val)
    return out


def last_checkout_tool(st):
    details = [
        t
        for t in (st.get("tools") or [])
        if isinstance(t, dict) and t.get("name") == "checkout_commit"
    ]
    return details[-1] if details else {}


def main():
    status = json.loads(urllib.request.urlopen(f"{GATEWAY}/api/realtime/status", timeout=10).read())
    if not status.get("data", {}).get("configured"):
        print(json.dumps({"error": "realtime not configured"}))
        return 1
    handler = load_handler()
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
        {"aud": "ondcbuyer", "return": f"{BUYER}/search", "display_name": "Checkout UI Residuals"}
    )
    call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 100,
            "actions": [
                {"type": "goto", "url": demo},
                {"type": "wait", "ms": 2200},
                {"type": "goto", "url": f"{BUYER}/search"},
                {"type": "wait", "ms": 2200},
                {"type": "evaluate", "expression": MANDATE},
                {"type": "wait", "ms": 800},
                {"type": "evaluate", "expression": CLICK},
                {"type": "wait", "ms": 12000},
                {"type": "evaluate", "expression": EVAL},
            ],
        },
    )

    rows = []

    # --- seed cart ---
    add = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 120,
            "actions": ask_actions("add banana to my cart", 26000),
        },
    )
    add_st = evals(add)[-1] if evals(add) else {}
    add_shots = save("B-CHECKOUT-OK-CART", add)

    # --- B-CHECKOUT-OK ---
    chk = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 130,
            "actions": ask_actions("please checkout and pay for my cart now", 30000)
            + [
                {"type": "wait", "ms": 2500},
                {"type": "evaluate", "expression": EVAL},
                {"type": "screenshot", "format": "jpeg", "quality": 70},
            ],
        },
    )
    chk_evals = evals(chk)
    after = chk_evals[0] if chk_evals else {}
    page = chk_evals[-1] if chk_evals else {}
    shots_ok = save("B-CHECKOUT-OK", chk)
    tool = last_checkout_tool(after) or last_checkout_tool(page)
    path = page.get("pathname") or after.get("pathname") or ""
    page_paid = bool(page.get("has_paid") or page.get("paid_ui") or after.get("has_paid"))
    page_receipt = bool(page.get("has_receipt") or page.get("receipt_ui") or after.get("has_receipt"))
    on_order = "/orders/" in path
    tool_ok = bool(tool.get("ok")) or bool(tool.get("receiptId")) or str(tool.get("decision") or "") == "allow"
    ok_pass = bool(shots_ok) and tool_ok and page_paid and page_receipt and (on_order or page.get("outcome_visible"))
    rows.append(
        {
            "id": "B-CHECKOUT-OK",
            "result": "Pass" if ok_pass else "Fail",
            "screenshots": shots_ok,
            "pathname": path,
            "tool": tool,
            "page_paid": page_paid,
            "page_receipt": page_receipt,
            "body_snip": (page.get("body_snip") or after.get("body_snip") or "")[:400],
            "cart_seed": {"pathname": add_st.get("pathname"), "has_banana": add_st.get("has_banana"), "shots": add_shots},
        }
    )

    # --- re-seed cart for over-limit ---
    call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 120,
            "actions": [
                {"type": "goto", "url": f"{BUYER}/search"},
                {"type": "wait", "ms": 1500},
            ]
            + ask_actions("add banana to my cart", 24000)[:-2],  # no final eval/shot
        },
    )

    over = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 130,
            "actions": ask_actions(
                "try to checkout my cart for twenty five thousand rupees",
                28000,
            )
            + [
                {"type": "goto", "url": f"{BUYER}/checkout"},
                {"type": "wait", "ms": 2000},
                {"type": "evaluate", "expression": EVAL},
                {"type": "screenshot", "format": "jpeg", "quality": 70},
            ],
        },
    )
    over_evals = evals(over)
    over_after = over_evals[0] if over_evals else {}
    over_page = over_evals[-1] if len(over_evals) > 1 else over_after
    shots_over = save("B-CHECKOUT-OVER", over)
    over_tool = last_checkout_tool(over_after) or last_checkout_tool(over_page)
    over_blob = f"{over_page.get('body_snip','')} {over_after.get('hint','')} {over_after.get('reply','')}".lower()
    over_visible = (
        bool(over_page.get("has_approval") or over_page.get("has_denied") or over_page.get("outcome_visible"))
        or any(k in over_blob for k in ("need approval", "need_approval", "denied", "one-time approval"))
    )
    over_decision = str(over_tool.get("decision") or "")
    over_pass = bool(shots_over) and over_visible and (
        over_decision in ("need_approval", "deny")
        or "checkout_commit" in [t.get("name") for t in (over_after.get("tools") or []) if isinstance(t, dict)]
    )
    rows.append(
        {
            "id": "B-CHECKOUT-OVER",
            "result": "Pass" if over_pass else "Fail",
            "screenshots": shots_over,
            "pathname": over_page.get("pathname"),
            "tool": over_tool,
            "outcome_visible": over_page.get("outcome_visible"),
            "body_snip": (over_page.get("body_snip") or "")[:400],
        }
    )

    # --- B-LONG-WEEKLY ---
    long = call(
        handler,
        {
            "action": "run",
            "session_name": SESSION,
            "use_selected_tab": False,
            "timeout_seconds": 110,
            "actions": [
                {"type": "goto", "url": f"{BUYER}/search"},
                {"type": "wait", "ms": 1500},
            ]
            + ask_actions(
                "This is a long multi-step planning job: plan my weekly groceries under 2000 rupees in the background and let me know when done",
                26000,
            ),
        },
    )
    long_st = evals(long)[-1] if evals(long) else {}
    shots_long = save("B-LONG-WEEKLY", long)
    long_path = long_st.get("pathname") or ""
    long_blob = f"{long_st.get('hint','')} {long_st.get('reply','')}".lower()
    if "/agent" in long_path or "cursor" in long_blob:
        long_res = "Fail"
        long_note = f"leaked path={long_path}"
    elif bool(long_st.get("has_handoff")) or any(
        k in long_blob for k in ("started", "let you know", "working", "background", "notify")
    ):
        long_res = "Pass" if shots_long else "Fail"
        long_note = f"handoff path={long_path}"
    else:
        long_res = "Fail"
        long_note = f"no handoff path={long_path} blob={long_blob[:160]}"
    rows.append(
        {
            "id": "B-LONG-WEEKLY",
            "result": long_res,
            "screenshots": shots_long,
            "pathname": long_path,
            "note": long_note,
            "hint": (long_st.get("hint") or "")[:300],
            "tools": [
                t.get("name")
                for t in (long_st.get("tools") or [])
                if isinstance(t, dict)
            ],
        }
    )

    out = {
        "success": all(r.get("result") == "Pass" for r in rows),
        "ts": TS,
        "rows": rows,
    }
    path = EVIDENCE / f"checkout-ui-residuals-{TS}.json"
    path.write_text(json.dumps(out, indent=2, default=str))
    print(json.dumps(out, indent=2, default=str))
    print("Wrote", path)
    return 0 if out["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
