#!/usr/bin/env python3
"""
voice-stop-gate.py - Final voice check on assistant chat output.

Stop hook for Claude Code.

The voice-lint PostToolUse hook only fires on file writes. Most voice
failures happen in chat output — drafts I produce for the founder to
copy-paste into X, LinkedIn, email, DMs. None of those reach a file.

This hook closes that gap. At turn end, it reads the transcript, finds
the assistant's final message text, writes it to a temp file, runs the
full voice-lint check on it, and exits 2 if violations are found. Claude
must then re-draft before the turn can complete.

Pairs with voice-substance-lint.py for positive-pattern enforcement.

Stdlib only. Reuses voice-lint.py and voice-substance-lint.py via subprocess.

Exit codes:
    0 = clean (turn completes)
    2 = violation (turn blocked, Claude must re-draft)
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parent
VOICE_LINT = SCRIPTS_DIR / "voice-lint.py"
SUBSTANCE_LINT = SCRIPTS_DIR / "voice-substance-lint.py"

MIN_TEXT_BYTES = 80


def find_final_assistant_text(transcript_path):
    if not transcript_path or not Path(transcript_path).exists():
        return ""
    text_parts = []
    for line in Path(transcript_path).read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except Exception:
            continue
        message = record.get("message", {})
        if not isinstance(message, dict):
            continue
        if message.get("role") != "assistant":
            continue
        text_parts = []
        for item in message.get("content", []):
            if isinstance(item, dict) and item.get("type") == "text":
                text = item.get("text", "")
                if text:
                    text_parts.append(text)
            elif isinstance(item, str):
                text_parts.append(item)
    return "\n\n".join(text_parts)


def run_check(script, file_path):
    if not script.exists():
        return (0, "")
    try:
        result = subprocess.run(
            ["python3", str(script), file_path],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return (result.returncode, result.stdout + result.stderr)
    except subprocess.TimeoutExpired:
        return (1, f"voice-stop-gate: {script.name} timed out")


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    transcript_path = payload.get("transcript_path", "")
    text = find_final_assistant_text(transcript_path)
    if len(text.encode("utf-8")) < MIN_TEXT_BYTES:
        sys.exit(0)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(text)
        tmp_path = tmp.name
    try:
        violations_output = []
        code1, out1 = run_check(VOICE_LINT, tmp_path)
        if code1 == 2 and out1:
            violations_output.append(out1)
        code2, out2 = run_check(SUBSTANCE_LINT, tmp_path)
        if code2 == 2 and out2:
            violations_output.append(out2)
        if violations_output:
            sys.stderr.write(
                "voice-stop-gate: assistant final message has voice violations.\n"
                "Re-draft before completing the turn.\n\n"
            )
            for output in violations_output:
                sys.stderr.write(output + "\n")
            sys.exit(2)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
    sys.exit(0)


if __name__ == "__main__":
    main()
