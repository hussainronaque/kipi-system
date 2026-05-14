---
id: prd-personas-phase-0-template
title: Phase 0: add Skeptic question template to PRD templates, run 2-week template-only experiment
status: closed
priority: p0
parent_prd: prd-planning-personas-2026-05-13
allowed_files:
  - q-system/marketing/templates/prd.md
  - plugins/prd-os/templates/prd.md
disallowed_files: []
required_checks:
  - grep -q 'Persona Review' plugins/prd-os/templates/prd.md
  - grep -q 'Persona Review' q-system/marketing/templates/prd.md
  - grep -q 'strongest argument against' plugins/prd-os/templates/prd.md
required_reviews: []
---
<!-- generated-by: prd_split.py prd=prd-planning-personas-2026-05-13 finding=finding-3 at=2026-05-14T14:40:07Z -->

# Phase 0: add Skeptic question template to PRD templates, run 2-week template-only experiment

## Context

Parent PRD: `.prd-os/prds/prd-planning-personas-2026-05-13.md`

## Acceptance

Both PRD templates include a commented-out Persona Review section with the 3 Skeptic questions. Founder fills it manually on the next 3 PRDs and the result is measured against the baseline before any plugin code ships.
