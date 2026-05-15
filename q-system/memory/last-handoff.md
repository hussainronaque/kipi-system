# Session Handoff

**Date:** 2026-05-15
**Theme:** Compounding judgement loop + green CI

## What shipped (5 commits on main, all pushed)

- **Phase A: Skeptic learns from Codex findings** - commit `3fe8fd3`. After PRD archives, `propose_skeptic_antipatterns.py` reads the archived PRD's Skeptic Q-A pairs plus the matching Codex findings, routes each via `classify_findings.classify_body`, and writes a proposal to `q-system/output/skeptic-proposals/`. Wired best-effort into `prd_runner.cmd_archive`. 10 new pytest fixtures, all 263 prd-os tests green.
- **Phase B: learn-from-correction skill** - same commit `3fe8fd3`. `plugins/kipi-core/skills/learn-from-correction/SKILL.md` encodes the 7-step Buzz workflow. `references/principle-vs-rule.md` is the load-bearing guardrail (principles transfer, rules overfit). Constraint: never auto-edits target skill files; output goes to `q-system/output/skill-proposals/`.
- **Phase C: hitlist override capture** - same commit `3fe8fd3`. `copy-diffs.schema.json` gained optional `original_text` + `posted_text` fields. `01c-copy-diff.md` agent now captures full before/after when status is `edited`. `route-overrides-to-learn.py` reads `copy_edits` SQLite rows and emits an inbox markdown that the founder can hand to the learn-from-correction skill.
- **Tree cleanup** - commits `80f3321` (lefthook: allow cleanup commits via `--diff-filter=ACMRT`), `d4f056c` (untrack 62 accidentally-committed `.pyc` files), `a677c0f` (auto-committed by Stop hook for last-handoff.md update).
- **CI is green for the first time in weeks** - commit `61cecd0` (fixed 2 KTLYST refs in `init-bus-day.sh` comment + `validate-separation.py` skeleton sweep now excludes `memory/`, added pytest step that runs the 263 prd-os tests). Commit `123c06f` (bumped `actions/checkout@v6` + `actions/setup-python@v6` ahead of June 2026 Node 20 cutover).

## Decisions

- Treating skills like code: every proposal (Skeptic anti-patterns, learn-from-correction outputs, engagement inbox) goes to a markdown file under `q-system/output/`. Founder commits the edit manually so Codex review fires on the diff. No auto-edit of skill or persona files anywhere in the loop.
- Phase A uses signal we already have (Codex findings vs Skeptic Q-A) before building any new capture. Phase B generalizes the principle-extraction. Phase C captures new signal (engagement overrides) and routes to Phase B.
- Lefthook's `blocked-paths` now scopes to `ACMRT` (additions, copies, modifications, renames, type-changes). Deletions pass through so cleanup commits don't need `--no-verify`. The protection against new `.env` or pycache additions still holds.
- `q-system/memory/` is runtime state, not skeleton template. Excluded from the skeleton sweep validator the same way `output/` already was.

## Tree state

- `main` synced with `origin/main`
- No dirty files
- 263 prd-os tests passing locally and in CI
- CI gate: validate workflow runs in ~27s, green

## Open items

- **Phase A's classifier is narrow.** `classify_findings.py` only knows `vague-goal-class` and `empty-non-goals-class`. Other Codex finding shapes route to "uncategorized" in proposals. If proposals are noisy in practice, the right knob is adding classes + keywords to `classify_findings.py:21-37`.
- **Learn-from-correction has no usage yet.** The skill exists, but nothing has been routed through it. First real test will be the next Phase A proposal that lands or the first time the founder runs `route-overrides-to-learn.py`.
- **engagement-hitlist override capture is not yet runtime-validated.** The 01c-copy-diff agent change is documented; the next `/q-morning` run with an edited hitlist will be the first real capture.
- **Plan file** at `~/.claude/plans/wise-sniffing-nebula.md` has the full A+B+C design including verification commands.

## Next session entry points

- If a PRD archived this week, check `q-system/output/skeptic-proposals/` for the first real proposal output and decide what (if anything) to merge into `plugins/prd-os/personas/skeptic.md`.
- If you ran `/q-morning` and edited a hitlist comment, run `python3 q-system/.q-system/scripts/route-overrides-to-learn.py` and see what the inbox looks like.

## Reference

- Source idea: Warp's writeup on the Buzz agent (principles transfer, rules overfit; daily PR with diffs; feedback loop lives where the team already works).
- Phase A reuses `phase0_measure` helpers (now public) for Skeptic section extraction. `__all__` declared.
- All output dirs tracked via `.gitkeep`: `skeptic-proposals/`, `skill-proposals/`, `skill-proposals/_inbox/`.
