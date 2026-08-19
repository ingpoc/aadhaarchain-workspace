#!/usr/bin/env python3
"""Export the single session checklist owner to the standard dashboard."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType

from generate_testing_ledger import build_data as build_testing_data


sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[1]
CONTROL_PATH = ROOT / ".session/checklist/checklist.json"
STATE_PATH = ROOT / ".session/checklist/state.json"
TESTING_PATH = ROOT / ".session/testing/testing-ledger.json"
GLOBAL_RENDERER = Path.home() / ".agents/skills/checklist-framework/scripts/render_checklist.py"
STATUSES = ("pending", "in_progress", "testing", "partial", "blocked", "complete", "deferred", "not_required", "review")
PRIORITIES = ("critical", "high", "medium", "low")
OPEN_STATUSES = {"pending", "in_progress", "testing", "partial", "blocked", "review"}
REQUIRED_CONTROL = {
    "schema_version", "project", "title", "warning", "current_blocker",
    "go_live_path", "areas", "items", "operator_decisions",
}
REQUIRED_ITEM = {
    "id", "gate", "item", "status_code", "status", "priority", "responsible_owner",
    "evidence_scope",
}


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f"{path.suffix}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def load_control() -> dict[str, object]:
    control = json.loads(CONTROL_PATH.read_text(encoding="utf-8"))
    if not isinstance(control, dict):
        raise ValueError("checklist.json must contain an object")
    missing = REQUIRED_CONTROL - control.keys()
    if missing:
        raise ValueError(f"checklist.json missing: {sorted(missing)}")
    if control["schema_version"] != "checklist-control.v1":
        raise ValueError("checklist.json schema_version must be checklist-control.v1")
    items = control["items"]
    if not isinstance(items, list):
        raise ValueError("checklist.json items must be an array")
    ids: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"items[{index}] must be an object")
        missing = REQUIRED_ITEM - item.keys()
        if missing:
            raise ValueError(f"items[{index}] missing: {sorted(missing)}")
        item_id = item["id"]
        if not isinstance(item_id, str) or not item_id:
            raise ValueError(f"items[{index}] id must be a non-empty string")
        if item_id in ids:
            raise ValueError(f"duplicate checklist item id: {item_id}")
        ids.add(item_id)
        if item["status_code"] not in STATUSES:
            raise ValueError(f"items[{index}] has invalid status_code")
        if item["priority"] not in PRIORITIES:
            raise ValueError(f"items[{index}] has invalid priority")
        if "owner" in item or "source" in item:
            raise ValueError(f"items[{index}] uses obsolete competing owner/source fields")
        if item["status_code"] in OPEN_STATUSES:
            for field in ("remaining_work", "completion_criteria"):
                value = item.get(field)
                if not isinstance(value, list) or not value or not all(isinstance(entry, str) and entry.strip() for entry in value):
                    raise ValueError(f"items[{index}] open item requires non-empty {field}")
    go_live_path = control["go_live_path"]
    phases = go_live_path.get("phases") if isinstance(go_live_path, dict) else None
    if not isinstance(phases, list) or not phases:
        raise ValueError("go_live_path must contain phases")
    path_ids = [item_id for phase in phases for item_id in phase.get("items", [])]
    if any(not isinstance(phase.get("label"), str) or not phase["label"].strip() or not phase.get("items") for phase in phases):
        raise ValueError("go_live_path phases require a label and items")
    if len(path_ids) != len(set(path_ids)) or not all(item_id in ids for item_id in path_ids):
        raise ValueError("go_live_path phases must name unique existing checklist items")
    for field in ("updated_at", "updated_by", "reason"):
        if not isinstance(go_live_path.get(field), str) or not go_live_path[field].strip():
            raise ValueError(f"go_live_path requires {field}")
    try:
        datetime.fromisoformat(go_live_path["updated_at"])
    except ValueError as error:
        raise ValueError("go_live_path updated_at must be ISO-8601") from error
    item_by_id = {item["id"]: item for item in items}
    closed_path = [item_id for item_id in path_ids if item_by_id[item_id]["status_code"] not in OPEN_STATUSES]
    if closed_path:
        raise ValueError(f"go_live_path must contain only open work: {closed_path}")
    required_open = {
        item["id"] for item in items
        if item["priority"] == "critical" and item["status_code"] in OPEN_STATUSES
    }
    if missing := required_open - set(path_ids):
        raise ValueError(f"go_live_path omits critical open work: {sorted(missing)}")
    parallel_now = go_live_path.get("parallel_now")
    if not isinstance(parallel_now, list) or len(parallel_now) != len(set(parallel_now)) or not all(item_id in path_ids for item_id in parallel_now):
        raise ValueError("go_live_path parallel_now must name unique queued items")
    invalid_parallel = [item_id for item_id in parallel_now if not item_by_id[item_id].get("operator_boundary")]
    if invalid_parallel:
        raise ValueError(f"parallel_now requires an operator boundary: {invalid_parallel}")
    primary = next((item_id for item_id in path_ids if item_id not in parallel_now), None)
    if primary is None or item_by_id[primary]["status_code"] not in {"in_progress", "testing", "partial"}:
        raise ValueError("the first agent-owned queue item must be in_progress, testing, or partial")
    load_renderer().validate_queue_conflicts(items, go_live_path)
    areas = control["areas"]
    if not isinstance(areas, list) or not areas:
        raise ValueError("areas must be a non-empty array")
    area_item_ids = [item_id for area in areas for item_id in area.get("items", [])]
    if len(area_item_ids) != len(set(area_item_ids)) or set(area_item_ids) != ids:
        raise ValueError("areas must assign every checklist item exactly once")
    load_renderer().validate_operator_decisions(control.get("operator_decisions"), ids)
    return control


def derive_focus_and_action(control: dict[str, object], items: list[dict[str, object]]) -> tuple[list[str], str]:
    path = control["go_live_path"]
    path_ids = [item_id for phase in path["phases"] for item_id in phase["items"]]
    parallel_now = path["parallel_now"]
    agent_items = [item_id for item_id in path_ids if item_id not in parallel_now]
    focus_items = [agent_items[0], *parallel_now, *agent_items[1:2]]
    item_by_id = {item["id"]: item for item in items}
    human = ", ".join(f"{item_id} — {item_by_id[item_id]['item']}" for item_id in parallel_now)
    next_action = f"Agent: continue {agent_items[0]} — {item_by_id[agent_items[0]]['item']}."
    if human:
        next_action += f" Human in parallel: {human}."
    return focus_items, next_action + " Queue order does not authorize external actions."


def build_state() -> dict[str, object]:
    control = load_control()
    items = [dict(item) for item in control["items"]]
    focus_items, next_action = derive_focus_and_action(control, items)
    active_open = sum(item["status_code"] in OPEN_STATUSES for item in items)
    items.append(
        {
            "id": "G9",
            "gate": "9 · Frozen-source go/no-go decision",
            "item": "Product lead go/no-go decision",
            "status_code": "pending" if active_open else "complete",
            "status": "Not ready — required launch outcomes remain open." if active_open else "Ready — all required launch outcomes are closed.",
            "priority": "critical",
            "responsible_owner": "Product lead",
            "evidence_scope": "operator",
            "operator_boundary": "The product lead must record the final go/no-go decision.",
            **(
                {
                    "remaining_work": ["Close every required open item, then make the explicit go/no-go decision against the frozen release source."],
                    "completion_criteria": ["All required items are complete and the product lead records the release decision; deferred items remain outside the launch target."],
                    "blocked_by": f"{active_open} required checklist outcomes remain open.",
                }
                if active_open
                else {"completed_evidence": ["All required checklist outcomes are closed."]}
            ),
        }
    )
    areas = [dict(area) for area in control["areas"]]
    areas.append({"id": "decision", "label": "9 · Frozen-source go/no-go decision", "items": ["G9"]})
    counts = {status: sum(item["status_code"] == status for item in items) for status in STATUSES}
    return {
        "schema_version": "checklist.v1",
        "project": control["project"],
        "title": control["title"],
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "source_fingerprint": hashlib.sha256(CONTROL_PATH.read_bytes()).hexdigest(),
        "control_owner": ".session/checklist/checklist.json",
        "posture": "not_ready" if active_open else "ready",
        "counts": counts,
        "items": items,
        "areas": areas,
        "focus_items": focus_items,
        "go_live_path": {
            **{key: value for key, value in control["go_live_path"].items() if key != "phases"},
            "phases": [
                *[dict(phase) for phase in control["go_live_path"]["phases"][:-1]],
                {
                    **control["go_live_path"]["phases"][-1],
                    "items": [*control["go_live_path"]["phases"][-1]["items"], "G9"],
                },
            ]
        },
        "current_blocker": control["current_blocker"],
        "next_action": next_action,
        "warning": control["warning"],
        "operator_decisions": control["operator_decisions"],
    }


def load_renderer() -> ModuleType:
    spec = importlib.util.spec_from_file_location("checklist_framework_renderer", GLOBAL_RENDERER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load global checklist renderer: {GLOBAL_RENDERER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def substantive(value: dict[str, object]) -> dict[str, object]:
    return {key: item for key, item in value.items() if key != "generated_at"}


def check_current() -> None:
    expected = build_state()
    actual = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    if substantive(actual) != substantive(expected):
        raise ValueError("Checklist state is stale; run python3 scripts/generate_checklist.py")
    expected_testing = build_testing_data()
    actual_testing = json.loads(TESTING_PATH.read_text(encoding="utf-8"))
    if substantive(actual_testing) != substantive(expected_testing):
        raise ValueError("Testing links are stale; run python3 scripts/generate_checklist.py")
    load_renderer().check_current(ROOT)


def generate() -> None:
    renderer = load_renderer()
    state = build_state()
    renderer.validate(state)
    testing = build_testing_data()
    renderer.validate_testing(state, testing)
    atomic_write(STATE_PATH, json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    atomic_write(TESTING_PATH, json.dumps(testing, ensure_ascii=False, indent=2) + "\n")
    renderer.write(ROOT)


def self_check() -> None:
    control = load_control()
    state = build_state()
    assert "focus_items" not in control and "next_action" not in control
    assert state["control_owner"] == ".session/checklist/checklist.json"
    assert len({item["id"] for item in state["items"]}) == len(state["items"])
    assert {item["priority"] for item in state["items"]} <= set(PRIORITIES)
    path_ids = [item_id for phase in state["go_live_path"]["phases"] for item_id in phase["items"]]
    assert len(path_ids) == len(set(path_ids))
    parallel_now = state["go_live_path"]["parallel_now"]
    agent_items = [item_id for item_id in path_ids if item_id not in parallel_now]
    assert state["focus_items"] == [agent_items[0], *parallel_now, *agent_items[1:2]]
    in_force = [decision for decision in state["operator_decisions"] if decision["in_force"]]
    assert all(not decision["completes_item"] for decision in state["operator_decisions"])
    assert {decision["checklist_id"] for decision in in_force} <= {item["id"] for item in state["items"]}
    poisoned = json.loads(json.dumps(control))
    later = next(item_id for item_id in agent_items[1:] if item_id != "G9")
    next(item for item in poisoned["items"] if item["id"] == agent_items[0])["remaining_work"] = [f"Wait for {later}"]
    try:
        load_renderer().validate_queue_conflicts(poisoned["items"], poisoned["go_live_path"])
    except ValueError as error:
        assert "queue conflict" in str(error)
    else:
        raise AssertionError("live board accepted a forward queue wait")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-current", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        self_check()
        print("checklist exporter self-check passed")
    elif args.check_current:
        check_current()
        print("checklist state and HTML match checklist.json")
    else:
        generate()
        print(STATE_PATH)
        print(TESTING_PATH)
        print(ROOT / ".session/html/checklist.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
