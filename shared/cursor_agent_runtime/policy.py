"""Cursor SDK runtime policy — uses CURSOR_API_KEY from the user's subscription."""
from __future__ import annotations

import functools
import importlib.util
import os
from dataclasses import dataclass
from typing import Literal, Optional

AgentAuthMode = Literal["cursor_api_key", "unavailable"]

DEFAULT_MODEL = os.getenv("CURSOR_AGENT_MODEL", "composer-2.5")


@dataclass(frozen=True)
class AgentRuntimePolicy:
    runtime_available: bool
    auth_mode: AgentAuthMode
    model: str
    blocked_reason: Optional[str]
    cursor_api_key_configured: bool


def _sdk_package_available() -> bool:
    return importlib.util.find_spec("cursor_sdk") is not None


def _has_cursor_api_key() -> bool:
    return bool((os.getenv("CURSOR_API_KEY") or "").strip())


@functools.lru_cache(maxsize=1)
def resolve_runtime_policy() -> AgentRuntimePolicy:
    """Resolve whether Cursor SDK can run locally with the configured API key."""
    has_key = _has_cursor_api_key()
    model = (os.getenv("CURSOR_AGENT_MODEL") or DEFAULT_MODEL).strip() or DEFAULT_MODEL

    if not _sdk_package_available():
        return AgentRuntimePolicy(
            runtime_available=False,
            auth_mode="unavailable",
            model=model,
            blocked_reason="cursor-sdk is not installed. Run: pip install cursor-sdk",
            cursor_api_key_configured=has_key,
        )

    if not has_key:
        return AgentRuntimePolicy(
            runtime_available=False,
            auth_mode="unavailable",
            model=model,
            blocked_reason=(
                "CURSOR_API_KEY is required. Create one at "
                "https://cursor.com/dashboard/integrations"
            ),
            cursor_api_key_configured=False,
        )

    return AgentRuntimePolicy(
        runtime_available=True,
        auth_mode="cursor_api_key",
        model=model,
        blocked_reason=None,
        cursor_api_key_configured=True,
    )


def clear_runtime_policy_cache() -> None:
    resolve_runtime_policy.cache_clear()
