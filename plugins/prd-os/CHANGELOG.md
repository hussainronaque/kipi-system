# Changelog

All notable changes to the `prd-os` plugin are recorded here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions follow semantic versioning; see `README.md` for the bump policy and the distinction between plugin version and config schema version.

## [Unreleased]

(next release goes here)

## [0.3.0]

### Added
- `templates/gap-classes.md`: a catalog of recurring defect classes (scaling,
  security, correctness/concurrency, cross-cutting) distilled from a
  reproducer-first, adversarially-reviewed build where ~50 defects were caught
  before merge. General by construction; no product specifics.
- `templates/review-rubric.md`: a sixth review dimension, "Recurring gap
  classes," that checks a PRD's design against the catalog.
- `commands/prd-review.md`: `/prd-review` now reads `gap-classes.md` alongside
  the rubric and feeds it to Codex, so dimension 6 has its source.

## [0.1.0] - 2026-04-16

### Added
- Initial plugin scaffold.
- `.claude-plugin/plugin.json` manifest (name, version, description, author).
- Directory tree for `commands/`, `hooks/`, `scripts/`, `templates/`, `tests/`, and `skills/prd-os/`.
- `skills/prd-os/SKILL.md` placeholder describing the planned system.
- `README.md` documenting the package layout, portable-core vs repo-local split, and versioning policy.
- This changelog.

### Notes
- Scaffold only. No runner logic, no commands, no hooks, no templates, no tests are wired.
- No changes to the host repo's settings, commands, or runtime.
- Config schema version not yet defined; lands with the runner port in step 3.
