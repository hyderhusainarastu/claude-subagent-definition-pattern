# Decision record template

Copy one block per decision into your project's decision log (for example `DECISIONS.md`). Entries are append-only: a changed decision gets a new entry that supersedes the old one, and the old one is marked SUPERSEDED, not deleted.

```markdown
## D-<number>: <short title>

- **Date:** YYYY-MM-DD
- **Status:** proposed | accepted | SUPERSEDED by D-<number>
- **Decided by:** <person or role with authority to decide>
- **Context:** what forced a decision, in two or three sentences.
- **Options considered:**
  1. <option> - <cost or risk>
  2. <option> - <cost or risk>
- **Decision:** the option chosen, in one sentence.
- **Why:** the evidence or constraint that tipped it.
- **Consequences:** what changes, what is now harder, what to revisit and when.
- **Binds agents to:** the rule agents must apply without re-litigating it.
```

Agents treat an `accepted` entry as a standing ruling: apply it, flag any tension with new evidence, never override it (see PATTERN.md section 6).
