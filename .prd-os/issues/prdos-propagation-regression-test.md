---
id: prdos-propagation-regression-test
title: Regression test asserting rsync exclusions are co-located with the q-system/ propagation call
status: closed
priority: p1
parent_prd: prd-prdos-propagation-contract-docs-2026-05-14
allowed_files:
  - plugins/prd-os/tests/test_propagation.py
disallowed_files: []
required_checks:
  - pytest -q plugins/prd-os/tests/test_propagation.py
required_reviews:
  - codex-review
---
<!-- generated-by: prd_split.py prd=prd-prdos-propagation-contract-docs-2026-05-14 finding=finding-3 at=2026-05-14T16:47:31Z -->

# Regression test asserting rsync exclusions are co-located with the q-system/ propagation call

## Context

Parent PRD: `.prd-os/prds/prd-prdos-propagation-contract-docs-2026-05-14.md`

## Acceptance

test_propagation.py reads kipi-update.sh, locates the rsync invocation that propagates q-system/, captures its contiguous flag block, and asserts --exclude=memory/, --exclude=output/, --exclude=my-project/ are all present in that block AND the rsync source is q-system/.
