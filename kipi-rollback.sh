#!/bin/bash
set -euo pipefail

# kipi rollback [instance] -- revert the last skeleton-sync commit in one or all
# registered instances. (H3 from the claudesidian harvest brief.)
#
# Safe by construction (these are the load-bearing correctness rules, not polish):
#   - Finds the sync commit by MESSAGE-PREFIX (git log --grep), never `git revert HEAD`.
#     A later content commit may sit on top of the sync; reverting HEAD would undo the
#     WRONG commit. (PRD finding-1.)
#   - Uses `git revert` (non-destructive). Never a hard reset -- the founder's
#     destructive-op hook blocks that anyway, and revert is the correct primitive.
#   - Refuses on a dirty working tree (don't bury uncommitted work). (PRD finding-1.)
#   - On a revert CONFLICT, aborts cleanly (`git revert --abort`) and reports FAIL --
#     never leaves a half-applied revert (REVERT_HEAD + conflict markers). (PRD finding-7.)
#
# Instance-content safety holds BECAUSE kipi-update.sh's rsync --delete EXCLUDES
# my-project/, canonical/, memory/, output/, and bus/ -- so the sync commit never
# touched those dirs and reverting it cannot disturb founder state. (PRD finding-3.)
# If a future kipi-update.sh drops one of those --exclude lines, revisit this safety.

KIPI_HOME="$(cd "$(dirname "$(readlink -f "$0" 2>/dev/null || realpath "$0" 2>/dev/null || echo "$0")")" && pwd)"
REGISTRY="${KIPI_REGISTRY:-$KIPI_HOME/instance-registry.json}"
SYNC_PREFIX='^chore: sync q-system from skeleton'
ONLY="${1:-}"   # optional: scope rollback to a single instance by name

PASS=0; SKIP=0; FAIL=0

rollback_one() {
  local name="$1" path="$2" itype="${3:-subtree}"
  echo "--- $name ---"
  if [ ! -d "$path/.git" ]; then
    echo "  SKIP (not a git repo / path missing: $path)"; SKIP=$((SKIP+1)); return 0
  fi
  # most recent sync commit by message-prefix -- NOT HEAD
  local sync_sha
  sync_sha="$(git -C "$path" log --grep="$SYNC_PREFIX" --format=%H -n 1 2>/dev/null || true)"
  if [ -z "$sync_sha" ]; then
    if [ "$itype" = "direct-clone" ]; then
      echo "  SKIP (direct-clone: syncs via git pull from origin, no local sync commit -- roll back with git inside the instance)"
    else
      echo "  SKIP (no skeleton-sync commit to roll back)"
    fi
    SKIP=$((SKIP+1)); return 0
  fi
  # refuse over uncommitted work (tracked changes, staged or unstaged)
  if ! git -C "$path" diff --quiet 2>/dev/null || ! git -C "$path" diff --cached --quiet 2>/dev/null; then
    echo "  SKIP (dirty working tree -- commit or stash first; refusing to revert over uncommitted work)"
    SKIP=$((SKIP+1)); return 0
  fi
  local short
  short="$(git -C "$path" rev-parse --short "$sync_sha")"
  if git -C "$path" revert --no-edit "$sync_sha" >/dev/null 2>&1; then
    echo "  ROLLED BACK (reverted sync $short)"; PASS=$((PASS+1))
  else
    git -C "$path" revert --abort >/dev/null 2>&1 || true
    echo "  FAIL (revert of $short conflicted; aborted cleanly, instance left untouched)"; FAIL=$((FAIL+1))
  fi
}

while IFS='|' read -r name path itype; do
  [ -z "$name" ] && continue
  if [ -n "$ONLY" ] && [ "$name" != "$ONLY" ]; then continue; fi
  rollback_one "$name" "$path" "$itype"
  echo ""
done < <(python3 -c "
import json
d = json.load(open('$REGISTRY'))
for i in d['instances']:
    if 'status' in i and i['status'].startswith('merged'):
        continue
    print(i['name'] + '|' + i['path'] + '|' + i.get('type', 'subtree'))
")

if [ "$((PASS+SKIP+FAIL))" -eq 0 ]; then
  if [ -n "$ONLY" ]; then
    echo "No registered instance named '$ONLY'." >&2
    exit 1
  fi
  echo "No eligible instances in the registry."
  exit 0
fi

echo "=== Rollback Summary ==="
echo "  Rolled back: $PASS"
echo "  Skipped:     $SKIP"
echo "  Failed:      $FAIL"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
