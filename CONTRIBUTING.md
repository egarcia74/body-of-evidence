# Contributing

Thank you for your interest in contributing to Body of Evidence. This document explains how to contribute effectively.

---

## Before You Start

Read these documents first. They contain the principles your contribution must uphold:

- [METHODOLOGY.md](METHODOLOGY.md) — how evidence is assessed
- [TERMINOLOGY.md](TERMINOLOGY.md) — shared vocabulary
- [ETHICS.md](ETHICS.md) — editorial ethics and conflicts of interest
- [STYLE_GUIDE.md](STYLE_GUIDE.md) — how to write claims, assessments, and sources

If your contribution doesn't align with the methodology, it will not be merged — not because we disagree with you, but because inconsistent methodology undermines the platform's trustworthiness.

---

## Types of Contribution

### 1. Evidence Submission
Adding new evidence to an existing investigation. Use the **Evidence Submission** issue template.

### 2. Claim Challenge
Formally challenging an existing claim or finding. Use the **Claim Challenge** issue template. A challenge must be evidence-based, not opinion-based.

### 3. New Investigation Proposal
Proposing a new investigation. Use the **New Investigation Proposal** issue template. Proposals require a defined scope, at least three identified primary sources, and a named lead investigator.

### 4. Bug Report
Broken links, validation errors, incorrect references, schema violations. Use the **Bug Report** issue template.

### 5. Platform Improvement
Changes to schema, scripts, documentation, or tooling. Open a standard issue first.

---

## Workflow

### Branch Strategy

| Branch | Purpose |
|---|---|
| `main` | Stable, published content only. Direct pushes blocked. |
| `investigate/<slug>` | Active investigation work |
| `fix/<description>` | Bug fixes and corrections |
| `feat/<description>` | Platform feature work |
| `docs/<description>` | Documentation changes |

All changes come in via Pull Request. PRs that touch investigation data require at least one review from a listed reviewer. PRs that touch schema require two reviews.

### PR Requirements

- [ ] All schema validation passes (`python scripts/validate.py`)
- [ ] No orphaned evidence (every piece of evidence is linked to a claim)
- [ ] All sources have provenance documented
- [ ] All new IDs follow `boe:<type>:<ulid>` format
- [ ] No existing entities have been silently edited (use revisions)
- [ ] PR description explains what was changed and why

### Commit Style

Use conventional commits:

```
feat: add covid-origins investigation scaffold
fix: correct broken source reference in claim boe:claim:...
docs: update METHODOLOGY.md confidence framework
schema: add optional context_integrity field to assessment
```

---

## Conflicts of Interest

Before submitting evidence or assessments related to an investigation, you must disclose any conflicts of interest. See [ETHICS.md](ETHICS.md) for the full policy. Undisclosed conflicts of interest are grounds for reverting a contribution.

---

## What Will Not Be Merged

- Claims that are not falsifiable
- Evidence without documented provenance
- Assessments without a confidence rationale
- Edits that silently change historical conclusions
- Contributions from accounts with undisclosed conflicts of interest
- Content that does not meet the [STYLE_GUIDE.md](STYLE_GUIDE.md)
- New investigations without an identified lead investigator

---

## Setting Up Locally

```bash
# Clone the repository
git clone https://github.com/your-org/body-of-evidence
cd body-of-evidence

# Install validation dependencies
pip install -r scripts/requirements.txt

# Run validation
python scripts/validate.py

# Validate a specific investigation
python scripts/validate.py --investigation <slug>
```

---

## Questions

Open a [Discussion](https://github.com/your-org/body-of-evidence/discussions) rather than an issue if you have a question about methodology, scope, or process. Issues are for actionable work items.
