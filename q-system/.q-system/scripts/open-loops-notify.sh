#!/bin/bash
# Durable open-loops reminder, fired by a macOS launchd LaunchAgent (survives Claude
# exits/restarts -- the always-on backbone behind the in-session CronCreate push).
# If any open loop is tagged [needs you], pop a macOS desktop notification.
# Desktop only; a phone push needs Claude Remote Control (the CronCreate path covers that).
set -euo pipefail

REPO="${KIPI_REPO:-/Users/assafkipnis/projects/kipi-system}"
SCRIPT="$REPO/q-system/.q-system/scripts/open-loops.py"
[ -f "$SCRIPT" ] || exit 0

OUT="$(CLAUDE_PROJECT_DIR="$REPO" python3 "$SCRIPT" --report 2>/dev/null || true)"
COUNT="$(printf '%s\n' "$OUT" | grep -c '\[needs you\]' || true)"
[ "${COUNT:-0}" -gt 0 ] || exit 0   # nothing waiting -> silent

TITLES="$(printf '%s\n' "$OUT" | grep '\[needs you\]' \
  | sed -E 's/^- \[ \] (.*) \[needs you\].*/\1/' | paste -sd ', ' -)"
[ -n "$TITLES" ] || TITLES="open loops need you"

osascript -e "display notification \"${TITLES}\" with title \"Kipi: ${COUNT} waiting on you\" sound name \"Glass\"" >/dev/null 2>&1 || true
exit 0
