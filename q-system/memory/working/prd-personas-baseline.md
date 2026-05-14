# prd-personas baseline measurement

**Purpose:** Record the rate of vague-goal-class and empty-non-goals-class findings across recent PRDs that did NOT run the planning-personas session. This baseline is the comparison point for the Phase 0 (template-only) and v0 (command-based) experiments described in `.prd-os/prds/prd-planning-personas-2026-05-13.md`.

## Propagation contract

This file is **instance-local**. Despite living under `q-system/memory/working/`, it is NOT propagated by `kipi update`. The exclusion lives in `kipi-update.sh` line 110:

```
rsync -a --delete \
    --exclude="my-project/" \
    --exclude="canonical/" \
    --exclude="memory/" \         # this line excludes q-system/memory/
    --exclude="output/" \
    --exclude=".q-system/agent-pipeline/bus/"
```

Three q-system directories are excluded from propagation: `memory/`, `output/`, and `my-project/`. Each instance maintains its own copy of files under these paths. Appending measurement rows to this file (via `plugins/prd-os/scripts/phase0_measure.py`) is therefore durable per-instance; `kipi update` will not overwrite them.

If the exclusion is ever removed from `kipi-update.sh`, the regression test at `plugins/prd-os/tests/test_propagation.py` will fail. That test is the binding contract; this section is explanation.

## Classification rules

A Codex finding counts as **vague-goal-class** if its `body` text (case-insensitive) contains any of: `vague`, `not measurable`, `unclear what success`, `no metric`, `operationalized`, `outcome-focused`, `implementation-focused`, `problem clarity`.

A Codex finding counts as **empty-non-goals-class** if its `body` contains any of: `non-goals`, `scope creep`, `scope discipline`, `unbounded scope`.

These keywords match the parent PRD verbatim. Any change to either list is a rule change to the success metric and must be documented as an amendment in the parent PRD before the script is updated.

Implementation: `plugins/prd-os/scripts/classify_findings.py`. Tests: `plugins/prd-os/tests/test_classify_findings.py`.

## Initial baseline (as of 2026-05-14)

The prd-os plugin was bootstrapped on 2026-05-14 and there is exactly one PRD in `.prd-os/prds/`: `prd-planning-personas-2026-05-13` itself. The findings file for that PRD captures the very Codex review that surfaced this baseline-measurement issue, so it is not a clean baseline candidate.

**Baseline state:** insufficient historical PRDs to compute a stable pre-personas baseline. The Phase 0 experiment must therefore run forward, not backward:

- Run `/prd-personas` (or, in Phase 0, the manual template) on the next 5 PRDs.
- For each new PRD, classify its Codex findings using `classify_findings.py file <findings.jsonl>`.
- Track the rate as PRDs accumulate.
- After 5 personas-applied PRDs, compare against any non-personas PRDs that ran in the same window. If no non-personas comparison exists, hold the kill criterion until at least 3 non-personas PRDs have run on the system for comparison.

This is a deliberate change from the v0 plan: the original PRD assumed sufficient historical PRDs existed to compute a backwards baseline. They do not. The Phase 0 experiment runs forward-only.

## How to record measurements

Each time a PRD finishes Codex review, append a row:

```
| YYYY-MM-DD | <prd-id> | <personas-applied? yes/no/manual-template> | <total findings> | <vague-goal count> | <empty-non-goals count> |
```

| Date | PRD | Personas | Total | Vague-goal | Empty-non-goals |
|------|-----|----------|-------|------------|-----------------|
| 2026-05-14 | prd-planning-personas-2026-05-13 | recursive-manual (Skeptic persona run against the PRD that defines the system) | 6 | 1 | 1 |

The recursive-manual run on this PRD still produced one vague-goal-class and one empty-non-goals-class finding (finding-2 in the JSONL, which Codex flagged for the success metric not being operationalized enough). The recursive persona pass did NOT prevent every goal-shape issue from reaching Codex. This is honest baseline data: even a persona pass against the PRD's own thesis still left a goal-shape gap that adversarial review caught. The Phase 0 experiment needs to outperform this single data point by at least 50% on the next 5 PRDs to clear the kill criterion.

Counts verified by running: `python3 plugins/prd-os/scripts/classify_findings.py file .prd-os/findings/prd-planning-personas-2026-05-13-findings.jsonl` on 2026-05-14.

## Kill criterion (from the PRD)

If after 5 personas-applied PRDs the vague-goal-class + empty-non-goals-class rate is NOT at least 50% lower than the same rate on the most recent 5 non-personas PRDs, the v0 command-based experiment is killed and the system rolls back to the Phase 0 template-only approach.

If the Phase 0 template-only approach achieves the 50% reduction unaided, the v0 command-based work is NOT built. The Phase 0 result determines whether the rest of the PRD ships.


## Append format used by phase0_measure.py

After Issue 2 ships, the only writer of new measurement rows is `plugins/prd-os/scripts/phase0_measure.py`. The script appends one row per invocation in the following format:

```
| <YYYY-MM-DD> | measurement | <personas_count>/<no_personas_count> PRDs | <total findings> | <vague-goal count> | <empty-non-goals count> | verdict=<kill|continue|insufficient-data> |
```

Existing manually-authored rows above this section remain. They are part of the baseline and are NOT rewritten by the script. The script only appends.

Rule: do not edit measurement rows by hand. If a measurement was wrong, append a corrective row with a comment in the same line explaining the correction.

## Updates

- 2026-05-14: baseline file created. Initial state: insufficient historical data; running forward-only experiment.
