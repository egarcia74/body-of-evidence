# Governance

## Purpose

This document describes how Body of Evidence makes decisions — about investigations, methodology, architecture, and editorial matters. Good governance is essential for a platform whose trustworthiness depends on transparent, consistent process.

---

## Roles

### Maintainer

Maintainers have merge rights on the main branch and are responsible for the technical and editorial health of the platform. Maintainers are listed in [CODEOWNERS](.github/CODEOWNERS).

Maintainers are responsible for:

- Reviewing and merging PRs
- Ensuring methodological consistency
- Resolving disputes
- Maintaining the roadmap
- Enforcing the Code of Conduct

### Lead Investigator

Each investigation has a designated lead investigator responsible for:

- Scoping the investigation
- Ensuring sources are documented with provenance
- Reviewing evidence submissions from contributors
- Signing off on findings before they move to `review` state

Lead investigators are named in the investigation's `investigation.yaml`.

### Reviewer

Any contributor who has had at least one investigation contribution merged may review PRs. Reviewers do not have merge rights but their approvals count toward the review threshold.

### Contributor

Anyone may open issues, submit PRs, or challenge claims. No prior contribution required.

---

## Decision-Making

### Routine Decisions

Minor changes (typo fixes, broken link repairs, documentation improvements, new source additions) are made by a single maintainer review and merge.

### Investigation Lifecycle Decisions

Moving an investigation from `draft` → `review` → `published` requires:

- Lead investigator sign-off
- At least one maintainer review
- All validation checks passing

### Architectural Decisions

Changes to schema, methodology, or core platform design require:

- A written proposal in the form of an issue
- At least 7 days open for discussion
- Consensus among active maintainers (no active objections from more than one maintainer)
- Documentation in [DECISIONS.md](DECISIONS.md) and/or `docs/adr/`

### Disputed Claims

When a contributor formally challenges a claim or finding:

1. The challenge is recorded as a `Review` entity with type `challenge`
2. The lead investigator has 30 days to respond
3. If the challenge cannot be resolved between challenger and lead investigator, a maintainer makes a final determination
4. The determination is documented in the `Review` entity
5. If the challenge is upheld, a `Revision` is created

### Conflict of Interest Recusals

Any maintainer or reviewer with a conflict of interest in an investigation must recuse themselves from decisions about that investigation. Recusals are documented in the relevant PR.

---

## Transparency

All governance decisions that affect published content are made in public (via GitHub issues and PRs). Private discussions about sensitive matters (e.g., source protection) are summarised publicly once the sensitivity is resolved.

The governance model itself can be changed through the Architectural Decision process above.

---

## Removal of Content

Published content is not removed except in the following circumstances:

1. Legal obligation (e.g., court order)
2. The content constitutes a genuine safety risk to an identified individual
3. The content is discovered to be fabricated in its entirety

In all cases, removal is documented with a `Revision` entity explaining what was removed and why. The removal itself is committed to the repository — the absence of content is part of the record.

---

## Code of Conduct Enforcement

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Maintainers are responsible for enforcement. Sanctions range from a warning to permanent ban from contributing, depending on severity and recurrence.
