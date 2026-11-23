# A note on the judgment tier

The two worked examples in `agents/` (`records-keeper.md`,
`document-intake.md`) cover the mechanical and pipeline tiers of the pattern
described in `../PATTERN.md`. This file is a short note on the third tier —
the judgment tier (the large tier in the mapping in PATTERN.md) — rather than a full worked example, because a
judgment-tier agent's real substance is domain-specific: the evidence bar, the
findings taxonomy, and the verdict vocabulary all depend heavily on what is
actually being judged (a code review, an editorial review, a compliance
review, a release gate). A generic judgment agent that doesn't commit to a
concrete evidence standard is not actually demonstrating the pattern — it's
demonstrating a shell.

What every judgment-tier agent definition should still include, regardless of
domain (see §3 of `../PATTERN.md` for the reasoning):

- **An explicit evidence bar.** State what a finding has to trace to before
  it's admissible (a specific file/line, a specific quoted passage, a
  specific rule reference) — never "asserted," always "shown."
- **A severity/findings taxonomy.** A small fixed vocabulary (for example:
  severe / major / moderate / minor) so verdicts are comparable across runs
  and reviewers.
- **Explicit permission to return a negative verdict.** State plainly that a
  negative outcome (reject, fail, block, request changes) is an admissible
  result, and that softening a verdict toward what the requester likely
  hoped for is a failure mode to actively resist — this is the single most
  common way judgment-tier agents go wrong.
- **An output-only discipline.** A judgment agent typically writes exactly one
  review artifact and touches nothing else — it recommends, it doesn't repair.
  Repairs belong to the executor agents its findings get routed back to.
- **The same standing-decision rule as every other tier** (§6 of
  `../PATTERN.md`): if the evidence in front of it seems to cut against a
  standing human decision, it still doesn't get to overrule that decision —
  it reports the tension as part of its review.

For a complete, concrete reviewer-persona template that fills in all of the
above for an adversarial code/document review role — including the exact
evidence-bar wording, the severity taxonomy, and the findings-format
convention — see:

**github.com/hyderhusainarastu/adversarial-peer-review-role**

That template is not reproduced here; this repository stays focused on the
definition-file pattern itself rather than duplicating a full persona that
already has its own home.
