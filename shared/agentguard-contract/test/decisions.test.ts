import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import {
  normalizeStoredDecisionV1,
  parseDecisionV2,
  parseStoredDecisionV1,
} from "../src/decisions.ts";
import {
  DECISION_VALUES,
  REQUIRED_ACTIONS,
  RISK_LEVELS,
  type Decision,
  type DecisionV2,
  normalizeStoredDecisionV1 as normalizeFromPackage,
  parseDecisionV2 as parseFromPackage,
} from "../src/index.ts";

async function fixture(name: string): Promise<unknown> {
  const contents = await readFile(new URL(`../fixtures/${name}`, import.meta.url), "utf8");
  return JSON.parse(contents);
}

test("golden V1 fixture parses and normalizes as non-authoritative", async () => {
  const input = await fixture("golden-decision-v1.json");
  assert.deepEqual(parseStoredDecisionV1(input), input);
  assert.deepEqual(normalizeStoredDecisionV1(input), {
    ...(input as object),
    authorization_usable: false,
    source_schema_version: "1",
  });
});

test("golden V2 fixture validates and is the live Decision type", async () => {
  const input = await fixture("golden-decision-v2.json");
  const parsed = parseDecisionV2(input);
  assert.deepEqual(parsed, input);
  assert.ok(parsed);
  const live: Decision = parsed;
  const versioned: DecisionV2 = live;
  assert.equal(live.schema_version, "2");
  assert.equal(versioned.policy_version, 3);
});

test("package entrypoint exports the complete decision enum and parser contract", async () => {
  assert.deepEqual(DECISION_VALUES, ["allow", "need_approval", "deny"]);
  assert.deepEqual(REQUIRED_ACTIONS, [
    "none",
    "review",
    "strong_authentication",
    "contact_support",
  ]);
  assert.deepEqual(RISK_LEVELS, ["read_only", "low", "medium", "high", "critical"]);
  assert.ok(parseFromPackage(await fixture("golden-decision-v2.json")));
  assert.ok(normalizeFromPackage(await fixture("golden-decision-v1.json")));
});

test("V2 parser rejects every missing required field", async () => {
  const input = await fixture("golden-decision-v2.json") as Record<string, unknown>;
  for (const field of [
    "schema_version",
    "decision_id",
    "policy_id",
    "decision",
    "reason_code",
    "human_reason",
    "required_action",
    "risk_level",
    "policy_version",
    "expires_at",
  ]) {
    const invalid = { ...input };
    delete invalid[field];
    assert.equal(parseDecisionV2(invalid), null, `accepted missing ${field}`);
  }
});

test("V2 parser rejects invalid enums and scalar values", async () => {
  const input = await fixture("golden-decision-v2.json") as Record<string, unknown>;
  for (const patch of [
    { schema_version: "1" },
    { decision_id: "" },
    { policy_id: "" },
    { decision: "approval_required" },
    { reason_code: "freeform" },
    { required_action: "approve" },
    { risk_level: "severe" },
    { policy_version: -1 },
    { policy_version: 1.5 },
    { expires_at: "not-a-date" },
    { human_reason: "" },
    { request_hash: 123 },
    { approval: [] },
    { receipt: "receipt" },
  ]) {
    assert.equal(parseDecisionV2({ ...input, ...patch }), null, `accepted ${JSON.stringify(patch)}`);
  }
});

test("V1 parser rejects a V2 decision", async () => {
  assert.equal(parseStoredDecisionV1(await fixture("golden-decision-v2.json")), null);
});
