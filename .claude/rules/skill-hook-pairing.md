# Skill-Hook Pairing (ENFORCED)

Skills generate. Hooks validate. Every skill that contains deterministic rules must ship with a hook that enforces them. Skills without hooks are aspirations.

## The architectural distinction

**Skills handle interpretation.** A skill loads reference material and shapes how Claude generates output. Skills are good at judgment: does this paragraph anchor in a real scar, does this hook fit Pattern A or B, is the analytical mode or personal mode the right register here.

**Hooks handle enforcement.** A hook is a Python script that exits non-zero if a deterministic violation is detected. Hooks are good at certainty: regex matches, banned words, character counts, file paths, schema validation.

**The two layers compose.** Skill drafts the content. Hook catches what the skill missed. Neither layer alone is sufficient for any rule that matters.

This is the same pattern already in use across the system:

- The Phase 6 sycophancy agent computes the rubber-stamp ratio. `sycophancy-harness.py` independently verifies. If the harness disagrees, the harness wins.
- Pipeline agents produce bus JSON. `verify-bus.py` schema-validates each file.
- The morning routine runs phases. `audit-morning.py` checks completion.

Voice rules belong in this pattern too. Skill describes what good writing sounds like. Hook catches deterministic violations the skill failed to enforce.

## The decision rule

For every rule in a skill, ask one question: **can this be detected with regex, string matching, character counting, or file inspection?**

- If yes → the rule must have a hook. Skill enforcement is insufficient.
- If no (requires interpretation) → skill is the right home. No hook needed.
- If partial (some deterministic, some interpretive) → split the rule. Hook the deterministic part. Leave interpretation in the skill.

## What deterministic looks like

- Banned words and phrases (`leverage`, `transformative`, `circling back`)
- Banned characters (em dashes)
- Banned patterns (`/q-foo` slash commands in published content)
- Character count constraints (LinkedIn 300 chars, X 280 chars)
- Required structural elements (frontmatter, H1, code fences)
- File path constraints (where outputs land)
- Citation patterns (no `\b\d+%`, no "X% of Y")
- Parallel-structure violations (three consecutive sentences with same opening word)

## What interpretation looks like

- Does the opener anchor in a real scar?
- Is this paragraph in analytical mode or personal mode?
- Does this draft sound like the founder specifically or like generic founder voice?
- Are these examples specific enough?
- Does the closing question land?

These cannot be regex'd. They live in the skill.

## Pairing contract

When a new skill ships, the wiring-check rule already requires the skill to be discoverable. The skill-hook pairing rule extends this:

- If the skill has deterministic rules, a paired hook must exist at the same time. The skill is not shippable without it.
- The hook lives at `q-system/.q-system/scripts/<skill-name>-lint.py` (or equivalent path per the folder-structure rule).
- The hook is wired in `.claude/settings.json` under the appropriate trigger (PostToolUse for output validation, PreToolUse for blocking before write).
- The hook scope must match the skill scope. A voice-lint hook on published-content paths only, not on every Edit.
- The hook documents which skill it pairs with in its header comment.

## Override mechanism

Hooks block by default. Founder can override on a per-file basis with an explicit comment marker:

- `<!-- voice-lint-skip -->` to bypass voice-lint on a markdown file
- `# headline-lint-skip` to bypass headline-lint
- One marker per hook. Skips do not stack. Founder must explicitly skip each.

This preserves the "hooks are contracts" thesis while allowing intentional exceptions.

## Existing skills that need hooks (priority order)

1. **assaf-voice / founder-voice** → voice-lint hook (banned words, stats, slash commands, rule-of-three)
2. **headline-engineering** (new) → headline-lint hook (char counts, banned title patterns, first-7-words emptiness)
3. **audhd-executive-function** → audhd-lint hook (every actionable list has time estimate + energy tag + concrete next action)
4. **linkedin-brand** → linkedin-format hook (no hashtags in first line, length constraints)
5. **research-mode** → mostly interpretive; hook scope limited to "no unmarked claims" detection

## When this rule does NOT apply

- Skills that are purely about loading reference material with no output (rare)
- Skills that produce code, not prose (different deterministic checks like type errors, linters)
- One-shot debrief or note-taking skills where the output is internal-only

## Wiring check addendum

When wiring-check runs (PostToolUse on Edit|Write), it should also check: if a new skill is being added, does it have a paired hook script and a settings.json entry? If not, the skill is incomplete.

## Cross-references

- `.claude/rules/wiring-check.md` — the broader end-to-end wiring rule this extends
- `.claude/rules/token-discipline.md` — same shape (hook-enforced budget rules)
- `q-system/.q-system/sycophancy-harness.py` — exemplar of the pattern (LLM agent + deterministic verifier)
