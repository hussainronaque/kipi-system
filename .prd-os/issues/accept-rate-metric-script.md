---
id: accept-rate-metric-script
title: accept-rate.py prd-os disposition/receipt-coverage metric
status: open
priority: p1
parent_prd: prd-accept-rate-metric-2026-06-15
allowed_files:
  - q-system/.q-system/scripts/accept-rate.py
disallowed_files: []
required_checks:
  - python3 q-system/.q-system/scripts/accept-rate.py --selftest
required_reviews: []
bypass_exempt: "Test-portability fix only (selftest runs in-memory so it works in a read-only sandbox). Read-only tool; introduces no gate, skip, or no-verify bypass."
---
<!-- generated-by: prd_split.py prd=prd-accept-rate-metric-2026-06-15 finding=finding-1 at=2026-06-15T23:44:23Z -->

# accept-rate.py prd-os disposition/receipt-coverage metric

## Context

Parent PRD: `.prd-os/prds/prd-accept-rate-metric-2026-06-15.md`

## Acceptance

selftest passes (positive+negative); plain run flags build-craft (8 accepted / 0 receipts) and leaves the other 3 PRDs ok; --gate exits 2 on alert
