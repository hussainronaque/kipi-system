---
id: prd-personas-baseline-and-classification
title: Operationalize success metric: baseline measurement script + classification rule
status: closed
priority: p0
parent_prd: prd-planning-personas-2026-05-13
allowed_files:
  - q-system/memory/working/prd-personas-baseline.md
  - plugins/prd-os/scripts/classify_findings.py
  - plugins/prd-os/tests/test_classify_findings.py
disallowed_files: []
required_checks:
  - test -f q-system/memory/working/prd-personas-baseline.md
  - test -f plugins/prd-os/scripts/classify_findings.py
  - pytest -q plugins/prd-os/tests/test_classify_findings.py
required_reviews: []
---
<!-- generated-by: prd_split.py prd=prd-planning-personas-2026-05-13 finding=finding-2 at=2026-05-14T14:40:07Z -->

# Operationalize success metric: baseline measurement script + classification rule

## Context

Parent PRD: `.prd-os/prds/prd-planning-personas-2026-05-13.md`

## Acceptance

classify_findings.py classifies a JSONL findings stream into vague-goal-class and empty-non-goals-class buckets via the body-text rules defined in the PRD. Baseline file records the rate across the 5 most recent merged PRDs. Test validates classification on a fixture.
