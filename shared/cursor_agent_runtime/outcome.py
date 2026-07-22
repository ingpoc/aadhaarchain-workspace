"""Fail-closed completion contract for background runtime work."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Iterable, Mapping


class RuntimeOutcomeError(ValueError):
    """Raised when an agent response cannot prove that requested work completed."""


@dataclass(frozen=True)
class VerifiedRuntimeOutcome:
    summary: str
    executed_tools: tuple[str, ...]
    postcondition_evidence: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": "completed",
            "summary": self.summary,
            "executed_tools": list(self.executed_tools),
            "postcondition": {
                "verified": True,
                "evidence": self.postcondition_evidence,
            },
        }


def completed_tool_names(messages: Iterable[Any]) -> tuple[str, ...]:
    """Return completed Cursor SDK tool names observed by the gateway."""
    names: list[str] = []
    for message in messages:
        if getattr(message, "type", None) != "tool_call":
            continue
        if getattr(message, "status", None) != "completed":
            continue
        name = getattr(message, "name", None)
        if isinstance(name, str) and name.strip():
            names.append(name.strip())
    return tuple(names)


def parse_verified_runtime_outcome(
    content: str,
    *,
    observed_completed_tools: Iterable[str],
) -> VerifiedRuntimeOutcome:
    """Validate model output against tool calls observed by the SDK stream."""
    try:
        payload = json.loads(content)
    except (TypeError, json.JSONDecodeError) as exc:
        raise RuntimeOutcomeError(
            "The runtime returned narrative text without verifiable completion evidence."
        ) from exc

    if not isinstance(payload, Mapping) or payload.get("status") != "completed":
        raise RuntimeOutcomeError("The runtime did not report a completed structured outcome.")

    summary = payload.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        raise RuntimeOutcomeError("The runtime completion summary is missing.")

    declared_tools = payload.get("executed_tools")
    if not isinstance(declared_tools, list) or not declared_tools:
        raise RuntimeOutcomeError("The runtime did not declare executed tool evidence.")
    if not all(isinstance(name, str) and name.strip() for name in declared_tools):
        raise RuntimeOutcomeError("The runtime tool evidence is malformed.")

    observed = {name.strip() for name in observed_completed_tools if name.strip()}
    declared = tuple(dict.fromkeys(name.strip() for name in declared_tools))
    if not observed or any(name not in observed for name in declared):
        raise RuntimeOutcomeError(
            "The runtime completion was not backed by completed SDK tool calls."
        )

    postcondition = payload.get("postcondition")
    if not isinstance(postcondition, Mapping) or postcondition.get("verified") is not True:
        raise RuntimeOutcomeError("The runtime did not verify the requested postcondition.")
    evidence = postcondition.get("evidence")
    if not isinstance(evidence, str) or not evidence.strip():
        raise RuntimeOutcomeError("The runtime postcondition evidence is missing.")

    return VerifiedRuntimeOutcome(
        summary=summary.strip()[:280],
        executed_tools=declared,
        postcondition_evidence=evidence.strip()[:500],
    )
