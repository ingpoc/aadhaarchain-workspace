#!/usr/bin/env python3
"""Generate the session testing-ledger snapshot from its canonical owners."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents/skills/testing-ledger"
CONTROL = ROOT / ".session/checklist/checklist.json"
CHECKLIST_GATES = SKILL / "references/checklist-gates.json"
DEFAULT_OUTPUT = ROOT / ".session/testing/testing-ledger.json"
GATE_STATUSES = {"pending", "blocked", "failed", "passed", "not_required"}
REQUIRED_CHAIN = {"A1", "A2", "A4", "A7", "B3", "B4", "B5", "B6", "B7", "Q1", "C4", "B8", "G9"}
REQUIRED_GATE = {
    "id", "title", "kind", "status_code", "blocks_completion",
    "criteria", "procedure", "evidence_required",
}


def load_checklist_gates(checklist_items: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    control = json.loads(CHECKLIST_GATES.read_text(encoding="utf-8"))
    if control.get("schema_version") != "checklist-gates.v1":
        raise ValueError("checklist-gates.json schema_version must be checklist-gates.v1")
    links = control.get("items")
    if not isinstance(links, list):
        raise ValueError("checklist-gates.json items must be an array")
    linked_ids: set[str] = set()
    gate_ids: set[str] = set()
    output: list[dict[str, object]] = []
    for index, link in enumerate(links):
        if not isinstance(link, dict) or not isinstance(link.get("checklist_id"), str):
            raise ValueError(f"checklist gate link {index} must name checklist_id")
        checklist_id = link["checklist_id"]
        if checklist_id in linked_ids:
            raise ValueError(f"duplicate checklist gate link: {checklist_id}")
        if checklist_id not in checklist_items and checklist_id != "G9":
            raise ValueError(f"unknown checklist gate link: {checklist_id}")
        linked_ids.add(checklist_id)
        gates = link.get("gates")
        if not isinstance(gates, list) or not gates:
            raise ValueError(f"{checklist_id} requires at least one acceptance gate")
        for gate in gates:
            if not isinstance(gate, dict) or REQUIRED_GATE - gate.keys():
                raise ValueError(f"{checklist_id} has an incomplete acceptance gate")
            if gate["id"] in gate_ids:
                raise ValueError(f"duplicate acceptance gate id: {gate['id']}")
            gate_ids.add(gate["id"])
            if gate["status_code"] not in GATE_STATUSES:
                raise ValueError(f"{gate['id']} has invalid status_code")
            if not isinstance(gate["blocks_completion"], bool):
                raise ValueError(f"{gate['id']} blocks_completion must be boolean")
            for field in ("criteria", "procedure", "evidence_required"):
                values = gate[field]
                if not isinstance(values, list) or not values or not all(isinstance(value, str) and value.strip() for value in values):
                    raise ValueError(f"{gate['id']} requires non-empty {field}")
        passed_provider_gate = any(gate["kind"] == "provider_verification" and gate["status_code"] == "passed" for gate in gates)
        if passed_provider_gate:
            for field in ("freshness", "verified_at"):
                if not isinstance(link.get(field), str) or not link[field].strip():
                    raise ValueError(f"{checklist_id} passed provider verification requires {field}")
            try:
                datetime.fromisoformat(link["verified_at"])
            except ValueError as error:
                raise ValueError(f"{checklist_id} verified_at must be ISO-8601") from error
            evidence_refs = link.get("evidence_refs")
            if not isinstance(evidence_refs, list) or not evidence_refs or not all(isinstance(ref, str) and ref.strip() for ref in evidence_refs):
                raise ValueError(f"{checklist_id} passed provider verification requires evidence_refs")
            if missing_refs := [ref for ref in evidence_refs if not (ROOT / ref).is_file()]:
                raise ValueError(f"{checklist_id} provider evidence does not exist: {missing_refs}")
        product = checklist_items.get(checklist_id, {
            "item": "Product lead go/no-go decision",
            "status_code": "pending",
        })
        blocking = [gate for gate in gates if gate["blocks_completion"]]
        statuses = {gate["status_code"] for gate in blocking}
        acceptance_status = (
            "failed" if "failed" in statuses else
            "blocked" if "blocked" in statuses else
            "pending" if "pending" in statuses else
            "passed"
        )
        result = {
            "checklist_id": checklist_id,
            "checklist_title": product["item"],
            "product_status": product["status_code"],
            "acceptance_status": acceptance_status,
            "passed_gates": sum(gate["status_code"] in {"passed", "not_required"} for gate in blocking),
            "blocking_gates": len(blocking),
            "gates": gates,
        }
        for field in ("freshness", "verified_at", "source_fingerprint", "scope_note", "not_proven", "revalidate_when", "evidence_refs"):
            if field in link:
                result[field] = link[field]
        output.append(result)
    missing = REQUIRED_CHAIN - linked_ids
    if missing:
        raise ValueError(f"launch chain is missing checklist acceptance links: {sorted(missing)}")
    complete = {item_id for item_id, item in checklist_items.items() if item["status_code"] == "complete"}
    if missing := complete - linked_ids:
        raise ValueError(f"complete checklist items require linked acceptance gates: {sorted(missing)}")
    return output


def build_data() -> dict[str, object]:
    control = json.loads(CONTROL.read_text(encoding="utf-8"))
    items = {item["id"]: item for item in control["items"]}
    checklist_links = load_checklist_gates(items)
    source_paths = [CONTROL, CHECKLIST_GATES]
    fingerprint = hashlib.sha256(b"\0".join(path.read_bytes() for path in source_paths)).hexdigest()
    return {
        "schema_version": "testing-ledger.v1",
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "source_fingerprint": fingerprint,
        "sources": [str(path.relative_to(ROOT)) for path in source_paths],
        "checklist_links": checklist_links,
    }


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f"{path.suffix}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def write(output: Path) -> dict[str, object]:
    data = build_data()
    atomic_write(output, json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    return data


def smoke_check() -> None:
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "testing-ledger.json"
        data = write(output)
        cached = json.loads(output.read_text(encoding="utf-8"))
        assert cached == data
        assert cached["schema_version"] == "testing-ledger.v1"
        assert cached["checklist_links"][0]["checklist_id"] == "G0"
        assert cached["checklist_links"][0]["gates"][0]["criteria"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        smoke_check()
        print("testing-ledger snapshot smoke check passed")
        return 0
    data = write(args.output)
    print(
        json.dumps(
            {
                "output": str(args.output),
                "source_fingerprint": data["source_fingerprint"],
                "checklist_links": len(data["checklist_links"]),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
