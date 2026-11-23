# Worked examples

Every file here is illustrative. Filenames such as `DECISIONS.md`, `OPEN_QUESTIONS.md`, and
`logs/task_ledger.csv` are stand-ins for whatever your project actually calls its governance
records. Placeholders to replace before use:

| Placeholder | Replace with |
|---|---|
| `<project-root>` | The writable root of your project |
| `[[STANDING-RULE-ID]]` | The identifier scheme your recorded rulings use |
| `[[YOUR-GATE-NAME]]` | The name of the checkpoint the pipeline satisfies |

## The three tiers

| File | Tier | Role |
|---|---|---|
| [`records-keeper.md`](records-keeper.md) | `haiku` | Mechanical, append-only bookkeeping |
| [`document-intake.md`](document-intake.md) | `sonnet` | Multi-step pipeline execution |
| *(see below)* | `opus` | Adversarial judgment |
| [`release-notes-trio/`](release-notes-trio/) | all three | The same pattern in a software-release domain |

## The opus slot

This repo does not ship a full judgment-agent body, because a good one is long enough to be its
own artifact and one already exists:

**→ [adversarial-peer-review-role](https://github.com/hyderhusainarastu/adversarial-peer-review-role)**

That repo ships the complete persona: the evidence bar, the severity taxonomy, the verdict
vocabulary, the disconfirmation discipline, and the one-artifact output rule. To use it as a
subagent definition, put its role text in the body of a file in `.claude/agents/` with
frontmatter of this shape:

```yaml
---
name: adversarial-reviewer
description: "High-judgment adversarial reviewer for gate reviews and sign-offs. Use for substantive review verdicts."
model: opus
---
```

`release-notes-trio/release-gate-reviewer.md` shows a compact, domain-specific version of the
same shape, for when a full persona is more than the job needs. A short checklist of what every
judgment-tier definition should contain is in [`../docs/judgment-tier.md`](../docs/judgment-tier.md).
Generic role definitions generated from one shared preamble are in [`generated/`](generated/).

Why `opus` for this tier and nothing lower: the role's entire value is disagreement. A reviewer
that agrees is worse than no reviewer, because it produces a sign-off record with nothing behind
it. That is the one job where the model's willingness to hold a negative position under pressure
is the product.
