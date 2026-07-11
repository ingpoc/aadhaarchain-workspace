"""One-shot Cursor agent prompts (gateway verification agents)."""
from __future__ import annotations

import os
import time
from typing import Any, Mapping, Optional

from .mcp import normalize_mcp_servers
from .policy import resolve_runtime_policy


def run_cursor_prompt(
    prompt: str,
    *,
    cwd: str,
    system_prompt: Optional[str] = None,
    mcp_servers: Optional[Mapping[str, Any]] = None,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    max_attempts: int = 3,
) -> tuple[str, Optional[str]]:
    """Run a single Cursor agent turn and return (text, error)."""
    policy = resolve_runtime_policy()
    if not policy.runtime_available:
        raise RuntimeError(policy.blocked_reason or "Cursor agent runtime is unavailable.")

    from cursor_sdk import Agent, AgentOptions, CursorAgentError, LocalAgentOptions, RateLimitError

    compiled = prompt
    if system_prompt:
        compiled = f"{system_prompt.strip()}\n\n{prompt}"

    key = (api_key or os.getenv("CURSOR_API_KEY") or "").strip()
    if not key:
        raise RuntimeError("CURSOR_API_KEY is required.")

    options = AgentOptions(
        api_key=key,
        model=model or policy.model,
        local=LocalAgentOptions(cwd=cwd, setting_sources=[]),
        mcp_servers=normalize_mcp_servers(mcp_servers),
    )

    last_error: Optional[Exception] = None
    for attempt in range(max_attempts):
        try:
            result = Agent.prompt(compiled, options)
            if result.status == "error":
                raise RuntimeError(f"Cursor agent run failed (run_id={result.id})")
            text = (result.result or "").strip()
            if not text:
                raise RuntimeError("Cursor agent returned empty content.")
            return text, None
        except RateLimitError as err:
            last_error = err
            delay = float(err.retry_after) if err.retry_after else 2**attempt
            time.sleep(delay)
        except CursorAgentError as err:
            last_error = err
            if not err.is_retryable:
                raise RuntimeError(str(err) or "Cursor agent run failed.") from err
            time.sleep(2**attempt)

    if last_error is not None:
        raise RuntimeError(str(last_error) or "Cursor agent run failed after retries.")
    raise RuntimeError("Cursor agent run failed after retries.")
