---
id: prdos-propagation-docs
title: Add Propagation contract header to baseline.md + phase0_measure docstring cross-reference
status: closed
priority: p1
parent_prd: prd-prdos-propagation-contract-docs-2026-05-14
allowed_files:
  - q-system/memory/working/prd-personas-baseline.md
  - plugins/prd-os/scripts/phase0_measure.py
disallowed_files: []
required_checks:
  - grep -q 'Propagation contract' q-system/memory/working/prd-personas-baseline.md
  - grep -q 'kipi-update.sh' plugins/prd-os/scripts/phase0_measure.py
required_reviews: []
---
<!-- generated-by: prd_split.py prd=prd-prdos-propagation-contract-docs-2026-05-14 finding=finding-1 at=2026-05-14T16:47:31Z -->

# Add Propagation contract header to baseline.md + phase0_measure docstring cross-reference

## Context

Parent PRD: `.prd-os/prds/prd-prdos-propagation-contract-docs-2026-05-14.md`

## Acceptance

baseline.md has a top-level ## Propagation contract section naming the kipi-update.sh exclusion of memory/, output/, my-project/. phase0_measure.py module docstring has a one-line cross-reference to kipi-update.sh.
