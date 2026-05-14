---
id: prd-planning-personas-2026-05-13
title: Planning Personas in prd-os Draft Phase
status: idea
created_at: 2026-05-13
updated_at: 2026-05-13
owner: assaf
reviewers: []
findings_path: .prd-os/findings/prd-planning-personas-2026-05-13-findings.jsonl
---

# Planning Personas in prd-os Draft Phase

## Problem

PRDs in kipi sometimes reach `/prd-review` without enough adversarial thinking up front. Codex catches issues at the review gate, but Codex is downstream. By the time Codex flags a vague success criterion, an unstated user, or a missing failure mode, the founder has already committed cognitive cycles to a specific direction. Revising at that stage costs more than asking the right question during the draft state.

Observed symptoms across recent PRDs:
- Goals stated in implementation language ("add X") rather than outcome language ("solve Y")
- Non-goals section left empty, which means scope is implicitly unlimited
- "Risks and rollback" treated as a checkbox rather than a real exposure assessment
- Open questions resolved silently between sessions without the founder confronting them explicitly

The most established analog in the public ecosystem, BMAD-METHOD (47K stars, bmad-code-org/BMAD-METHOD), addresses this through dedicated agentic personas (PM, Architect, Analyst, UX) that collaborate during planning. Kipi has the council skill in kipi-ops, but council is built for strategic decisions, not PRD shaping, and is not wired into the prd-os state machine.

This PRD proposes adding structured planning personas to the draft state of prd-os: a lightweight, optional, founder-invoked session that surfaces sharper questions before review.

## Goals

- Add a `/prd-personas` command that runs while a PRD is in the `draft` state.
- Run 3-4 personas (PM, Architect, Skeptic, optionally UX) asking 2-3 sharp questions each.
- Append the questions and the founder's answers as a `## Persona Review` section in the PRD spec itself.
- Make Codex's downstream review aware of what was already considered, so adversarial review can challenge specific answers rather than asking the same questions again.
- Keep the session bounded: max 3 personas active, max 3 questions each, founder answers in conversation, total session well under 20 minutes.

## Non-goals

- Replacing Codex adversarial review at the `/prd-review` gate. Personas surface thinking; Codex still adversarially reviews the final PRD.
- Multi-LLM debate. This stays single-Claude. The persona work is about loading sharper question patterns into context, not consensus mining across providers.
- Forcing personas on every PRD. Small PRDs (bug fixes, minor tweaks) skip this step. The command is optional.
- New state transitions in the PRD state machine. The PRD stays in `draft` throughout. Persona Review is content, not a state.
- A separate persona definition language. Personas live as plain markdown files, parallel to existing skills.

## Proposed approach

### New command

`/prd-personas` in `plugins/prd-os/commands/prd-personas.md`. Requires the active PRD to be in `draft` state, otherwise refuses with the current state and a hint.

### Persona definitions

New directory `plugins/prd-os/personas/` with one markdown file per persona. Each file declares:
- Persona name and one-line role
- 3-5 lens questions, phrased as concrete prompts
- Anti-patterns the persona watches for (vague success metrics, implementation-disguised-as-goal, etc.)

Initial personas:
- `pm.md`: who is this for, what problem are they having today, what does success look like in 1 sentence, what is the smallest version that proves the value
- `architect.md`: what is the cleanest design, what existing primitives are reused, what new dependencies are introduced, what breaks if this ships
- `skeptic.md`: what is the strongest argument against doing this, what is the smallest experiment that disproves the thesis, who is unhappy with this shipped, what is the cheapest non-build alternative
- `ux.md` (optional, only when the PRD has a user-facing surface): what does the founder actually have to do to use this, where does friction live, what is a 10x worse version that still works

### Session flow

When `/prd-personas` runs:

1. Read the active PRD spec.
2. Run a `precheck` step: for each persona, identify questions that are already answered in the spec. Skip those to avoid wasting the founder's attention.
3. For the remaining questions, work through personas one at a time:
   - Surface the persona's questions in a structured prompt.
   - Founder answers in conversation, one persona at a time.
   - Capture each Q-A pair.
4. After all personas, append the captured Q-A pairs to the PRD spec as a new `## Persona Review` section, with one subsection per persona.
5. Update the PRD's `updated_at` and save.

