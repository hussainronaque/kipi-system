---
id: prd-prdos-propagation-contract-docs-2026-05-14
title: Document and verify the prd-os artifact propagation contract
status: archived
created_at: 2026-05-14T16:45:24Z
updated_at: 2026-05-14T16:51:01Z
owner: assaf
reviewers: []
findings_path: .prd-os/findings/prd-prdos-propagation-contract-docs-2026-05-14-findings.jsonl
codex_reviewed_at: 2026-05-14T16:50:52Z
---

# Document and verify the prd-os artifact propagation contract

## Problem

After committing the planning-personas + prd-os infrastructure work (commits `fa75eb7` and `00ecd8f`), a wiring check raised a concern: `q-system/memory/working/prd-personas-baseline.md` lives in the propagated tree, so `kipi update` would supposedly overwrite an instance's locally-appended measurement rows when `phase0_measure.py` runs.

Investigation showed the concern was wrong. `kipi-update.sh` line 110 already excludes `memory/` from the rsync:

```
--exclude="my-project/" \
--exclude="canonical/" \
--exclude="memory/" \
--exclude="output/" \
--exclude=".q-system/agent-pipeline/bus/" 2>/dev/null
```

The baseline file is therefore NOT propagated. `phase0_measure.py` appending to it is safe.

The real gap is that the contract is invisible. Future readers (or future-me reviewing in six months) see a file at a path under `q-system/` and assume it propagates, then reason about it incorrectly. The wiring report I produced today raised exactly that worry until I read the rsync flags. Documentation closes the gap. A regression test prevents the contract from silently breaking if someone removes an exclusion from `kipi-update.sh`.

## Goals

**Primary outcome (single success metric, addressing finding-2):**

After this PRD is archived, both of the following hold:
1. `grep -q "Propagation contract" q-system/memory/working/prd-personas-baseline.md` returns 0.
2. `pytest -q plugins/prd-os/tests/test_propagation.py` passes.

The `kipi update --dry` check is dropped from the success metric (per finding-2): it depends on instance fixture state we can't pin deterministically, and the regression test already proves the same contract more rigorously. End-to-end behavior is verified by the test, not by a manual dry-run.

Supporting outcomes:
- `phase0_measure.py` module docstring cross-references `kipi-update.sh` so the propagation contract is discoverable from the writer too.
- A regression test reads `kipi-update.sh` directly and asserts the exclusion list contains `memory/`, `output/`, and `my-project/`. Catches the failure mode where someone removes an exclusion in a different PR without updating the contract elsewhere.

## Non-goals

- Moving `prd-personas-baseline.md` to a different path. The current path is correct; only the documentation was missing.
- Modifying `kipi-update.sh` exclusion list. It is already correct.
- Auditing every other prd-os artifact for propagation status. This PRD covers one file's contract; a broader propagation audit is a separate spike.
- Adding a runtime check in `phase0_measure.py` that refuses to run if the exclusion is missing from `kipi-update.sh`. The pytest regression is sufficient signal; runtime coupling adds complexity without value.
- Auto-running the new test from a hook. Standard pytest discovery on `plugins/prd-os/tests/` is enough.
- Splitting `prd-personas-baseline.md` into design-doc + measurement-log files. The current single-file structure works because the file is instance-local.

## Proposed approach

### Issue 1: docs (baseline.md header + phase0_measure docstring)

Files modified:
- `q-system/memory/working/prd-personas-baseline.md` — add a top-of-file `## Propagation contract` section that:
  - States the file is instance-local
  - Cites `kipi-update.sh:110` as the source of truth for the exclusion
  - Explains the consequence: `phase0_measure.py` appends are durable per-instance
- `plugins/prd-os/scripts/phase0_measure.py` — add a one-line note to the module docstring referencing `kipi-update.sh` exclusion as the reason this file's append target is safe.

### Issue 2: regression test (test_propagation.py)

New file: `plugins/prd-os/tests/test_propagation.py`. Reads `kipi-update.sh` from the repo root and verifies the exclusions are co-located with the rsync invocation that propagates `q-system/` (addressing finding-3 — a substring match alone would pass even if a refactor disconnected the exclusions from the actual rsync). Specifically:

