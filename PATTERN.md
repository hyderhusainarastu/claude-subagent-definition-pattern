# The Subagent Definition Pattern

A subagent definition is a Markdown file in `.claude/agents/` that Claude Code loads as a
delegatable role. This guide covers what belongs in that file, what does not, and where the
"what does not" should live instead.

The short version:

> A **skill** describes work that any caller might need to do.
> An **agent definition** describes the *executor* that does it: which model runs, which files
> it may write, which rules it may never break, and what it must hand back.

Everything below elaborates that split.

---

## 1. Anatomy

```markdown
---
name: records-keeper
description: "Mechanical governance-records agent for DECISIONS.md, the task ledger, and OPEN_QUESTIONS.md. Use for all bookkeeping and logging tasks."
model: haiku
---

You are the mechanical governance-records agent for this project (<project-root>). You append
rows and entries exactly as briefed — no interpretation, no substantive work. Follow the
records-update skill for all formats.

## Hard rules (restated inline — no lookup needed)
...

## Working method
...

## Output
...
```

Four moving parts:

| Part | Job |
|---|---|
| `name` | The address. How a caller asks for this role by hand. |
| `description` | The **router string**. How the model decides to delegate here on its own. |
| `model` | The tier. Sets both cost and how much judgment the role is permitted. |
| Body | The standing brief: constraints, method, output contract. |

---

## 2. `description` is a router string, not a bio

This is the field people get wrong most often, because it looks like a place to describe the
agent. It is not. It is the text an orchestrating model reads when it is deciding *whether to
hand this task off*. It is matched against an incoming task, not read for color.

So it must name **the trigger condition**, in the vocabulary the caller will actually be using.

**Weak — describes personality:**

```yaml
description: "A careful, detail-oriented agent that values accuracy and never cuts corners."
```

Nothing in there matches a task. "Careful" and "detail-oriented" are true of every role you
would ever write, so they carry no routing signal at all.

**Weak — too abstract to match:**

```yaml
description: "Handles project records."
```

Which records? A caller holding the task "log this decision and append a ledger row" has to
already know the answer to route correctly.

**Strong — names the artifacts and the trigger:**

```yaml
description: "Mechanical governance-records agent for DECISIONS.md, the task ledger, and OPEN_QUESTIONS.md. Use for all bookkeeping and logging tasks."
```

```yaml
description: "Document-intake agent: processes new files through the metadata / classification / extraction / manifest / provenance pipeline. Use when new documents arrive in the intake directory."
```

The shape that works is two clauses:

1. **What it is**, with the concrete nouns a task will contain — real filenames, real directory
   names, the domain terms your project uses.
2. **When to use it**, phrased as the condition, starting with "Use when…" or "Use for…".

Rules of thumb:

- Put the **filenames and paths** in. `DECISIONS.md` is a routing keyword; "records" is not.
- Put the **arrival event** in for pipeline roles. "Use when new documents arrive in the intake
  directory" catches a task the model would otherwise route to a generic file-handler.
- Keep it to one or two sentences. It is an index entry.
- Do **not** put instructions in it. The body is for instructions; anything you write here is
  spent on routing, and long descriptions dilute the match.
- Do not write "expert" or "senior" or "world-class". They match everything, which means they
  match nothing.

Testing it is easy: write down three task strings you expect to arrive, and one you expect to be
routed elsewhere. If the description does not obviously catch the three and obviously miss the
fourth, rewrite it.

---

## 3. Model tiering

The `model` field is a real design decision, not a cost knob you set last. Pick the tier from
the *kind of judgment the role is allowed to exercise*.

| Tier | Kind of work | Judgment permitted |
|---|---|---|
| `haiku` | Mechanical, append-only, format-matching. Copy values from a brief into a known row shape. | None. Every field value comes from the brief or from the file. A gap gets reported, never filled. |
| `sonnet` | Multi-step pipeline execution. Run an ordered procedure over an input, using tools, producing several coordinated artifacts. | Local and procedural. Decide *how* to extract, *whether* a record is a duplicate — not whether the rules are right. |
| `opus` | Adversarial judgment. Verdicts, sign-offs, rulings, reviews that can block work. | Substantive. The role's whole value is disagreeing with the person who asked. |

### The tier/body correlation

