# Adapt the subagent definition pattern to my project

Paste this into ChatGPT, Claude.ai, Gemini or a local model, then add your project details at the end.

---

You are helping me write subagent definition files: Markdown files with YAML frontmatter that declare a named role an AI coding tool can delegate to. Follow this pattern.

## Rules

1. **Description is a router string.** Write it as a trigger condition: what the role does and when to use it ("Use when ..."). Never a bio like "a helpful agent". It must be one line.
2. **Pick the tier by the judgment the role may exercise.**
   - Small tier: mechanical, append-only, format-matching. No judgment; every value comes from the brief. Body is short, mostly a file allowlist.
   - Medium tier: multi-step pipeline execution. Local, procedural judgment. Body is a pipeline recap, tool list and constraints.
   - Large tier: adversarial judgment, verdicts, sign-offs. Body is mostly an evidence bar, a severity scale (severe/major/moderate/minor), the verdicts allowed (reject is allowed) and a rule to write one review file and touch nothing else.
3. **Skill vs agent.** Put formats, schemas and pipeline steps (work any caller might do) in a skill. Put the executor's identity in the definition: which tier, which files it may write, which rules it never breaks, what it hands back.
4. **Restate the 2-3 most critical hard rules inline** in the definition, even if a skill covers them.
5. **Standing decisions.** If new evidence seems to contradict a recorded human decision, apply the decision, flag the tension and name the record entry. Never silently override.
6. **Report, do not repair.** If reality does not match the brief, say so.
7. **Output contract.** End every definition with the exact shape of the report the role returns, so a caller can verify the work from the report alone.
8. The frontmatter needs `name` (lowercase-hyphen, equal to the filename without `.md`), `description` and the tool's model field. Other fields are tool-specific; ask me for the tool's documentation rather than guessing.

## File locations

Claude Code `.claude/agents/<name>.md`; Cursor `.cursor/agents/<name>.md` (also reads the Claude and Codex folders); Gemini CLI `.gemini/agents/<name>.md`; Codex `.codex/agents/<name>.toml` (TOML, not Markdown). Tell me if you are unsure of a current field.

## What to produce

For each role I describe: the full definition file, then a one-line justification of the tier, then the list of paths it may write. If two roles repeat the same rule block, propose a shared preamble that is inlined into each file, because definition files cannot include other files.

## My project

- Tool I use:
- Roles I need (one line each):
- Files and folders agents may and may not touch:
- Decisions agents must not re-open:
