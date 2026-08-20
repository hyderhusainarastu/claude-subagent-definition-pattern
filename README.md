# Claude Code Subagent Definition Pattern

A pattern for writing `.claude/agents/*.md` subagent definition files for
Claude Code, plus worked examples across two invented domains.

## The problem

Claude Code projects that use both `.claude/skills/` and `.claude/agents/`
tend to converge on the same failure after a few months: nobody's sure which
layer a given piece of content belongs in.

- A rule gets written once, in a skill, and an agent is told to "follow the
  skill" — and then months later the agent misapplies the rule, because
  following a pointer correctly, every single invocation, with no lossy
  summarization, turns out to be a real failure mode, not a hypothetical one.
- An agent's `description` field gets written like a bio ("a helpful,
  detail-oriented agent that manages records") instead of a trigger condition,
  so the thing that's supposed to auto-route tasks to it can't actually tell
  when it should fire.
- The `model:` tier gets picked once, out of habit, and never revisited
  against what the task actually requires — so a judgment call gets
  delegated to a model that just executes formats, or a purely mechanical
  bookkeeping task gets routed to a model that editorializes when it should
  just be transcribing.
- Nobody has written down what an agent should do when new evidence seems to
  contradict a decision a human already made — so agents improvise, and
  sometimes improvise by quietly overriding a decision they had no authority
  to revisit.

This repo writes down a pattern that avoids all four, and shows it applied to
two small invented domains so the pattern is visible without any of the
project-specific baggage a real production example would carry.

## Quick start

1. Read **[`PATTERN.md`](PATTERN.md)** first — it's short, and it's the
   actual content of this repo. Everything else is worked example.
2. Look at **[`agents/records-keeper.md`](agents/records-keeper.md)** (a
   `haiku`-tier mechanical bookkeeping agent) and
   **[`agents/document-intake.md`](agents/document-intake.md)** (a
   `sonnet`-tier pipeline agent) side by side — notice how body length and
   content track the model tier, and how each restates its two or three
   most critical rules inline even though a fuller version lives elsewhere.
3. Read **[`agents/OPUS-TIER.md`](agents/OPUS-TIER.md)** for what the
   judgment tier adds on top of the other two.
4. Look at **[`agents/release-notes-trio/`](agents/release-notes-trio/)** —
   the same haiku/sonnet/opus three-tier shape, applied to a completely
   different domain (release notes instead of records), to see that the
   pattern isn't specific to record-keeping.
5. Copy whichever example is closest to your own use case into your own
   `.claude/agents/` directory and edit the placeholders
   (`<project-root>`, `[[STANDING-RULE-ID]]`, `[[YOUR-GATE-NAME]]`) to match
   your project.

**Related:** this repo covers per-role *definitions* — the standing file that
describes an agent's model tier, allowlist, and hard rules. For the separate
question of how to hand one specific *task* to an agent at run time (a
briefing format, not a role definition), see
**github.com/hyderhusainarastu/agent-brief-schema-for-specialist-roles** —
briefs are per-task, definitions are per-role, and the two are meant to
compose, not duplicate each other.

## What's in this repo

```
PATTERN.md                              the pattern itself (start here)
agents/
  records-keeper.md                     haiku — mechanical bookkeeping example
  document-intake.md                    sonnet — pipeline execution example
  OPUS-TIER.md                          note on the judgment tier + external link
  release-notes-trio/
    changelog-appender.md               haiku
    release-notes-drafter.md            sonnet
    release-gate-reviewer.md            opus
```

Every example agent uses invented domains and clearly-fictional example
filenames/content (`DECISIONS.md`, `logs/task_ledger.csv`, `CHANGELOG.md`,
etc.) — none of it is drawn from any specific production project, and none of
it should be treated as such.

## Limitations

- This is a documentation and worked-example repo, not a library or a CLI
  tool. There's nothing to install and nothing that runs — you read
  `PATTERN.md`, look at the example files, and adapt them by hand.
- The pattern describes conventions this repo's author has found useful for
  structuring `.claude/agents/*.md` files. It is not an official Claude Code
  specification, and Claude Code will happily run agent files that ignore
  every recommendation here — the `description`-as-router behavior and the
  `model:` field are the only parts backed by actual Claude Code mechanics;
  the rest (the skill/agent split, restating rules inline, the
  standing-decision rule) is authoring discipline, not something the tool
  enforces for you.
- The worked examples are deliberately small and synthetic. A real production
  agent file will usually need a longer, more specific tool list, a fuller
  file allowlist, and rules specific to its own project's actual formats —
  the examples here show the *shape*, not a template to use unedited.
- The model-tier guidance in §3 of `PATTERN.md` is a design heuristic based
  on observed failure patterns, not a benchmarked recommendation. Treat it as
  a starting point for judgment, not a rule to apply mechanically without
  checking it against your own task.
