---
id: prd-personas-command-implementation
title: Implement /prd-personas command + skeptic persona file + parser-compat test
status: closed
priority: p1
parent_prd: prd-planning-personas-2026-05-13
allowed_files:
  - plugins/prd-os/commands/prd-personas.md
  - plugins/prd-os/personas/skeptic.md
  - plugins/prd-os/tests/test_prd_split_personas.py
disallowed_files: []
required_checks:
  - test -f plugins/prd-os/commands/prd-personas.md
  - test -f plugins/prd-os/personas/skeptic.md
  - grep -q 'draft' plugins/prd-os/commands/prd-personas.md
  - pytest -q plugins/prd-os/tests/test_prd_split_personas.py
required_reviews:
  - codex-review
---
<!-- generated-by: prd_split.py prd=prd-planning-personas-2026-05-13 finding=finding-1 at=2026-05-14T14:40:07Z -->

# Implement /prd-personas command + skeptic persona file + parser-compat test

## Context

Parent PRD: `.prd-os/prds/prd-planning-personas-2026-05-13.md`

## Acceptance

Command file documents draft-state-only invocation and calls prd_runner.py status for active-PRD discovery. skeptic.md declares the 3 pinned questions verbatim. Parser-compat test confirms prd_split.py handles PRDs with a Persona Review section. Only ships if Phase 0 fails the kill criterion.
