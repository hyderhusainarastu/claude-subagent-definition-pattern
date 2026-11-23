# The same pattern, a different domain

These three definitions are entirely fictional — an invented software project that ships releases
and keeps a changelog. They exist to show that the tiering is a property of the *kind of work*,
not of any one project's subject matter.

Set them beside the examples in the parent directory:

| Tier | Records/documents domain | Release domain | Shared shape |
|---|---|---|---|
| `haiku` | `records-keeper` | `changelog-appender` | Append-only, format-matching, file allowlist, never invent a field |
| `sonnet` | `document-intake` | `release-notes-drafter` | Ordered pipeline, tool list, stop-and-report on a blocked step, one ledger row |
| `opus` | *(see parent README)* | `release-gate-reviewer` | Evidence bar, severity taxonomy, negative verdict explicitly admissible, one artifact, touch nothing else |

Read across a row and the bodies rhyme almost line for line, in different vocabulary. Read down a
column and the bodies change character completely: allowlists become pipelines become standards.
That is the pattern.

The three constants that appear in all six definitions, at every tier:

1. **A file allowlist**, with an explicit "never" list.
2. **Report discrepancies rather than silently repairing them.**
3. **Apply a standing ruling, flag the tension, never silently override.**

Placeholders (`<project-root>`, `[[STANDING-RULE-ID]]`, `[[YOUR-GATE-NAME]]`) work the same way
here as in the parent directory.
