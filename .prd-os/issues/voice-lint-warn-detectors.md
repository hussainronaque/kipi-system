---
id: voice-lint-warn-detectors
title: H8b+H9: emphasis-opener + rhetorical-QA WARN detectors in voice-lint
status: closed
priority: p2
parent_prd: prd-claudesidian-finish-2026-06-20
allowed_files:
  - q-system/.q-system/scripts/voice-lint.py
  - q-system/.q-system/scripts/test/test-voice-lint-warn-detectors.sh
disallowed_files: []
required_checks:
  - bash q-system/.q-system/scripts/test/test-voice-lint-warn-detectors.sh
required_reviews: []
bypass_check: "bash q-system/.q-system/scripts/test/test-voice-lint-warn-detectors.sh"
---
<!-- generated-by: prd_split.py prd=prd-claudesidian-finish-2026-06-20 finding=finding-2 at=2026-06-20T05:17:02Z -->

# H8b+H9: emphasis-opener + rhetorical-QA WARN detectors in voice-lint

## Context

Parent PRD: `.prd-os/prds/prd-claudesidian-finish-2026-06-20.md`

## Acceptance

Sentence-initial 'Importantly,'/'Notably,'/'Crucially,'/'Significantly,' and a short rhetorical question answered by the next short sentence each emit a violation with a NEW rule name that is in WARN_RULES (exit 0, advisory); mid-sentence 'significantly faster' and a real reader-directed question do NOT flag; the kipi-mcp linter is untouched; and the test asserts WARN_RULES membership is unchanged except the two new rule names (no existing rule re-tiered).
