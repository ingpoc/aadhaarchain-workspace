# Token Nxt — curated application answers

Prepared 2026-07-12 for [Token Nxt By NPCI](https://www.npci.org.in/token-nxt).  
**Do not submit until operator fills `[OPERATOR]` fields and adds demo video (Q33).**  
Honesty rule: no live UPI, no prod ONDC orders, no NPCI partnership claim.

Form inventory: [`token-nxt-application-form.md`](token-nxt-application-form.md).

---

## Page 1 — Company Identity

| # | Field | Answer |
| --- | --- | --- |
| 1 | Company Name | `GURUSHARAN GUPTA HUF` |
| 2 | Company Website URL | `https://aadharcha.in` |
| 3 | Headquarters Country | `India` |
| 4 | Year of Founding | `[OPERATOR]` — confirm HUF / venture year (≤2026) |
| 5 | Company Size (Employees) | `1-10` |
| 6 | Funding Stage | `Bootstrapped` |
| 7 | Primary Contact Name | `Gurusharan Gupta` |
| 8 | Primary Contact Email | `[OPERATOR]` — real inbox you monitor |
| 9 | Primary Contact Designation | `Founder` |
| 10 | LinkedIn Company Page URL | `[OPERATOR]` — personal or company LinkedIn URL, or leave blank if optional |

---

## Page 2 — AI Product / Solution Details

| # | Field | Answer |
| --- | --- | --- |
| 11 | Product / Solution Name | `AgentGuard — realtime voice + runtime agents for ONDC commerce, with mandate-based authority control` *(100/150)* |
| 12 | Product Website or Landing Page | `https://ondcbuyer.aadharcha.in` |
| 13 | Primary AI Product Category | `AI Agents & Autonomous Systems` |
| 14 | Secondary AI Product Category | `Security & Governance` |
| 15 | B2B / B2C / B2G | `B2B + B2C` |
| 18 | Live & commercially available? | `Yes - Limited Beta` |
| 19 | Active users / enterprise customers | `<100` |

### 16. Describe your product in 2–3 sentences *(401/500)*

```
AgentGuard is a live proof-of-concept for safe agentic commerce on ONDC. A natural realtime voice agent and a runtime agent work together: you speak what you need; tools search the network, add items to cart, and iterate—without typing. AgentGuard enforces what the agent may or may not do. When NPCI opens broader UPI Circle agent onboarding, the same guarded agent can complete checkout and payment.
```

### 17. What problem does your product solve? *(578/600)*

```
People want agents that shop and operate stores, but API keys and logins grant more power than intended. KYC proves identity; payment limits constrain value; neither answers why an autonomous action was allowed. AgentGuard solves safe authority: the principal sets allowed actions and limits; every protected tool call is server-evaluated—allow, step-up approve, or block—with pause/revoke and receipts. Voice handles simple “find and add” jobs and complex briefs like a ₹2,000 grocery basket using preferences and past context, without forcing the user to drive the UI by hand.
```

### 20. Key differentiator from existing solutions *(420/500)*

```
USP is realtime voice + runtime agent under one AgentGuard control plane on both ONDC Buyer and Seller. Conversation stays calm and tool-backed—not chat-only. The model proposes; deterministic policy authorizes. We do not invent a payment rail; we supply the authority layer that can later bind to UPI Circle agent profiles when NPCI’s pilot path is generally available—while demoing live cart and mandate control today.
```

---

## Page 3 — Technology Architecture

### 21. How is your product or solution built? *(multi-select)*

- [x] Built on 3rd-party LLM API  
- [x] Hybrid architecture  
- [x] Agent-based multi-model  

*(Optional add if you want richer stack story: RAG-based — only if you claim memory/retrieval in the PreProd demo.)*

### 22. Which AI models or frameworks are at the core? *(166/200)*

```
OpenAI Realtime (gpt-realtime) for Buyer voice; Cursor agent runtime for longer plans; shared tool runner; AgentGuard APIs on our gateway. No custom foundation model.
```

### 23. Does your product incorporate any of the following? *(multi-select)*

- [x] Real-time data processing  
- [x] Explainability *(mandate + receipts / action preview)*  
- [x] Guardrails & Safety layers *(AgentGuard evaluate / approve / pause)*  
- [ ] Other — leave blank unless you need a one-liner  

### 24. Describe your data handling and privacy approach *(451/500)*

```
Principals authenticate via Auth0 session cookies—not wallet keys for AgentGuard. Mandates and decisions are principal-keyed server-side. Models never receive PIN, OTP, full payment credentials, or raw identity evidence. Intent receipts are privacy-minimizing. Commerce demo uses ONDC PreProd; payment remains simulated until a sanctioned agent-payment path exists. We minimize what tools expose to the model and filter tools by the confirmed mandate.
```

### 25. Is your model proprietary, open-source, or hybrid?

`Partially Open-Source`  
*(Hosted LLM APIs + our proprietary AgentGuard/control plane and app tooling; not a fully open foundation model.)*

### 26. What measures are in place to reduce hallucination or bias? *(388/400)*

```
Consequential actions never rely on model judgment alone: AgentGuard evaluates every protected tool call against a human-confirmed mandate. Disallowed tools are filtered before the model can request them. Step-up approval binds one exact action with nonce and expiry. Voice and runtime agents share the same runner so hosts cannot bypass policy. Prefer tool results over free-form claims.
```

---

## Page 4 — Impact & Use Cases

### 27. Primary domain or industry *(multi-select)*

- [x] Finance & Banking  
- [x] Retail & E-commerce  

### 28. Describe a specific use case and outcome achieved *(581/700)*

```
Buyer speaks a grocery need (or a budget brief). Realtime voice issues real tool calls—search ONDC PreProd, compare, add to cart—while AgentGuard caps auto-approve amount and allowed actions (e.g. block checkout until mandate allows it). Seller side shows the same contract for refunds/ops. Outcome: a PreProd-ready POC where the user barely touches the UI, yet cannot be overcharged or over-authorized by the agent. Roadmap: when UPI Circle agent onboarding is available beyond CUG, the same agent completes payment under the same limits, applying offers and remembered preferences.
```

### 29. Quantify the impact of your solution *(371/400)*

```
POC metrics (lab/PreProd, not revenue): protected actions always hit server evaluate before mutate; Hermes-validated AgentGuard approve/replay/pause/deny paths; FQDN Buyer+Seller+gateway live; ONDC PreProd BAP+BPP search and order ACKs. Goal for end users: hands-free find-and-cart, and safer agent spend once payment rails accept guarded agents. No production GMV claimed.
```

| # | Field | Answer |
| --- | --- | --- |
| 30 | Do you have case studies? | `No` |
| 31 | Link to case study? | Leave blank (or skip if hidden when No) |
| 32 | Awards / certifications / recognitions *(102/300)* | `None yet. Selected for self-built ONDC PreProd Buyer+Seller participation and public FQDN demo (2026).` |

---

## Page 5 — Supporting Materials

| # | Field | Answer |
| --- | --- | --- |
| 33 | Product Demo Video Link | `[OPERATOR]` — **required for strength.** Record 2–3 min Loom: voice → tools → cart → AgentGuard restrict/approve on `ondcbuyer.aadharcha.in` (+ optional Seller refund). |
| 34 | Additional links or references *(169/300)* | see below |
| 35 | How did you hear about this program? | `NPCI Website` *(or LinkedIn if that is accurate)* |

### 34. Any additional links or references

```
Buyer: https://ondcbuyer.aadharcha.in | Seller: https://ondcseller.aadharcha.in | Gateway health: https://gateway.aadharcha.in/api/health | Product: https://aadharcha.in
```

---

## Pages 6–7 — Terms

| # | Field | Answer |
| --- | --- | --- |
| 36 | Agree to Terms & Condition | `Yes` *(read T&Cs on form first)* |
| 37 | Agree to Terms and conditions | `Yes` *(read T&Cs on form first)* |

**Do not click Submit until Q4, Q8, Q10 (if any), and Q33 are filled.**

---

## Operator checklist before Submit

1. Confirm year of founding (Q4) and contact email (Q8).  
2. Record and paste demo video URL (Q33).  
3. Confirm LinkedIn (Q10) or leave empty if optional.  
4. Re-read Q16/Q18/Q28 — no accidental “we pay via UPI today” wording.  
5. Be ready to staff a booth 9–11 Sep 2026 if selected (T&Cs require dedicated reps).
