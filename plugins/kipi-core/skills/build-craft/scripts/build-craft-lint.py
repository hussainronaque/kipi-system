#!/usr/bin/env python3
"""
build-craft-lint.py — Deterministic test-isolation enforcer.

Pairs with the build-craft skill (SKILL.md). Enforces the one mechanically
checkable slice of that skill's "verify against a copy, never the live resource"
rule: a TEST file must not name a real data path. Tests use a temp copy, a
tempfile, or :memory:.

This is the graded-good Fable habit (it migrated a COPY of the live prod DB to
prove idempotency) turned into a consistent guardrail, because an independent
Codex review caught a sibling test risking mutation of the live founder DB.

Usage:
    python3 build-craft-lint.py <file_path>   # CLI mode
    (no args)                                 # hook mode: PostToolUse JSON on stdin

Exit codes:
    0 = clean (or out of scope)
    2 = violation (a test names a non-isolated data path)

Override:
    Add  # build-craft-lint-skip  anywhere in the file to bypass.

Detector coverage (enumerated on purpose, per the hook-blind-spots rule):
    CATCHES  a string literal that looks like a real DB path — has a path
             separator AND a DB extension (.db/.sqlite/.sqlite3/.duckdb) — and is
             not isolated, whether it sits directly in connect("...")/open("...")
             or is assigned to a variable that is passed on. The separator
             requirement is what lets `tmp_path / "t.db"` through: the bare
             filename "t.db" has no separator, and isolation lives in the temp
             variable, not the literal.
    MISSES   a no-argument default call like db.connect() that uses a module-level
             live DB_PATH. There is no literal to see. This is left to the skill
             (use the monkeypatch-the-default convention) on purpose: a generic
             no-arg detector false-positives on non-DB .connect() calls
             (websockets, mocks) across instances.

Scope (fast-exit otherwise, token discipline):
    Fires only on a Python TEST file, detected by basename test_*.py / *_test.py
    or a path under a /tests/ directory. Non-test code and non-Python edits exit 0.
"""

import json
import re
import sys
from pathlib import Path

SKIP_MARKER = "build-craft-lint-skip"

# A path literal is isolated (safe in a test) if it names any of these.
ISOLATION_TOKENS = (
    ":memory:", "tmp", "temp", "fixture", "fixtures", "mock", "sample",
    "testdata", "test_data", "mktemp", "temporarydirectory", "tmp_path",
    "tmpdir", "/var/folders", "getfixturevalue", "monkeypatch",
)

DB_EXTS = (".db", ".sqlite", ".sqlite3", ".duckdb")

# Simple single-line string literal (good enough; triple-quote bodies are skipped).
_STR = re.compile(r"(['\"])(.*?)\1")

# A live-DB literal only matters in a connect/open/copy call or a variable
# assignment. In an assertion or comparison it is just a string being checked
# (e.g. an OSS-secrets audit test asserting the live path is NAMED in a report),
# so those lines are skipped to avoid false positives.
CALL_CONTEXTS = (
    "connect(", "open(", "init_db(", "sqlite3", "duckdb",
    "write_text", "read_text", "copyfile", "copy2", "shutil.copy", ".copy(",
)
_ASSIGN = re.compile(r"^\s*[A-Za-z_][\w.]*\s*(?::[^=]+)?=(?!=)\s*")


def _is_isolated(p):
    low = p.lower()
    return any(tok in low for tok in ISOLATION_TOKENS)


def _is_live_db_path(p):
    """A real live-DB path literal: a path separator AND a DB extension.

    The separator requirement avoids flagging a bare filename fragment joined to
    a temp base (e.g. tmp_path / "t.db"), where the isolation lives in the
    variable, not the literal."""
    low = p.lower()
    if "/" not in low and "\\" not in low:
        return False
    return low.endswith(DB_EXTS)


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
    in_doc = False
    delim = None
    seen = set()
    for i, line in enumerate(text.splitlines(), 1):
        if in_doc:
            if delim in line:
                in_doc = False
                delim = None
            continue
        if line.lstrip().startswith("#"):
            continue
        # enter a triple-quoted block if one opens and does not close this line
        for q in ('"""', "'''"):
            if line.count(q) % 2 == 1:
                in_doc = True
                delim = q
                break
        if line.lstrip().startswith("assert"):
            continue
        if not (any(c in line for c in CALL_CONTEXTS) or _ASSIGN.match(line)):
            continue
        for m in _STR.finditer(line):
            path = m.group(2)
            if not path or _is_isolated(path):
                continue
            if _is_live_db_path(path):
                key = (i, path)
                if key not in seen:
                    seen.add(key)
                    violations.append((i, path))
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
    for ln, path in violations:
        lines.append(f"  line {ln}: test names a live data path \"{path}\"")
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
