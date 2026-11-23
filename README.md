# Subagent Definition Pattern

Claude Code lets you define subagents as Markdown files in `.claude/agents/`. It also lets you
define skills. Both are Markdown, both have YAML frontmatter with a `name` and a `description`,
and both describe how to do some piece of work — so in practice people write one, then write the
other, and end up with two files that half-overlap and slowly disagree.

This repo is a pattern guide for the split that keeps them from overlapping:

> A **skill** describes work that any caller might need to do — formats, schemas, pipeline steps.
> An **agent definition** describes the *executor*: which model runs, which files it may write,
> which rules it may never break, and what it must hand back.

Plus the parts of an agent definition that are easy to get wrong: the `description` field is a
**router string** (it triggers auto-delegation, so it names a trigger condition, not a
personality), the `model` field is a **judgment budget** rather than a cost knob, and the hard
constraints are worth **restating inline** even when a skill already documents them.

**Works with:** Claude Code, Codex, Cursor, Gemini CLI; ChatGPT, Claude.ai and Gemini via [`PROMPT.md`](PROMPT.md).

| Surface | How | Status |
|---|---|---|
| Claude Code | `.claude/agents/*.md` definitions (the format the examples use) | tested 2026-11-23, file format and locations checked against the docs; not run end to end |
| Codex | `.codex/agents/*.toml`; pattern applies, files must be rewritten as TOML | not tested |
| Cursor | `.cursor/agents/*.md`; also reads `.claude/agents/` | not tested |
| Gemini CLI | `.gemini/agents/*.md` | not tested |
| ChatGPT / Claude.ai / Gemini | paste [`PROMPT.md`](PROMPT.md) | not tested |
| Linter and generator | `python3 tools/*.py`, standard library only | tested 2026-11-23, Python 3.14 (CI also runs 3.10 and 3.12) |

## Quick start

Drop a file into `.claude/agents/` in your project:

```markdown
---
name: records-keeper
description: "Mechanical governance-records agent for DECISIONS.md, OPEN_QUESTIONS.md, and logs/task_ledger.csv. Use for all bookkeeping and logging tasks."
model: haiku
---

You are the mechanical governance-records agent for this project (<project-root>). You append
rows and entries to governance records exactly as briefed — no interpretation, no editorializing,
no substantive work. Follow the records-update skill for all formats.

## Hard rules (restated inline — no lookup needed)

1. **File allowlist — touch ONLY these:** DECISIONS.md, OPEN_QUESTIONS.md, REQUESTS.md, and
   files under logs/. Never source documents, never deliverable content, never anything else.
2. **No version-control writes.** Ever.
3. **Append, don't delete.** To resolve an OPEN_QUESTIONS.md entry, append a dated resolution
   note beneath the original and flip its status label; never rewrite existing text.
4. **Never invent content.** Every field value comes from the task brief or from the file
   itself. If the brief leaves a required field unspecified, report the gap rather than guessing.

## Working method

Always read the target file's existing format first — the header row plus the last two or three
entries — and match it exactly: column count, quoting, date format, trailing newline.

## Output

Return a verbatim diff-style report: for each file touched, the filename and the exact lines
appended (quoted verbatim), plus a one-line note of any format anomaly found.
```

That is the whole mechanism. Ask for "log this decision and append a ledger row" and the
`description` routes it here; `model: haiku` keeps it cheap; the allowlist keeps it contained;
the output contract lets you verify the work without reopening the files.

Then read **[PATTERN.md](PATTERN.md)** for why each part is shaped that way.

## What's here

| Path | What it is |
|---|---|
| [`PATTERN.md`](PATTERN.md) | The guide: router strings, model tiering, the skill/definition split, inline restatement, escalation, output contracts, anti-patterns, review checklist |
| [`agents/records-keeper.md`](agents/records-keeper.md) | Worked `haiku` example — mechanical, append-only bookkeeping |
| [`agents/document-intake.md`](agents/document-intake.md) | Worked `sonnet` example — multi-step pipeline execution |
| [`agents/README.md`](agents/README.md) | Placeholder key, and the pointer for the `opus` judgment tier |
| [`agents/release-notes-trio/`](agents/release-notes-trio/) | The same three tiers in an unrelated (fictional) software-release domain |
| [`tools/check_frontmatter.py`](tools/check_frontmatter.py) | Validates definition frontmatter — required fields, name/filename agreement, model tier, description length |
| [`tools/gen_agents.py`](tools/gen_agents.py) | Generates definition files from one shared preamble; `--check` fails on stale output |
| [`agent_src/`](agent_src/), [`agents/generated/`](agents/generated/) | Five generic roles (architect, implementer, judge, reviewer, mechanical) and their generated files |
| [`templates/decision-record.md`](templates/decision-record.md) | Append-only decision record entry for the standing-decision rule |
| [`docs/judgment-tier.md`](docs/judgment-tier.md) | Checklist for any judgment-tier definition |

Run the validator over your own definitions:

```sh
python3 tools/check_frontmatter.py .claude/agents/*.md
```