Look at the three definitions in this repo and in the trio, and a pattern shows up that is worth
naming explicitly: **the higher the tier, the more of the body is about standards rather than
steps.**

- The **haiku** body is mostly a *file allowlist and a format-matching discipline*. It is short.
  It spends its words on what the agent must not touch and on "read the existing format first".
  There is almost no "how to think" content, because there is no thinking in the job.
- The **sonnet** body is mostly a *pipeline recap plus a tool list plus constraints*. It is
  medium-length. It names the ordered steps (delegating their detail to the skill), lists the
  binaries and environments available, and spends the rest on what to do when reality does not
  match the procedure — report the discrepancy, do not silently repair it.
- The **opus** body is mostly an *evidence bar and an output discipline*. It is the longest, and
  nearly none of it is procedure. It specifies what counts as proof, what severity labels mean,
  which verdicts are admissible, and — critically — that negative verdicts are permitted. A
  judgment agent with no explicit statement that "REJECT is an allowed outcome" will drift
  toward agreement.

If you find yourself writing a long, standards-heavy body for a `haiku` agent, you have
mis-tiered the role. If you find yourself writing step-by-step procedure for an `opus` agent,
either the work is not judgment work, or the procedure belongs in a skill.

### The opus slot

This repo deliberately does not ship a full opus judgment-agent template, because a good one is
long enough to be its own artifact and one already exists:

