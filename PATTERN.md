# The Subagent Definition Pattern

A guide to writing `.claude/agents/*.md` files for Claude Code — the format that
declares a project-local subagent: a named role Claude Code can invoke (by name
or by auto-routing) to run a bounded piece of work with its own model tier and
its own rules.

This document teaches the pattern in the abstract. The `agents/` directory next
to it shows the pattern applied to two invented domains (records bookkeeping
and document intake, plus a release-notes trio) so you can see the shape
without borrowing anyone's real project content.

---

## 1. The file format, briefly

A subagent definition is a Markdown file with YAML frontmatter:

```markdown
---
name: some-agent-name
description: "One sentence stating exactly when this agent should fire."
model: haiku | sonnet | opus
---

Body: who this agent is, what it's allowed to touch, its hard rules,
its working method, and its output contract.
```

`name` is the identifier used to invoke the agent explicitly. `description` and
`model` do more work than their brevity suggests — the rest of this guide is
mostly about those two fields and about what belongs in the body.

---

## 2. The description field is a router, not a bio

It is tempting to write the `description` field the way you'd write a job
title on a business card: "A helpful assistant for managing project records."
That is the wrong instinct.

Claude Code (and any orchestrator built on the same convention) reads the
`description` field to decide, automatically, whether a given task should be
routed to this agent instead of another one, or handled inline. The field is
matched against the task at hand, not read by a human deciding whether to hire
someone. Write it as a **trigger condition**: the concrete situations that
should cause this agent to fire, and the concrete class of task it covers.

**Weak (personality blurb):**

> "A careful, detail-oriented agent that helps keep project records neat and
> up to date."

This tells the router nothing about *when* to pick it over any other agent
that also sounds careful and detail-oriented.

**Strong (trigger condition):**

> "Mechanical bookkeeping agent for the decisions log and task ledger. Use for
> all append-only record-keeping tasks — new decision rows, ledger rows, status
> flips. Not for anything that requires judgment about what the record should
> say."

Notice the second version names the exact files/record types it covers, states
the affirmative trigger ("use for..."), and — often just as valuable — states
what it is *not* for, so a near-miss task doesn't get misrouted to it. A good
description usually has three parts: **what class of task**, **what
trigger phrase or file pattern** should cause a match, and **what it
excludes**, if there is likely to be a confusable neighbor agent (as there
almost always is between a mechanical agent and a judgment agent working the
same domain).

A practical test: if you deleted the agent's name and body and handed a
stranger only the `description` field alongside five other agents'
descriptions, could they correctly route an incoming task to yours? If not,
the field is a bio, not a router — rewrite it as a condition.

---

## 3. Choosing the model tier by work type, not by budget

The `model:` field is a scope decision as much as a cost decision. A useful
first cut is to bucket the work itself into three shapes, then let the model
follow:

| Work shape | Model | Why |
|---|---|---|
| Mechanical, append-only, format-matching. No interpretation of content, no judgment calls, one right answer per input. | `haiku` | The task is "copy this into that shape correctly." A larger model buys nothing here except cost — the constraint is following a format exactly, not reasoning. |
| Multi-step pipeline execution with several ordered stages, each with its own decision points, but every decision point is governed by a documented rule (a classification scheme, a dedupe policy, a naming convention). | `sonnet` | The task requires tracking pipeline state and applying several different rules in sequence, but doesn't require originating a judgment the rules don't already answer. |
| Adversarial judgment, sign-off/veto authority, or any call where the "right" answer is contestable and the agent's job is specifically to argue a position (find what's wrong, decide if a bar is met, rule on a genuine tradeoff). | `opus` | The task is evaluative rather than executional — it has to weigh, not just apply. |

This is a real design signal, not a cost-optimization footnote: assigning a
task shape to the wrong tier tends to fail in a specific, recognizable way.
Give a `haiku`-shaped bookkeeping task to an `opus` agent and you'll usually
still get correct output, just at higher cost and often with unwanted
editorializing — a judgment-tier agent tends to "improve" content it was only
supposed to transcribe. Give an `opus`-shaped adversarial-review task to a
`haiku` agent and the reviews will read confident but hollow: findings won't
trace to real evidence, and negative verdicts will get softened toward
whatever the input seems to want, because genuinely holding a contestable
position under scrutiny is exactly the capability that tier lacks.

### Body length and content track the tier

One more useful signal falls out of this bucketing almost for free: **the
length and content of the agent's body should roughly track its tier**, and
if it doesn't, that's worth noticing.

- A `haiku` mechanical agent's body is typically the shortest of the three:
  a file allowlist, a handful of hard rules restated inline, and a pointer to
  the exact format(s) it must match. It should not contain prose reasoning
  about *why* a format is shaped the way it is — that reasoning belongs
  upstream, in the format's own documentation, not in the executor.
- A `sonnet` pipeline agent's body is usually the longest of the three in
  practical terms: it has to enumerate pipeline stages in order, name the
  tooling available, and state the hard constraints governing each stage,
  because it is the one actually walking the pipeline.
- An `opus` judgment agent's body is often the shortest in step-count but the
  densest in standard: it doesn't need a long procedure, but it needs a
  precisely stated evidence bar, a findings taxonomy (severity labels), and
  an explicit instruction that negative verdicts are permitted and expected
  where warranted — because the natural failure mode at this tier is
  softening a verdict toward what the requester hoped to hear.

If you find yourself writing three paragraphs of nuanced judgment-calls into a
`haiku` agent's body, that's usually a sign the task itself is judgment-shaped
and belongs on a higher tier — not a sign the agent needs a longer prompt.
Conversely, if an `opus` agent's body reads like a step-by-step checklist with
no standard for what counts as a defect, the task may actually be mechanical
and overpaying for judgment it isn't using.

