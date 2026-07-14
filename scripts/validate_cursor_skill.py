#!/usr/bin/env python3
"""Deterministic validation for the repository-owned Cursor skills."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / ".cursor" / "skills"
AUDIT = Path.home() / ".codex" / "skills" / "create-skill" / "scripts" / "audit.py"

REQUIRED_MARKERS: dict[str, tuple[str, ...]] = {
    "apisetu-partner-onboarding": (
        'semantic `locator`',
        "Use `testId` (camel case)",
        "token-nxt-curated-answers.md",
    ),
    "authentication": (
        "scripts/hermes_demo_sso.py buyer|seller",
        "principal:demo:",
        "PYTHONPATH=. .venv/bin/pytest",
    ),
    "demo-video-recording": (
        "button named `Open Samantha`",
        '"testId": "samantha-orb-text"',
        "references/evidence/README.md",
    ),
    "ondc-testing": (
        "started → heartbeat → completed",
        "scripts/hermes_ondc_testing_matrix.py",
        'semantic `locator` actions',
    ),
    "portfolio-browser": (
        "native `network_watch`",
        "native `console_tail`",
        "scripts/hermes_ondc_testing_matrix.py buyer|seller",
    ),
    "portfolio-deploy": (
        "Validation is read-only/offline and never deploys",
        "scripts/ondc_ci_graders.py --offline",
        "HARD POLICY: always free tier",
    ),
}

FORBIDDEN_GUIDANCE = (
    "prefer `evaluate` for SPA click",
    "use `evaluate` value-setter",
    "install console hooks after goto",
    "no `portfolio_browser` subcommand yet",
    "workflow-hardening",
    "button[data-testid=samantha-orb]",
)


def run(command: list[str], *, cwd: Path = ROOT) -> None:
    print(f"$ {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def syntax_check(paths: list[Path]) -> None:
    for path in paths:
        source = path.read_text(encoding="utf-8")
        compile(source, str(path), "exec")
    print(f"python syntax: {len(paths)} file(s) clean")


def audit_skill(skill_dir: Path) -> None:
    if not AUDIT.is_file():
        raise SystemExit(f"missing create-skill audit: {AUDIT}")
    completed = subprocess.run(
        [sys.executable, str(AUDIT), str(skill_dir), "--strict", "--json"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    if completed.stderr:
        print(completed.stderr, file=sys.stderr, end="")
    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"skill audit returned invalid JSON: {exc}") from exc
    hard = int(report.get("total_hard", 0))
    soft = int(report.get("total_soft", 0))
    if completed.returncode or hard or soft:
        print(completed.stdout)
        raise SystemExit(
            f"skill audit failed: exit={completed.returncode} hard={hard} soft={soft}"
        )
    print("create-skill audit: clean")


def validate_guidance(name: str, skill_dir: Path) -> None:
    markdown = []
    for path in skill_dir.rglob("*.md"):
        if "evidence" in path.parts:
            continue
        markdown.append(path.read_text(encoding="utf-8"))
    corpus = "\n".join(markdown)
    missing = [marker for marker in REQUIRED_MARKERS[name] if marker not in corpus]
    stale = [marker for marker in FORBIDDEN_GUIDANCE if marker.casefold() in corpus.casefold()]
    if missing or stale:
        for marker in missing:
            print(f"missing required marker: {marker}", file=sys.stderr)
        for marker in stale:
            print(f"stale guidance remains: {marker}", file=sys.stderr)
        raise SystemExit(1)
    print("owner guidance: clean")


def validate_domain(name: str) -> None:
    if name == "apisetu-partner-onboarding":
        syntax_check([ROOT / "scripts" / "ondc_preprod_smoke.py"])
    elif name == "authentication":
        run(
            [
                "env",
                "PYTHONPATH=.",
                "PYTHONDONTWRITEBYTECODE=1",
                ".venv/bin/pytest",
                "-q",
                "-p",
                "no:cacheprovider",
                "tests/test_oauth_state.py",
                "tests/test_session_cookie_flags.py",
                "tests/test_social_auth.py",
            ],
            cwd=ROOT / "aadharchain" / "gateway",
        )
    elif name == "demo-video-recording":
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            raise SystemExit("ffmpeg is required for the recording skill")
        print(f"ffmpeg: {ffmpeg}")
    elif name == "ondc-testing":
        syntax_check(
            [
                ROOT / "scripts" / "hermes_demo_sso.py",
                ROOT / "scripts" / "hermes_ondc_testing_matrix.py",
                ROOT / "scripts" / "ondc_preprod_smoke.py",
            ]
        )
        run(["env", "PYTHONDONTWRITEBYTECODE=1", sys.executable, "scripts/ondc_ci_graders.py", "--offline"])
    elif name == "portfolio-browser":
        browser_scripts = sorted((SKILLS_ROOT / name / "scripts").glob("*.py"))
        syntax_check(browser_scripts)
    elif name == "portfolio-deploy":
        run(["env", "PYTHONDONTWRITEBYTECODE=1", sys.executable, "scripts/ondc_ci_graders.py", "--offline"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("skill", choices=sorted(REQUIRED_MARKERS))
    args = parser.parse_args()
    skill_dir = SKILLS_ROOT / args.skill
    audit_skill(skill_dir)
    validate_guidance(args.skill, skill_dir)
    validate_domain(args.skill)
    print(f"PASS: {args.skill}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
