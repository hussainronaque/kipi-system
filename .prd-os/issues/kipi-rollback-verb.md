---
id: kipi-rollback-verb
title: H3: kipi rollback [instance] - safe revert of the last skeleton sync
status: closed
priority: p2
parent_prd: prd-claudesidian-finish-2026-06-20
allowed_files:
  - kipi
  - kipi-rollback.sh
  - UPDATE.md
  - q-system/.q-system/scripts/test/test-kipi-rollback.sh
disallowed_files: []
required_checks:
  - bash q-system/.q-system/scripts/test/test-kipi-rollback.sh
required_reviews: []
bypass_check: "bash q-system/.q-system/scripts/test/test-kipi-rollback.sh"
---
<!-- generated-by: prd_split.py prd=prd-claudesidian-finish-2026-06-20 finding=finding-1 at=2026-06-20T05:17:02Z -->

# H3: kipi rollback [instance] - safe revert of the last skeleton sync

## Context

Parent PRD: `.prd-os/prds/prd-claudesidian-finish-2026-06-20.md`

## Acceptance

kipi rollback [instance] reverts ONLY the 'chore: sync q-system from skeleton' commit found by message-prefix (not HEAD). Revert-safety holds BECAUSE the sync diff is scoped to non-preserved paths (kipi-update.sh rsync --delete excludes my-project/canonical/memory/output/bus). Test asserts the TRACKED preserved files (my-project/, canonical/, memory/) are byte-identical after rollback; gitignored output/bus are NOT asserted (they cannot be in a commit). The pre-sync 'chore: auto-commit before kipi update' commit survives. Dirty tree refuses BEFORE revert; on a git-revert CONFLICT during revert the script runs git revert --abort and reports, never leaving a half-applied revert. No hard reset. Fixture test green for: happy-path revert, dirty-tree-refuses, and revert-conflict-aborts-cleanly.