**→ [adversarial-peer-review-role](https://github.com/hyderhusainarastu/adversarial-peer-review-role)**

That repo ships the full persona: evidence bar, severity taxonomy, verdict vocabulary,
disconfirmation discipline, and the one-artifact output rule. Drop its role text into the body
of an `.claude/agents/*.md` file with `model: opus` and the frontmatter shape shown in §1, and
you have the third tier of this pattern. The synthetic `release-gate-reviewer` in
`agents/release-notes-trio/` shows a compact, domain-specific version of the same shape. The checklist of what any
judgment-tier definition must contain, whatever the domain, is in
[`docs/judgment-tier.md`](docs/judgment-tier.md).

---

## 4. What goes in the skill, what goes in the agent definition

Both files describe the same work. They are not redundant if you split them on **audience**:

- The **skill** is read by *anyone doing this kind of task*, including the orchestrator working
  directly, a different agent, or a human. It is shared reference.
- The **agent definition** is read by *one executor at the moment it is spawned*. It is that
  executor's contract.

| Belongs in the skill | Belongs in the agent definition |
|---|---|
| Exact column schemas, header rows, table shapes | The model tier |
| Worked format examples ("a real row looks like this") | The file allowlist — what this executor may write, and the explicit "never" list |
| The ordered pipeline steps and what each produces | Which tools/binaries/environments this executor has |
| Classification rules and their evidence requirements | The hard rules, restated (see §5) |
| Naming conventions, directory layout, status vocabularies | The output contract — exactly what comes back to the caller |
| Cross-file invariants (e.g. "these two manifests never diverge") | Escalation behavior on conflict (see §6) |

Two consequences worth stating plainly:

**A skill with no agent is fine.** Formats are useful to whoever is holding the keyboard.

**An agent with no skill is a smell.** If the definition body has grown a full format
specification inside it, that specification is now invisible to every other caller and will
drift from the files it describes. Move it to a skill and point at it.

The test for any given line: *would a person doing this task by hand need to know it?* If yes,
it is skill content. If it is only true because a delegated executor with limited context and
write access is doing the work, it is definition content.

---

## 5. Restate the hard rules inline, even though the skill documents them

The definitions in this repo repeat their skills. `records-keeper` restates the file allowlist,
the append-only rule, and the no-commits rule, all of which are already written in the
records-update skill. That duplication is deliberate.

Why:

1. **A skill reference is a lookup; the body is already loaded.** The body is in context from the
   first token of the agent's run. A constraint that requires opening another file is a
   constraint that can be missed under load, mid-task, on step nine of eleven.
2. **The unrecoverable ones deserve belt and braces.** Appending a row in the wrong column order
   is a fixable mistake. Writing to a file the role was never supposed to touch, deleting an
   append-only record, or committing to version control may not be. The cost of the duplication
   is a few lines; the cost of the miss is the thing the rule exists to prevent.
3. **The skill is shared and will be edited by others.** A format change should propagate. A
   safety constraint should not silently disappear from a role because someone reorganized a
   shared reference file.
4. **It makes the contract legible in one place.** A reviewer asking "what can this thing
   damage?" reads one file and gets a complete answer.

**What to restate:** constraints whose violation is expensive or irreversible — file allowlists,
append-only rules, write-tool prohibitions, network/egress limits, "never invent a value"
rules, concurrency rules.

**What not to restate:** formats, schemas, column lists, worked examples, step detail. Those
belong in the skill and only in the skill, precisely because they change.

Label the section so its redundancy reads as intentional rather than as drift:

```markdown
## Hard rules (restated inline — no lookup needed)
```

---

## 6. The escalation rule: apply the ruling, flag the tension, never silently override

Every long-running project accumulates standing rulings — decisions a human made once that
subsequent work is supposed to honor. Sooner or later, an executor will encounter evidence that
seems to contradict one.

There are three things it can do, and only one of them is acceptable.

| Behavior | Outcome |
|---|---|
| Silently follow the evidence, overriding the ruling | The project's records now contain a decision nobody made. Worse, nobody knows. |
| Silently follow the ruling, discarding the evidence | The ruling never gets revisited. The contradiction is now invisible and permanent. |
| **Apply the ruling, and report the tension** | The record stays consistent, and the human gets what they need to revise the ruling if it deserves revising. |

State it in the definition, in the imperative:

```markdown
3. **Never override a standing human ruling.** If evidence appears to contradict a recorded
   ruling ([[STANDING-RULE-ID]] in DECISIONS.md), apply the ruling as written *and* report the
   tension in your output — quoting the evidence and naming the ruling. Never resolve the
   conflict yourself in either direction, and never leave it unreported.
```

Three details that make it work in practice:

- **Name the record.** "Standing rulings" is abstract; `DECISIONS.md` and a rule ID are
  addressable. The agent needs to know where rulings live to recognize one.
- **Require the evidence in the report.** "I noticed a tension" is unactionable. The quoted
  passage plus the location is actionable.
- **Give the flag a home in the durable record too**, not just in the chat reply — an open
  question entry, a blockers field in the ledger row. Reports scroll away; records do not.

The same shape generalizes past rulings. It is the correct default for *any* discrepancy an
executor finds and was not asked to fix: manifest divergence, a duplicate row, a missing
provenance file, a misnamed slug. **Report discrepancies rather than silently repairing them,
unless the brief says otherwise.** An agent that quietly tidies things up destroys the evidence
that something upstream is broken.

---

## 7. The output contract

Every definition ends with a section saying exactly what comes back. This is the part most
often left implicit, and it is the part the caller depends on most.

A good output contract is specific about **shape**, not just topic:

```markdown
## Output

Return a verbatim diff-style report: for each file touched, the filename and the exact lines
appended (quoted verbatim), plus a one-line note of any format anomaly or discrepancy found.
```

Note what it does: the caller can verify the work *from the report alone*, without re-reading
the files. "Quoted verbatim" is doing the load-bearing work there.

For pipeline roles, enumerate the fields:

```markdown
## Output

Report per document: slug, metadata verified (with evidence location in the document),
classification status plus its evidence, dedupe result, extraction status and word count, files
written, request-tracking updates, and any discrepancies found.
```

For judgment roles, specify the artifact and the terminal line:

```markdown
## Output discipline

Write exactly one output file per review, at the path given in the task brief. Touch nothing
else. End with an explicit verdict line (PASS / REVISE / MAJOR-REVISION / BLOCKED) and a
numbered list of required changes.
```

The "touch nothing else" clause matters for reviewers specifically: a reviewer that fixes what
it finds has destroyed its own audit trail and put unreviewed edits into the tree.

---

## 8. Write ownership

When more than one role can write the same file, say so in both definitions. The cheapest
version is a rule that makes the agent stop rather than race:

```markdown
6. **Serialize ledger writes.** Never assume exclusive access — if the brief indicates another
   agent may be writing the same file, stop and report instead of appending.
```

This is definition content, not skill content: it exists only because work is being delegated in
parallel. A person doing the task by hand does not need it.

---

## 9. Anti-patterns

| Anti-pattern | Fix |
|---|---|
| `description` describes the agent's temperament | Rewrite as trigger condition + concrete nouns |
| `description` is three paragraphs of instructions | Move them to the body; the description is an index entry |
| Every agent is `sonnet` because it is the safe middle | Tier by judgment permitted; mechanical work is cheaper *and* more reliable on `haiku` |
| Column schemas pasted into the definition body | Move to a skill; keep the pointer |
| No file allowlist | Add one, with an explicit "never" list. This is the single highest-value line in most definitions |
| No output contract | Add one. Specify shape, not topic |
| "Fix any problems you find" | Replace with "report discrepancies rather than silently fixing them, unless the brief says so" |
| Judgment agent with no statement that negative verdicts are allowed | State it. Explicitly. Agreement is the default failure mode |
| Absolute machine paths in the body | Use a project-root placeholder, so the file survives being cloned |

---

## 10. Review checklist

Before committing a new definition:

- [ ] `description` names concrete artifacts and a trigger condition, in one or two sentences.
- [ ] Three plausible incoming tasks would route here; one adjacent task would not.
- [ ] `model` matches the judgment the role is permitted to exercise.
- [ ] The formats live in a skill, and the body points at it.
- [ ] The unrecoverable constraints are restated inline, under a label that says so.
- [ ] There is a file allowlist with an explicit "never" list.
- [ ] Escalation on conflict is stated: apply, flag, never silently override.
- [ ] Discrepancy handling is stated: report, do not silently repair.
- [ ] The output contract specifies shape well enough for the caller to verify the work from the
      report alone.
- [ ] No absolute machine paths.

---

## 11. One source for shared rules: the generator

Definition files cannot include other files, so a rule block that every role needs ends up
copied into each file, and the copies drift. `tools/gen_agents.py` keeps one source:

- `agent_src/preamble.md` holds the shared rules.
- `agent_src/<role>.md` holds one role, with a `{{PREAMBLE}}` marker where the shared rules go.
- `python3 tools/gen_agents.py --src agent_src --out .claude/agents` writes the finished files.
- `--check` writes nothing and exits 1 if any generated file is missing or stale. Run it in CI
  or in a pre-commit hook so nobody edits the output by hand.

This repo ships five generic roles built that way (`architect`, `implementer`, `judge`,
`reviewer`, `mechanical`; output in `agents/generated/`) and a decision-record template in
`templates/decision-record.md` for the standing-decision rule in section 6.

---

## 12. Portability

The pattern (router description, tiered body, inline hard rules, output contract) is
tool-neutral. Only the file location and format change. Locations below were checked against
each vendor's documentation on 2026-11-23.

| Tool | Project location | User location | Format | Source |
|---|---|---|---|---|
| Claude Code | `.claude/agents/<name>.md` | `~/.claude/agents/` | Markdown + YAML frontmatter | https://code.claude.com/docs/en/sub-agents |
| Codex | `.codex/agents/<name>.toml` | `~/.codex/agents/` | one TOML file per agent (`name`, `description`, instructions) | https://developers.openai.com/codex/subagents |
| Cursor | `.cursor/agents/<name>.md` | `~/.cursor/agents/` | Markdown + YAML frontmatter; also reads `.claude/agents/` and `.codex/agents/` | https://cursor.com/docs/context/subagents |
| Gemini CLI | `.gemini/agents/<name>.md` | `~/.gemini/agents/` | Markdown + YAML frontmatter; body is the system prompt | https://geminicli.com/docs/core/subagents/ |

What carries over unchanged: the description-as-trigger rule, the body shape per tier, the
allowlist, the output contract. What does not: the `model:` values and other frontmatter
fields are each tool's own. Check the linked page before copying a file across tools, and
re-run `tools/check_frontmatter.py --models <your values>` against the values that tool accepts.

### Tier mapping

Pick the tier by the kind of work (section 3), then use whatever your tool calls that size.

| Tier | Kind of work | Claude Code `model:` alias used in this repo | Other tools |
|---|---|---|---|
| small | mechanical, append-only | `haiku` | the tool's smallest or fastest model |
| medium | multi-step pipeline execution | `sonnet` | the tool's default mid-size model |
| large | adversarial judgment, verdicts | `opus` | the tool's strongest reasoning model |

The mapping is a starting heuristic, not a benchmark. Test a role at the tier you picked before
trusting it.
