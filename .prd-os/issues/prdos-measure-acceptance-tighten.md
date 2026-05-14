---
id: prdos-measure-acceptance-tighten
title: Replace ambiguous kipi-update-dry success metric with deterministic grep + pytest
status: closed
priority: p2
parent_prd: prd-prdos-propagation-contract-docs-2026-05-14
allowed_files:
  - .prd-os/prds/prd-prdos-propagation-contract-docs-2026-05-14.md
disallowed_files: []
required_checks:
  - grep -q 'kipi update --dry check is dropped' .prd-os/prds/prd-prdos-propagation-contract-docs-2026-05-14.md
required_reviews: []
---
<!-- generated-by: prd_split.py prd=prd-prdos-propagation-contract-docs-2026-05-14 finding=finding-2 at=2026-05-14T16:47:31Z -->

# Replace ambiguous kipi-update-dry success metric with deterministic grep + pytest

## Context

Parent PRD: `.prd-os/prds/prd-prdos-propagation-contract-docs-2026-05-14.md`

## Acceptance

The PRD success metric no longer references kipi update --dry. The grep + pytest pair is the binding success metric.
