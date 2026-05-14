---
id: prdos-layout-coupling-note
title: Narrow docs scope to exclusions the regression test actually verifies
status: closed
priority: p3
parent_prd: prd-prdos-propagation-contract-docs-2026-05-14
allowed_files:
  - q-system/memory/working/prd-personas-baseline.md
disallowed_files: []
required_checks:
  - grep -c 'memory/' q-system/memory/working/prd-personas-baseline.md
required_reviews: []
---
<!-- generated-by: prd_split.py prd=prd-prdos-propagation-contract-docs-2026-05-14 finding=finding-4 at=2026-05-14T16:47:31Z -->

# Narrow docs scope to exclusions the regression test actually verifies

## Context

Parent PRD: `.prd-os/prds/prd-prdos-propagation-contract-docs-2026-05-14.md`

## Acceptance

Header documents memory/, output/, my-project/. Does not mention .prd-os/ as an exclusion (per finding-4: .prd-os is outside q-system and not in the rsync source).
