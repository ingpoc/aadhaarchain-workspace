"""Normalize MCP server configs for the Cursor Python SDK."""
from __future__ import annotations

from typing import Any, Mapping, Optional


def normalize_mcp_servers(
    mcp_servers: Optional[Mapping[str, Any]],
) -> dict[str, Any]:
    """Convert legacy stdio dict configs into Cursor SDK StdioMcpServerConfig objects."""
    if not mcp_servers:
        return {}

    from cursor_sdk import StdioMcpServerConfig

    normalized: dict[str, Any] = {}
    for name, config in mcp_servers.items():
        if config is None:
            continue
        if isinstance(config, StdioMcpServerConfig):
            normalized[name] = config
            continue
        if not isinstance(config, dict):
            continue
        if config.get("type") not in {None, "stdio"}:
            continue
        command = config.get("command")
        if not isinstance(command, str) or not command.strip():
            continue
        args = config.get("args") or []
        if not isinstance(args, list):
            args = []
        env = config.get("env")
        normalized[name] = StdioMcpServerConfig(
            command=command,
            args=args,
            env=env if isinstance(env, dict) else None,
        )
    return normalized