It uses PyYAML if you have it and falls back to a flat `key: value` reader if you don't, so it
has no dependencies.

Options: `--models small,large` replaces the allowed `model` values (default `haiku,sonnet,opus`),
`--require name,description` replaces the required fields, `--json` prints one JSON document.
Exit code 0 means every file passed, 1 means a file failed, 2 means a usage error.

Pre-commit hook (save as `.git/hooks/pre-commit` and `chmod +x`):

```sh
#!/bin/sh
python3 tools/check_frontmatter.py .claude/agents/*.md
```

Generate role files from a shared preamble, and check they are current:

```sh
python3 tools/gen_agents.py --src agent_src --out .claude/agents
python3 tools/gen_agents.py --src agent_src --out .claude/agents --check
```

Tests: `python3 -m unittest discover -s tests`.

For Codex, Cursor and Gemini CLI file locations and a small/medium/large tier mapping, see
section 12 of [`PATTERN.md`](PATTERN.md).

## The three tiers at a glance

| Tier | Kind of work | Judgment permitted | Body tends to be |
|---|---|---|---|
| `haiku` | Mechanical, append-only, format-matching | None — every value comes from the brief | Short; mostly an allowlist |
| `sonnet` | Multi-step pipeline execution | Local and procedural | Medium; pipeline recap, tools, constraints |
| `opus` | Adversarial judgment, verdicts, sign-offs | Substantive — the role's value is disagreeing | Long; mostly an evidence bar |

The `opus` slot is a pointer rather than a template: a full judgment persona already exists at
**[adversarial-peer-review-role](https://github.com/hyderhusainarastu/adversarial-peer-review-role)**,
which ships the evidence bar, severity taxonomy, verdict vocabulary, and disconfirmation
discipline as a drop-in role body. `agents/release-notes-trio/release-gate-reviewer.md` shows a
compact domain-specific version.

## Related

More patterns: **[palimnote-agent-patterns](https://github.com/hyderhusainarastu/palimnote-agent-patterns)**, **[multi-agent-orchestration-playbook](https://github.com/hyderhusainarastu/multi-agent-orchestration-playbook)**, **[adversarial-peer-review-role](https://github.com/hyderhusainarastu/adversarial-peer-review-role)**.

**[agent-brief-schema-for-specialist-roles](https://github.com/hyderhusainarastu/agent-brief-schema-for-specialist-roles)**
— the schema for the *task brief* you hand an agent when you invoke it. The one-line distinction:
**briefs are per-task, definitions are per-role.** A definition says what this executor always
is; a brief says what it is doing right now. Use both — the brief gets much shorter once the
standing constraints live in the definition.

## How it differs

Official docs for each tool describe the file format. This repo is about what to write inside the
file and how to split it from skills. It is not a catalog of ready-made agents; collections of
prebuilt subagents exist elsewhere and complement it.

## Limitations

- **This is a pattern guide, not a specification.** Claude Code owns the actual frontmatter
  contract for `.claude/agents/` files, and it can change. Fields beyond `name`, `description`,
  and `model` exist and are not covered here; check the official documentation before relying on
  any of them. The validator checks the three fields this pattern is about and ignores others.
- **Auto-delegation is a heuristic.** A good `description` improves routing; it does not
  guarantee it. If a task must go to a particular role, name the role explicitly when you
  delegate. Nothing here makes routing deterministic.
- **Tiering advice is a heuristic too.** "Mechanical work on `haiku`" holds for append-and-match
  tasks against a well-specified format. Work that looks mechanical but has judgment hiding in it
  — deciding whether two records describe the same thing, choosing a category — will fail at that
  tier, and the failure mode is confident wrongness. Test before you downshift.
- **The examples are illustrative, not runnable.** `DECISIONS.md`, `logs/task_ledger.csv`,
  `CHANGELOG.md` and the rest are stand-in names, and `<project-root>`,
  `[[STANDING-RULE-ID]]`, `[[YOUR-GATE-NAME]]` are placeholders. Every example references a
  companion skill that this repo does not ship — the split is the point, and the skill's content
  is necessarily yours.
- **The release-notes trio is fictional.** It is a second instantiation written to show the
  pattern generalizes, not a description of any real release process.
- **The reliability claims are practitioner experience, not measurement.** Inline restatement of
  hard rules, explicit output contracts, and file allowlists are here because agents drift
  without them. No benchmark accompanies that claim, and none is offered.
- **No governance is enforced.** A file allowlist in a definition is an instruction, not a
  sandbox. If a role genuinely must not write somewhere, use the permission settings, not prose.

## License

[CC BY 4.0](LICENSE) (Creative Commons Attribution 4.0 International).

Copyright (c) 2026 hyderhusainarastu

Use the examples, adapt
them, ship them in your own projects.

**Keywords:** subagent definition, `.claude/agents`, AGENTS.md, agent description, model tier,
skill vs agent, frontmatter linter, Claude Code, Codex, Cursor, Gemini CLI.

---

Part of palimnote-agent-patterns - more at https://github.com/hyderhusainarastu
