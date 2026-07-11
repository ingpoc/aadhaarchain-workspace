"""SSE-friendly streaming helpers for portfolio agent chat."""
from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Mapping, Optional

from .policy import resolve_runtime_policy


def _now_ms() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def _extract_assistant_text(message: Any) -> Optional[str]:
    if getattr(message, "type", None) != "assistant":
        return None
    body = getattr(message, "message", None)
    content = getattr(body, "content", None)
    if not isinstance(content, list):
        return None
    parts: list[str] = []
    for block in content:
        if getattr(block, "type", None) == "text":
            text = getattr(block, "text", None)
            if isinstance(text, str) and text:
                parts.append(text)
    combined = "".join(parts).strip()
    return combined or None


def _extract_text_delta(update: Any) -> Optional[str]:
    if getattr(update, "type", None) != "text_delta":
        return None
    text = getattr(update, "text", None)
    return text if isinstance(text, str) and text else None


async def stream_cursor_response(
    *,
    prompt: str,
    cwd: str,
    runtime_snapshot: Mapping[str, Any],
    session: Mapping[str, Any],
    system_prefix: str,
    resume_agent_id: Optional[str] = None,
) -> AsyncGenerator[dict[str, Any], None]:
    """Yield portfolio-compatible SSE events using the Cursor SDK."""
    yield {
        "type": "init",
        "session_id": session.get("session_id"),
        "sdk_session_id": resume_agent_id or session.get("sdk_session_id"),
        "mode": session.get("mode"),
    }

    if not runtime_snapshot.get("runtime_available") or session.get("mode") == "blocked":
        yield {
            "type": "error",
            "error": runtime_snapshot.get("blocked_reason") or "Cursor agent runtime is unavailable.",
            "timestamp": _now_ms(),
        }
        return

    policy = resolve_runtime_policy()
    if not policy.runtime_available:
        yield {
            "type": "error",
            "error": policy.blocked_reason or "Cursor agent runtime is unavailable.",
            "timestamp": _now_ms(),
        }
        return

    from cursor_sdk import Agent, AgentOptions, CursorAgentError, LocalAgentOptions, RateLimitError

    api_key = (os.getenv("CURSOR_API_KEY") or "").strip()
    compiled_prompt = (
        f"{system_prefix.strip()}\n\n"
        f"User request: {prompt}"
    )
    agent_id = resume_agent_id or session.get("sdk_session_id")

    try:
        options = AgentOptions(
            api_key=api_key,
            model=runtime_snapshot.get("model") or policy.model,
            local=LocalAgentOptions(cwd=cwd, setting_sources=[]),
            agent_id=agent_id if isinstance(agent_id, str) else None,
        )

        def _run_stream() -> tuple[str, Optional[str], list[str]]:
            deltas: list[str] = []
            final_text = ""
            resolved_agent_id: Optional[str] = None

            if agent_id:
                with Agent.resume(agent_id, options) as agent:
                    resolved_agent_id = agent.agent_id
                    run = agent.send(compiled_prompt)
                    for message in run.messages():
                        delta = _extract_text_delta(message)
                        if delta:
                            deltas.append(delta)
                        text = _extract_assistant_text(message)
                        if text:
                            final_text = text
                    result = run.wait()
                    if result.status == "error":
                        raise RuntimeError(f"Cursor agent run failed (run_id={result.id})")
                    if not final_text and result.result:
                        final_text = str(result.result).strip()
            else:
                with Agent.create(options) as agent:
                    resolved_agent_id = agent.agent_id
                    run = agent.send(compiled_prompt)
                    for message in run.messages():
                        delta = _extract_text_delta(message)
                        if delta:
                            deltas.append(delta)
                        text = _extract_assistant_text(message)
                        if text:
                            final_text = text
                    result = run.wait()
                    if result.status == "error":
                        raise RuntimeError(f"Cursor agent run failed (run_id={result.id})")
                    if not final_text and result.result:
                        final_text = str(result.result).strip()

            if not final_text:
                final_text = "".join(deltas).strip()
            if not final_text:
                raise RuntimeError("Cursor agent returned no assistant content.")
            return final_text, resolved_agent_id, deltas

        final_text, resolved_agent_id, deltas = await asyncio.to_thread(_run_stream)

        for delta in deltas:
            yield {
                "type": "assistant_delta",
                "content": delta,
                "timestamp": _now_ms(),
            }

        yield {
            "type": "result",
            "content": final_text,
            "sdk_session_id": resolved_agent_id,
            "estimated_cost_usd": None,
            "timestamp": _now_ms(),
        }
    except (CursorAgentError, RuntimeError) as exc:
        yield {
            "type": "error",
            "error": str(exc) or "Cursor agent runtime failed to process the request.",
            "timestamp": _now_ms(),
        }
    except Exception as exc:
        yield {
            "type": "error",
            "error": str(exc) or "Cursor agent runtime failed to process the request.",
            "timestamp": _now_ms(),
        }