1. Locate the line containing `rsync` followed by `q-system/` (the propagation call).
2. Walk forward and backward up to ~15 lines to capture the contiguous rsync flag block (lines ending in `\` or beginning with `--exclude`).
3. Assert that block contains all of: `--exclude="memory/"`, `--exclude="output/"`, `--exclude="my-project/"`.
4. Also assert the rsync call's source path is `q-system/` (so the exclusions are anchored to the right propagation target).

Tests are standalone; they read the real `kipi-update.sh` via a path derived from the test file location. Repo root resolved as `Path(__file__).resolve().parents[3]` (test → tests/ → prd-os/ → plugins/ → repo).

If a future change removes an exclusion OR splits it off from the rsync call (different command, different source path, etc.), this test fails immediately.

## Risks and rollback

### Risks

- **Stale exclusion list.** If `kipi-update.sh` changes the exclusion DSL (e.g., switches from `--exclude="path/"` to a different rsync syntax), the regex-style substring check breaks. Mitigation: keep the assertions on the literal current syntax; if `kipi-update.sh` changes, the test fails on the next pytest run and forces both files to be updated together.
- **Documentation drift.** The header I add today could go stale if `kipi-update.sh` adds or removes an exclusion. Mitigation: the regression test is the binding contract; the docs are explanation.
- **Tests reading paths outside the test tree.** `plugins/prd-os/tests/test_propagation.py` reads `kipi-update.sh` from the repo root. This violates the standard `fake_repo` ephemeral-tmp-path pattern. Mitigation: the test is read-only against a stable artifact, no state mutation, no risk of contaminating other tests. Document this exception in the test file's module docstring.

### Rollback

- Revert the header in `prd-personas-baseline.md`.
- Revert the docstring change in `phase0_measure.py`.
- Delete `plugins/prd-os/tests/test_propagation.py`.

Rollback cost: 3 file reverts. Blast radius: zero (the new content is additive; no existing behavior depends on it being present).

## Open questions

- **Should the test parse the rsync flags as data rather than string-match?** Resolved: no for v1. Substring matching is simpler and breaks loudly when the syntax changes, which is the desired behavior. Parsing the shell script properly is an over-engineered solution to a small problem.
- **Should the header also document the `output/` exclusion (which protects `q-system/output/`)?** Resolved: yes for `output/` and `memory/`. Excludes `.prd-os/` from the docs scope (per finding-4): `.prd-os/` is not in `q-system/` so it is not part of the rsync source at all; mentioning it conflated two different propagation surfaces. The header scope matches the regression test scope: `memory/`, `output/`, `my-project/`.
- **Should `phase0_measure.py`'s docstring re-state the entire contract?** Resolved: no. A one-line cross-reference to `kipi-update.sh` is enough. The full contract lives in `prd-personas-baseline.md`.

## Persona Review

This PRD intentionally skips the planning-personas Skeptic session. Per the `prd-planning-personas-2026-05-13` design notes (and applied to `prd-prd-os-receipts-and-phase0-measure-2026-05-14` for the same reason), small mechanical infrastructure PRDs should skip the persona session because ceremony cost exceeds the value. This is the system's own decision rule applied recursively for the third time.

Codex review can challenge the skip if it disagrees.

## Issues

<!--
After review and approval, populate the fenced JSON block below with one
entry per atomic issue. Required keys per entry: id, title, finding_id, allowed_files, required_checks.
-->

```json
[
  {
    "id": "prdos-propagation-docs",
    "title": "Add Propagation contract header to baseline.md + phase0_measure docstring cross-reference",
    "finding_id": "finding-1",
    "priority": "p1",
    "allowed_files": [
      "q-system/memory/working/prd-personas-baseline.md",
      "plugins/prd-os/scripts/phase0_measure.py"
    ],
    "required_checks": [
      "grep -q 'Propagation contract' q-system/memory/working/prd-personas-baseline.md",
      "grep -q 'kipi-update.sh' plugins/prd-os/scripts/phase0_measure.py"
    ],
    "acceptance": "baseline.md has a top-level ## Propagation contract section naming the kipi-update.sh exclusion of memory/, output/, my-project/. phase0_measure.py module docstring has a one-line cross-reference to kipi-update.sh."
  },
  {
    "id": "prdos-propagation-regression-test",
    "title": "Regression test asserting rsync exclusions are co-located with the q-system/ propagation call",
    "finding_id": "finding-3",
    "priority": "p1",
    "allowed_files": [
      "plugins/prd-os/tests/test_propagation.py"
    ],
    "required_checks": [
      "pytest -q plugins/prd-os/tests/test_propagation.py"
    ],
    "acceptance": "test_propagation.py reads kipi-update.sh, locates the rsync invocation that propagates q-system/, captures its contiguous flag block, and asserts --exclude=memory/, --exclude=output/, --exclude=my-project/ are all present in that block AND the rsync source is q-system/.",
    "required_reviews": ["codex-review"]
  },
  {
    "id": "prdos-measure-acceptance-tighten",
    "title": "Replace ambiguous kipi-update-dry success metric with deterministic grep + pytest",
    "finding_id": "finding-2",
    "priority": "p2",
    "allowed_files": [
      ".prd-os/prds/prd-prdos-propagation-contract-docs-2026-05-14.md"
    ],
    "required_checks": [
      "grep -q 'kipi update --dry check is dropped' .prd-os/prds/prd-prdos-propagation-contract-docs-2026-05-14.md"
    ],
    "acceptance": "The PRD success metric no longer references kipi update --dry. The grep + pytest pair is the binding success metric."
  },
  {
    "id": "prdos-layout-coupling-note",
    "title": "Narrow docs scope to exclusions the regression test actually verifies",
    "finding_id": "finding-4",
    "priority": "p3",
    "allowed_files": [
      "q-system/memory/working/prd-personas-baseline.md"
    ],
    "required_checks": [
      "grep -c 'memory/' q-system/memory/working/prd-personas-baseline.md"
    ],
    "acceptance": "Header documents memory/, output/, my-project/. Does not mention .prd-os/ as an exclusion (per finding-4: .prd-os is outside q-system and not in the rsync source)."
  }
]
```
