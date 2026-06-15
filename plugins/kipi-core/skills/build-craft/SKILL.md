---
name: build-craft
description: "Engineering discipline for writing and editing code. Use when building a feature, fixing a bug, writing a script, writing tests, hardening a data path, or any task that edits more than a one-line config. Encodes the verified-good habits of the Fable 5 model (recon before edit, verify against a copy with a negative self-test, single-writer chokepoints, scar-anchored why-comments) as an additive layer on top of Opus defaults, plus the consistency rules an independent Codex review showed were applied unevenly (test isolation, dependency pinning, edge-case specification, input validation). Pairs with the build-craft-lint hook."
---

# Build-Craft Skill

The forward-engineering counterpart to the rca skill. This encodes coding habits
that an independent review (Codex findings on 4 PRDs, plus git-survival of the
shipped code) graded as genuinely good, distilled from a forensic read of 697
code edits written by the Fable 5 model.

**Framing matters: this is the Fable delta on top of Opus, not a replacement.**
Opus already documents, type-hints, and guards by default. Keep all of that. This
skill adds the handful of things Fable did that Opus does not do by default, and
makes them consistent (the review showed Fable did them well but unevenly).

## The four habits to add (graded-good, code survived in git)

1. **Recon before edit. Read reality, do not assume it.**
   Before changing code, run a `grep`/`sed`/inline-`python` burst against the
   real schema and call-sites. Confirm the connection point exists before drafting
   against it. Never edit a file you have not read this session. If you already
   read a schema, re-read the column names rather than guessing them (the single
   most common self-inflicted failure in the corpus was guessing `type`/`name`
   when the columns were `entity_type`/`canonical_name`, after the file was
   already open).

2. **Verify against a copy, with a negative self-test.**
   A passing gate is not trusted until it has been seen to fail. Run the
   reproducer against a *copy* of the live resource, never the live one. Then
   corrupt a valid input and prove the gate FAILS on the violation, so the green
   is not a rubber stamp. Example from the corpus:
   `# Negative self-test: gate must FAIL on a violating manifest (proves it's not a rubber stamp)`

3. **Single-writer chokepoint, guarded by a grep-the-tree test.**
   When a resource (a table, a layout, a lock) has many would-be writers, route
   every mutation through one helper and write a test that shells out to `grep`
   to prove no caller bypasses it. Migrate every existing call-site one small,
   independently revertible edit at a time, not one bulk rewrite.

4. **Why-comments anchored to a named scar.**
   Comments encode the constraint and the specific past bug that motivates it,
   not a restatement of the code. Example that survived into a test file:
   `# the mixed-format trap from the TTFN metric bug`. If the scar has an rca,
   reference it. These survive refactors because they encode invariants.

## The five consistency rules (Codex flagged these as applied unevenly)

Fable did each of these correctly *somewhere* and forgot them *elsewhere*. Make
them non-optional:

- **Test isolation.** A test connects to a temp/copy resource or `:memory:`,
  never a real data path. (This is the deterministic slice the build-craft-lint
  hook enforces.)
- **Declare and pin every new dependency** the moment you import it, and keep a
  test that proves the manifest covers every third-party import.
- **Specify degenerate cases before implementing**: empty, single-element,
  disconnected, and non-converging inputs each get defined behavior, not an
  implicit crash or a stale-state leak.
- **Validate persisted external input.** Never store arbitrary user/LLM JSON or
  selectors that, if malformed, can permanently break rendering or a load path.
- **Enumerate all call-sites when scoping a change.** Before declaring a change
  done, grep for every site the change must reach (the single-writer migration
  did this well: all 14 insert sites were routed through the one helper).

## Anti-patterns to drop (Fable weaknesses, do not import)

- Guessing a schema or API you have already read. Re-read it.
- Re-attempting the same failing shell shape. After one failure, change the
  approach, do not retry verbatim.
- Em-dashes in narration to the founder. The no-em-dash rule applies to your own
  status prose, not just shipped content (Fable broke this 476 times in one repo).

## Communication while building

Terse mid-task (`9/9 green. Wiring the CLI command.`), then decompress at the
seam into a `**Verification (ran, not assumed):**` block listing what you ran and
what passed. When a real choice exists, name the options, mark your pick, give the
tradeoff, end with one action. (This half already lives in the name-options rule
and the AUDHD output style. Reuse it, do not restate it.)

## Pairing

The deterministic slice (test isolation) is enforced by
`scripts/build-craft-lint.py`, wired in the kipi-core `hooks/hooks.json`
PostToolUse. The rest is judgment and lives here. See `references/checklist.md`
for the copy-paste pre-done gate.