### What changes downstream

- `/prd-review` (Codex adversarial pass) sees the Persona Review section. The review rubric is updated to weight findings that contradict an explicit Persona Review answer differently from findings that surface a genuinely missed concern.
- `review-rubric.md` (in `plugins/prd-os/templates/`) gains a section: "Cross-reference findings against any existing `## Persona Review` section. A finding that restates a persona question without engaging with the recorded answer should be downgraded."
- No state machine changes. The PRD remains in `draft` after persona session; the founder still has to call `/prd-review` to advance.

### Persona detection

The decision to skip a question if it is already answered uses simple heuristics:
- Search the spec for the question's key concepts (regex or substring match).
- If a section labeled with one of the question's anchor keywords contains non-empty content, mark the question as "already covered" and skip.
- If ambiguous, present the question with a flag: "this might be covered in [section name]. Confirm or override?"

### Optional auto-suggestion at /prd-review

If `/prd-review` is invoked on a PRD that has no `## Persona Review` section and the PRD is non-trivial (heuristic: more than N lines, or marked as `priority: p0`), surface a one-line nudge before running Codex:

> "This PRD has no Persona Review. Run `/prd-personas` first? (y/skip)"

The nudge is non-blocking. Skip continues straight to Codex. This is the smallest possible surface area for catching the case where the founder forgot the optional step.

## Risks and rollback

### Risks

- **Risk: tedious for the founder, gets skipped.** The whole point is to surface thinking the founder hasn't done yet. If the session feels like busywork, it gets bypassed and the value is lost. **Mitigation:** keep it strictly optional, position as "for non-trivial PRDs," cap at 3 personas active at once, allow the founder to short-circuit specific personas if their lens does not apply.

- **Risk: persona questions duplicate existing draft content.** The PRD template already has Problem, Goals, Non-goals, Risks. If personas ask the same things, it is friction without value. **Mitigation:** precheck step skips questions already answered. Founder can override.

- **Risk: session balloons context.** Multiple personas with multiple questions can drift into long conversations that compete with other work in the session. **Mitigation:** hard caps (3 personas, 3 questions each, 1-sentence answers preferred). If the founder wants to go deeper on a specific question, they extend on their own.

- **Risk: overlap with the existing council skill.** Council is for strategic-decision-level dissent. This is for PRD shape. The two could blur. **Mitigation:** council operates on canonical files and high-stakes decisions; planning-personas operates on the active PRD draft. Different inputs, different outputs, different state machines.

- **Risk: encourages over-design.** Forcing every PRD through structured questioning could push toward bigger, more architectured solutions when smaller ones would do. **Mitigation:** Skeptic persona explicitly asks "what is the cheapest non-build alternative" and "what is the smallest experiment that disproves the thesis." The persona set is balanced to argue against over-design, not toward it.

### Rollback

- Delete `plugins/prd-os/commands/prd-personas.md`.
- Delete `plugins/prd-os/personas/` directory.
- Revert the optional nudge in the `/prd-review` command.
- Revert the rubric update in `review-rubric.md`.
- No state machine changes to revert. No data migration. No external integrations.

Rollback cost is one git revert per file. Low blast radius.

## Open questions

- Should `/prd-personas` block `/prd-review` until the persona session has been run at least once? Tentative answer: no. Forcing the optional step makes it non-optional and is the wrong move. The nudge at `/prd-review` is sufficient.

- Should personas be customizable per project (different KTLYST cluster instances might want different personas)? Tentative answer: yes, eventually. For v1, ship one persona set in the plugin. Add per-project overrides as a v2 issue if the need surfaces.

- Should the Persona Review section be machine-validated for completeness (e.g., every persona must have at least one Q-A pair)? Tentative answer: no for v1. Let founder shape the section freely. Add validation only if Codex review starts flagging incomplete persona sections as a pattern.

- Does this duplicate `kipi-ops/skills/council`? Different surface (PRD vs canonical decision), different timing (planning vs strategic shift), different output (PRD section vs council ruling). Worth one explicit comparison line in the persona docs.

- Should a UX persona be the default, or only fire when the PRD touches a user-facing surface? Tentative answer: only when user-facing. Most kipi PRDs are infrastructure (rules, scripts, plugins). UX persona on those is noise.

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