---

## 4. The skill/agent split

Projects that use both `.claude/skills/` and `.claude/agents/` run into a
predictable failure: content ends up in the wrong layer, duplicated across
both, or missing from the one place that actually needed it. The clean split:

- **A skill documents a shared format or procedure that any caller might
  need** — the exact column schema for a CSV, the classification rules for a
  four-way category system, the ordered steps of a pipeline. A skill is
  reference material. It doesn't know who is calling it or what model tier
  they run at. Multiple agents (and a human, and a different orchestrator)
  can all point at the same skill.

- **An agent definition holds only what a specific executor needs to run**:
  which model tier it runs at, which files it's allowed to touch (a file
  allowlist), the hard rules that constrain its specific behavior, and the
  output contract — the shape of what it must report back. An agent
  definition is not the place to explain *why* a rule exists, or to fully
  restate a format's schema when a skill already owns that schema.

A useful check: if you deleted every other agent that might call a given
skill, would the skill still make sense as a standalone reference document?
If yes, it's correctly a skill. If it only makes sense in the context of one
specific agent's job, it probably belongs in that agent's body instead.

---

## 5. Restate critical rules inline, even when a skill documents them

This looks like it contradicts §4, but it doesn't — it's the pattern's most
important refinement of it.

Even when a skill fully documents a rule (a file allowlist, a "never delete,
only append" policy, a "no git commits" constraint), **the agent definition
should still restate the two or three rules that would be catastrophic to
violate**, directly in its own body, in a short "hard rules" section near the
top.

The reason is structural, not redundancy for its own sake: an agent's body is
guaranteed to be in context every time it runs. A skill it's told to "follow"
is a pointer — it depends on the agent actually reading it, correctly, every
single invocation, with no lossy summarization along the way. For rules where
a miss is expensive (deleting instead of appending; writing outside an
allowlisted directory; silently overriding a standing decision), don't bet the
outcome on a lookup succeeding. State the load-bearing rules twice: once in
the skill (the canonical, fully-explained version, for anyone who needs the
reasoning) and once, tersely, inline in every agent body that must obey it
(the "no lookup needed" version, so the agent is safe even in a degraded
context).

A good test for which rules earn this treatment: ask "if this agent silently
violated the rule and nobody caught it for a while, how bad is that?" Rules
that answer "very bad, and hard to undo" (deleting append-only history,
writing outside the allowed root, committing without authorization) get
restated inline. Rules that answer "annoying but recoverable" (a formatting
nit, a preferred phrasing) can safely live only in the skill.

---

## 6. When evidence conflicts with a standing decision: follow it, report it, never override it

Any sufficiently long-running agent-run project accumulates standing
decisions — rulings a human made earlier that later work is supposed to
respect, even when new evidence arrives that seems to cut against them. A
records agent might encounter a new fact that seems to argue against a
decision already logged. A pipeline agent might process a new document whose
evidence seems to contradict a classification rule a human previously
confirmed. This is not a rare edge case — it is close to guaranteed to happen
in any project with enough history behind it, and it is the single place
subagents most often make an authority mistake.

The pattern's rule is a strict three-step sequence, and the order matters:

1. **Follow the standing decision as written.** Do not treat apparently
   contradicting evidence as license to reinterpret, narrow, or quietly set
   aside a ruling a human already made. The agent's evidence, however
   compelling it looks in the moment, is not a substitute for the human
   revisiting the decision themselves.
2. **Report the conflict explicitly**, in the agent's output, with the
   specific evidence that seems to cut against the standing decision named
   and located (not just gestured at). The report has to be findable — buried
   in a large output the human won't read in full defeats the point.
3. **Never silently resolve it either way.** Don't quietly apply the standing
   decision and drop the tension unmentioned (that hides a live problem from
   the human who needs to see it), and don't quietly apply the *new* evidence
   instead of the decision (that's the override this rule exists to prevent).
   The agent's job is to surface the tension, not adjudicate it.

This keeps a clean authority boundary: standing human decisions are read-only
ground truth for every agent below the human, no matter how model-tier-heavy
that agent is — an `opus` judgment agent gets exactly the same instruction as
a `haiku` bookkeeping agent on this point. The only thing model tier changes
is who is *allowed* to originate a proposal to revisit the decision, not
whether they may unilaterally act as though it's already changed.

---

## 7. A minimal checklist

Before you commit a new `.claude/agents/*.md` file, check:

- [ ] `description` reads as a trigger condition ("use when X"), not a bio.
- [ ] `description` states what the agent is *not* for, if a confusable
      neighbor agent exists in the same domain.
- [ ] `model:` matches the work's actual shape (mechanical / pipeline /
      judgment), not a default or a guess.
- [ ] The body's length and content roughly track the chosen tier.
- [ ] Anything a shared skill already documents in full is referenced, not
      copy-pasted wholesale into the agent body.
- [ ] The two or three rules whose silent violation would be catastrophic are
      restated inline in the agent's own body regardless.
- [ ] The body states what happens when evidence conflicts with a standing
      decision: follow it, report the conflict, never override it silently.
- [ ] The body ends with an explicit output contract — what the agent must
      report back, and in what shape.

See `agents/records-keeper.md` and `agents/document-intake.md` for two worked
examples applying every point above, `agents/OPUS-TIER.md` for a short note on
the judgment tier specifically, and `agents/release-notes-trio/` for the same
three-tier shape applied to an unrelated domain, to confirm the pattern
generalizes rather than being specific to record-keeping.
