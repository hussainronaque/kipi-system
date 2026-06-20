---
id: prd-claudesidian-finish-2026-06-20
title: Claudesidian Finish
status: archived
created_at: 2026-06-20T05:11:08Z
updated_at: 2026-06-20T05:31:02Z
owner: assafkip
reviewers: []
findings_path: .prd-os/findings/prd-claudesidian-finish-2026-06-20-findings.jsonl
codex_reviewed_at: 2026-06-20T05:16:17Z
---

# Claudesidian Finish

## Problem

The claudesidian harvest (canonical brief, entry #001) defined H0-H15 additions
for kipi. This session already shipped H0, H1, H2, H4, H5, H7, H10, H13, and the
"worth mentioning/noting" slice of H8. A ground-truth verification pass (7 agents,
each reading the real files) confirmed the remaining items and graded them:

- **H3 (rollback verb):** ABSENT. `kipi` dispatcher has no `rollback`; the sync
  commit `chore: sync q-system from skeleton <date>` (kipi-update.sh:141) is the
  revert target, and the pre-sync `chore: auto-commit before kipi update`
  (line 72) must stay intact. Worth building as a thin, safe wrapper.
- **H8-remainder (emphasis openers) + H9 (rhetorical-Q-then-answer):** ABSENT.
  Sentence-initial "Importantly,"/"Notably,"/"Crucially,"/"Significantly," and the
  "X? Y." setup-and-reveal are uncaught by voice-lint.py. The linter already has a
  fully-wired WARN tier (WARN_RULES frozenset + _partition, exit 0 advisory), so
  the prior "too false-positive-prone to block" objection dissolves: ship both as
  WARN-class, not BLOCK.

Deferred after verification (documented in the brief ledger, NOT in this PRD):
H6 (resumable manifest — fleet of 18 is local/fast/idempotent, doesn't earn the
complexity until ~50), H11 (skill-discovery hook — kipi's semantic auto-invoke
already beats a literal-"skill" trigger), H12 (benchmark — already dropped in the
Goal-2 brief, expensive, non-deterministic scoring). Cross-repo H14/H15 need
explicit founder sign-off (separate kipi-investigations repo).

## Goals

- `kipi rollback [instance]` reverts the last skeleton-sync commit safely (git revert by message-prefix, never reset --hard), leaving instance-preserved dirs and the pre-sync snapshot commit untouched.
- voice-lint.py flags sentence-initial emphasis openers and rhetorical-question-then-answer pairs as WARN (advisory, exit 0), not BLOCK.
- Every shipped item has a reproducer test that is green before closeout.

## Non-goals

- No H6 / H11 / H12 (deferred with documented reasons in the brief ledger).
- No edits to kipi-investigations (H14/H15 are a separate repo + a separate founder decision).
- No change to the existing BLOCK-tier voice rules. The two new WARN detectors land on the voice-lint.py Edit-hook path ONLY, not the second voice path in the kipi-mcp linter (plugins/kipi-core/kipi-mcp/src/kipi_mcp/). That is a DELIBERATE coverage choice, not an oversight: the MCP linter has no WARN tier (binary pass/fail), so adding these heuristic detectors there would hard-fail drafts. Documented gap; revisit if the MCP linter gains a WARN tier.
- No `git reset --hard` / branch deletion anywhere (forced onto `git revert` by the destructive-op hook and by correctness).

## Proposed approach

**H3:** new `kipi-rollback.sh` (root-level, sibling of `kipi-update.sh`) + a
`rollback)` case in the `kipi` dispatcher + a usage line. The script walks the
same registry filter as kipi-update.sh, or scopes to one instance by name. Per
target: locate the sync commit by `git log --grep='^chore: sync q-system from
skeleton' --format=%H -n 1` (message-prefix, NOT HEAD — a content commit may sit
on top), skip if none, refuse on a dirty tree, `git revert --no-edit <sha>`, leave
the pre-sync auto-commit intact. Fixture-instance test.

**H8b+H9:** two new WARN-class functions in voice-lint.py —
`check_emphasis_opener()` (regex anchored to sentence-initial position + trailing
comma) and `check_rhetorical_qa()` (short `?`-ending sentence followed by a short
or connector-led answer, with reader-directed-question suppression and `#`-heading
skip). Both rule names go in the WARN_RULES frozenset so they exit 0. Wire both
into lint_file(). One test with should-flag + should-not-flag fixtures for each.

## Risks and rollback

- **H3 wrong-commit revert** if implemented as `git revert HEAD` — mitigated by message-prefix lookup. Dirty-tree conflict — mitigated by a refuse guard. Rollback of the verb itself: `git revert` the commit; it adds files, removes nothing.
- **voice-lint false positives** — both rules are WARN-only, so a stray hit costs a stderr line, never a blocked edit. Must use a NEW rule name in WARN_RULES; riding `banned-phrase` would invert to BLOCK.
- Blast radius is small: one new script + one dispatcher case + two isolated lint functions. No data path, no migration.

## Open questions

- None blocking. H6/H11 can be added later if the founder wants them despite the marginal grade.

## Issues

```json
[
  {
    "id": "kipi-rollback-verb",
    "title": "H3: kipi rollback [instance] - safe revert of the last skeleton sync",
    "priority": "p2",
    "finding_id": "finding-1",
    "allowed_files": [
      "kipi",
      "kipi-rollback.sh",
      "UPDATE.md",
      "q-system/.q-system/scripts/test/test-kipi-rollback.sh"
    ],
    "required_checks": [
      "bash q-system/.q-system/scripts/test/test-kipi-rollback.sh"
    ],
    "bypass_check": "bash q-system/.q-system/scripts/test/test-kipi-rollback.sh",
    "acceptance": "kipi rollback [instance] reverts ONLY the 'chore: sync q-system from skeleton' commit found by message-prefix (not HEAD). Revert-safety holds BECAUSE the sync diff is scoped to non-preserved paths (kipi-update.sh rsync --delete excludes my-project/canonical/memory/output/bus). Test asserts the TRACKED preserved files (my-project/, canonical/, memory/) are byte-identical after rollback; gitignored output/bus are NOT asserted (they cannot be in a commit). The pre-sync 'chore: auto-commit before kipi update' commit survives. Dirty tree refuses BEFORE revert; on a git-revert CONFLICT during revert the script runs git revert --abort and reports, never leaving a half-applied revert. No hard reset. Fixture test green for: happy-path revert, dirty-tree-refuses, and revert-conflict-aborts-cleanly."
  },
  {
    "id": "voice-lint-warn-detectors",
    "title": "H8b+H9: emphasis-opener + rhetorical-QA WARN detectors in voice-lint",
    "priority": "p2",
    "finding_id": "finding-2",
    "allowed_files": [
      "q-system/.q-system/scripts/voice-lint.py",
      "q-system/.q-system/scripts/test/test-voice-lint-warn-detectors.sh"
    ],
    "required_checks": [
      "bash q-system/.q-system/scripts/test/test-voice-lint-warn-detectors.sh"
    ],
    "bypass_check": "bash q-system/.q-system/scripts/test/test-voice-lint-warn-detectors.sh",
    "acceptance": "Sentence-initial 'Importantly,'/'Notably,'/'Crucially,'/'Significantly,' and a short rhetorical question answered by the next short sentence each emit a violation with a NEW rule name that is in WARN_RULES (exit 0, advisory); mid-sentence 'significantly faster' and a real reader-directed question do NOT flag; the kipi-mcp linter is untouched; and the test asserts WARN_RULES membership is unchanged except the two new rule names (no existing rule re-tiered)."
  }
]
```
