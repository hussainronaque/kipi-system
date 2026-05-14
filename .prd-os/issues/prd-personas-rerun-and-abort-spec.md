---
id: prd-personas-rerun-and-abort-spec
title: Document rerun, interruption, abort, and dup-section handling in command spec
status: closed
priority: p1
parent_prd: prd-planning-personas-2026-05-13
allowed_files:
  - plugins/prd-os/commands/prd-personas.md
disallowed_files: []
required_checks:
  - grep -q 'rerun' plugins/prd-os/commands/prd-personas.md
  - grep -q 'abort' plugins/prd-os/commands/prd-personas.md
  - grep -q 'timestamped' plugins/prd-os/commands/prd-personas.md
required_reviews: []
---
<!-- generated-by: prd_split.py prd=prd-planning-personas-2026-05-13 finding=finding-5 at=2026-05-14T14:40:07Z -->

# Document rerun, interruption, abort, and dup-section handling in command spec

## Context

Parent PRD: `.prd-os/prds/prd-planning-personas-2026-05-13.md`

## Acceptance

Command file documents: rerun appends timestamped subsection (not duplicate ## heading); interruption discards partial answers; explicit abort discards partial answers; never writes a second top-level ## Persona Review heading.
