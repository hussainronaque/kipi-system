---
id: {{prd_id}}
title: {{title}}
status: idea
created_at: {{created_at}}
updated_at: {{created_at}}
owner: {{owner}}
reviewers: []
findings_path: .prd-os/findings/{{prd_id}}-findings.jsonl
---

# {{title}}

## Problem

<!-- What pain is this solving? Concrete, observed, measurable. -->

## Goals

- 

## Non-goals

- 

## Proposed approach

<!-- How. Keep it scannable. Diagrams go inline as fenced blocks. -->

## Risks and rollback

<!-- Blast radius, migration cost, how to back out if this ships wrong. -->

## Open questions

- 

<!--
## Persona Review (optional, fill in before /prd-review)

Phase 0 of the prd-os planning-personas experiment (PRD prd-planning-personas-2026-05-13).
For non-trivial PRDs, answer the three Skeptic questions below before invoking /prd-review.
Brief answers are fine. The goal is to force one round of adversarial thinking before Codex.

### Skeptic

Q1: What is the strongest argument against doing this?
A1:

Q2: What is the smallest experiment that would disprove the thesis?
A2:

Q3: What is the cheapest non-build alternative?
A3:

When done with these questions, uncomment this section and move it to live just before `## Issues` below.
-->

## Issues

<!--
After review and approval, populate the fenced JSON block below with one
entry per atomic issue. `prd_split.py` reads this block verbatim and writes
one issue spec per entry.

Required keys per entry:
  - id (kebab-case, unique across the repo)
  - title (non-empty string)
  - allowed_files (non-empty list of glob patterns)
  - required_checks (non-empty list, e.g. ["pytest -q"]). The runner's
    stop-gate checks that three receipts are marked (verified, reviewed,
    findings_triaged). Those receipts are meaningless unless the spec
    documents what must be verified, so an empty list is rejected.

Optional keys:
  - priority (default p1)
  - disallowed_files, required_reviews, acceptance

IDs must match the repo's issue naming convention and must not collide with
existing issue specs.
-->

```json
[]
```
