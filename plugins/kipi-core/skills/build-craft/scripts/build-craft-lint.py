#!/usr/bin/env python3
"""
build-craft-lint.py — Deterministic test-isolation enforcer.

Pairs with the build-craft skill (SKILL.md). Enforces the one mechanically
checkable slice of that skill's "verify against a copy, never the live resource"
rule: a TEST file must not connect/open a real data path. Tests use a temp copy,
a tempfile, or :memory:.

This is the graded-good Fable habit (it migrated a COPY of the live prod DB to
prove idempotency) turned into a consistent guardrail, because an independent
Codex review caught a sibling test stripping keys off the *live* founder DB.

Usage:
    python3 build-craft-lint.py <file_path>   # CLI mode
    (no args)                                 # hook mode: PostToolUse JSON on stdin

Exit codes:
    0 = clean (or out of scope)
    2 = violation (a test touches a non-isolated data path)

Override:
    Add  # build-craft-lint-skip  anywhere in the file to bypass.

Scope (fast-exit otherwise, token discipline):
    Fires only on a Python TEST file, detected by basename test_*.py / *_test.py
    or a path under a /tests/ directory. Non-test code and non-Python edits exit 0.
"""

import json
import re
import sys
from pathlib import Path

SKIP_MARKER = "build-craft-lint-skip"

# A path is isolated (safe in a test) if it names any of these.
ISOLATION_TOKENS = (
    ":memory:", "tmp", "temp", "fixture", "fixtures", "mock", "sample",
    "testdata", "test_data", "mktemp", "temporarydirectory", "tmp_path",
    "tmpdir", "/var/folders", "getfixturevalue", "monkeypatch",
)

# A captured path is a real data resource worth guarding if it looks like a DB
# file or lives under a data dir.
def _is_data_path(p):
    low = p.lower()
    return (
        low.endswith(".db")
        or low.endswith(".sqlite")
        or low.endswith(".sqlite3")
        or low.endswith(".duckdb")
        or "/data/" in low
    )


def _is_isolated(p):
    low = p.lower()
    return any(tok in low for tok in ISOLATION_TOKENS)


# connect("..."), sqlite3.connect("..."), db.connect("..."), duckdb.connect("...")
_CONNECT = re.compile(r"\bconnect\s*\(\s*([\"'])(.*?)\1")
# open("...")  -- first string arg
_OPEN = re.compile(r"\bopen\s*\(\s*([\"'])(.*?)\1")


def is_test_file(file_path):
    p = Path(str(file_path))
    if p.suffix != ".py":
        return False
    name = p.name
    if name.startswith("test_") or name.endswith("_test.py"):
        return True
    return "/tests/" in str(file_path).replace("\\", "/")


def find_violations(text):
    violations = []
    for rx, kind in ((_CONNECT, "connect"), (_OPEN, "open")):
        for m in rx.finditer(text):
            path = m.group(2)
            if not path:
                continue
            if _is_isolated(path):
                continue
            if _is_data_path(path):
                line = text[: m.start()].count("\n") + 1
                violations.append((line, kind, path))
    return violations


def lint_file(file_path):
    try:
        text = Path(file_path).read_text(encoding="utf-8")
    except Exception:
        # Never block a write on a read/infra failure; this is a content gate.
        return []
    if SKIP_MARKER in text:
        return []
    return find_violations(text)


def format_report(file_path, violations):
    lines = [f"build-craft-lint: {len(violations)} test-isolation violation(s) in {file_path}:"]
    for ln, kind, path in violations:
        lines.append(f"  [{kind}] line {ln}: test touches live data path \"{path}\"")
    lines.append(
        "Tests must use a temp copy, a tempfile, or :memory: — never a real data "
        "resource (build-craft skill: verify against a copy). "
        f"Fix it, or add  # {SKIP_MARKER}  to bypass."
    )
    return "\n".join(lines)


def hook_mode():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if payload.get("tool_name", "") not in ("Edit", "Write", "MultiEdit"):
        sys.exit(0)
    file_path = payload.get("tool_input", {}).get("file_path", "")
    if not file_path or not is_test_file(file_path):
        sys.exit(0)
    violations = lint_file(file_path)
    if not violations:
        sys.exit(0)
    print(format_report(file_path, violations), file=sys.stderr)
    sys.exit(2)


def cli_mode(file_path):
    if not is_test_file(file_path):
        print(f"build-craft-lint: out of scope (not a test file): {file_path}")
        sys.exit(0)
    violations = lint_file(file_path)
    if not violations:
        print(f"build-craft-lint: clean ({file_path})")
        sys.exit(0)
    print(format_report(file_path, violations))
    sys.exit(2)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        hook_mode()
    elif len(sys.argv) == 2:
        cli_mode(sys.argv[1])
    else:
        print("Usage: build-craft-lint.py <file_path>", file=sys.stderr)
        sys.exit(1)
