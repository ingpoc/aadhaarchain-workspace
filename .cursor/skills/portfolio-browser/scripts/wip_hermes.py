"""AadhaarChain portfolio → Hermes Chrome **WIP only** (never Codex live)."""
from __future__ import annotations

import importlib.util
import os
import pathlib

WIP_ROOT = pathlib.Path(
    os.environ.get(
        "HERMES_CHROME_WIP_ROOT",
        "/Users/gurusharan/plugins/hermes-chrome-cursor-wip",
    )
)
WIP_TOOLS = WIP_ROOT / "plugin" / "hermes_chrome" / "tools.py"
WIP_SOCKET = WIP_ROOT / "run" / "chrome-bridge.sock"
WIP_SYNC = WIP_ROOT / "scripts" / "sync-wip.sh"


def ensure_wip_env() -> pathlib.Path:
    """Force WIP socket before importing tools.py (module reads env at import)."""
    if not WIP_TOOLS.is_file():
        raise RuntimeError(f"WIP Hermes tools missing: {WIP_TOOLS}")
    os.environ["HERMES_CHROME_BRIDGE_SOCKET"] = str(WIP_SOCKET)
    os.environ["HERMES_CHROME_WIP_ROOT"] = str(WIP_ROOT)
    return WIP_SOCKET


def load_handler():
    """Load WIP plugin/hermes_chrome/tools.py with WIP socket env set."""
    ensure_wip_env()
    spec = importlib.util.spec_from_file_location("hermes_chrome_wip_tools", WIP_TOOLS)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load WIP Hermes plugin at {WIP_TOOLS}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
