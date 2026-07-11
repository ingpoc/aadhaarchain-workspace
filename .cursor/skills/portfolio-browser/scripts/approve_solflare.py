#!/usr/bin/env python3
"""Approve Solflare extension popup (sign message / transaction).

Hermes cannot inject into chrome-extension:// popups. This script:
1. Finds the Chrome window named "Solflare" via AppleScript
2. Clicks the Approve button at computed coordinates (cliclick)

Usage:
  python3 .cursor/skills/portfolio-browser/scripts/approve_solflare.py
  python3 .cursor/skills/portfolio-browser/scripts/approve_solflare.py --reject
"""
from __future__ import annotations

import argparse
import subprocess
import sys


def applescript(script: str) -> str:
    proc = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "osascript failed")
    return proc.stdout.strip()


def solflare_bounds() -> tuple[int, int, int, int]:
    raw = applescript(
        '''
tell application "Google Chrome"
  repeat with w in windows
    if name of w is "Solflare" then
      set index of w to 1
      set b to bounds of w
      return (item 1 of b as text) & "," & (item 2 of b as text) & "," & (item 3 of b as text) & "," & (item 4 of b as text)
    end if
  end repeat
end tell
return "NOTFOUND"
'''
    )
    if raw == "NOTFOUND":
        raise RuntimeError('No Chrome window named "Solflare" — sign popup not open')
    parts = [int(x.strip()) for x in raw.split(",")]
    if len(parts) != 4:
        raise RuntimeError(f"Unexpected bounds: {raw!r}")
    return parts[0], parts[1], parts[2], parts[3]


def button_point(bounds: tuple[int, int, int, int], *, approve: bool) -> tuple[int, int]:
    left, top, right, bottom = bounds
    width = right - left
    height = bottom - top
    # Solflare popup: Reject left ~30%, Approve right ~72% x, ~90% y (validated manually)
    x_ratio = 0.72 if approve else 0.30
    y_ratio = 0.90
    return int(left + width * x_ratio), int(top + height * y_ratio)


def main() -> int:
    parser = argparse.ArgumentParser(description="Click Approve/Reject on Solflare Chrome popup")
    parser.add_argument("--reject", action="store_true", help="Click Reject instead of Approve")
    args = parser.parse_args()

    applescript('tell application "Google Chrome" to activate')
    bounds = solflare_bounds()
    x, y = button_point(bounds, approve=not args.reject)
    label = "Reject" if args.reject else "Approve"

    subprocess.run(["cliclick", f"c:{x},{y}"], check=True)
    print(f"clicked {label} at {x},{y} (window bounds {bounds})")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
