# claude-subagent-definition-pattern

A guide, worked examples, a frontmatter linter and a single-source generator for writing AI subagent definition files.

## Using this in your project

- Read `PATTERN.md` before writing or editing a subagent definition file. It covers the description as a trigger string, tier choice, the skill vs agent split, inline hard rules, escalation, output contracts and portability.
- Write each definition with a `description` that names a trigger condition ("Use when ..."), not a personality.
- Pick the tier (small, medium, large) from the kind of judgment the role may exercise, not from cost.
- Restate the two or three hard rules inline in the definition even if a skill documents them.
- Lint definitions: `python3 tools/check_frontmatter.py [--models a,b] [--require a,b] [--json] FILES`.
  Exit codes: 0 all pass, 1 a file failed or none found, 2 usage error.
- Share one rule block across roles with `python3 tools/gen_agents.py --src agent_src --out <agents dir>`. Add `--check` in CI. Never edit generated files by hand; edit the source and regenerate.
- Agent file locations differ per tool (see "Portability" in `PATTERN.md`). Copy the shape, then check that tool's current docs for its fields.
- Never invent frontmatter fields or model names for a tool; check its docs.
- Treat the examples as placeholders: replace `<project-root>`, `[[STANDING-RULE-ID]]` and `[[YOUR-GATE-NAME]]`.
- No PROMPT.md is needed for the tools, but `PROMPT.md` here is a paste-in version of the pattern for chat UIs.

## Working on this repo

- Setup: none. Python 3.10+, standard library only (PyYAML is used if installed).
- Test: `python3 -m unittest discover -s tests` (runs offline).
- Regenerate the sample roles: `python3 tools/gen_agents.py --src agent_src --out agents/generated`.
- Keep examples synthetic: no real project names, paths or data.
- Do not edit `agents/generated/` directly.

<!-- cc-only -->
Claude Code loads definitions from `.claude/agents/` (project) and `~/.claude/agents/` (user). Run `tools/check_frontmatter.py .claude/agents/*.md` before committing changes there.
<!-- /cc-only -->
