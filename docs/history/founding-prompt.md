# Founding Prompt

This file records the specification that created the Body of Evidence repository. It is preserved as part of the project's history.

**Date:** 2026-08-04

---

## Original Specification

You are bootstrapping a new open-source project called **Body of Evidence** (`body-of-evidence`). This is a substantial, production-quality repository scaffold — treat it as the founding moment of a significant long-term open-source project.

## Step 0 — Find the GitHub folder

Check these paths in order and use the first one that exists:
- ~/GitHub
- ~/github
- ~/Projects
- ~/Developer/GitHub
- ~/Developer

Use the Bash tool to check. If none exist, ask the user once where to put it before proceeding.

Create the repo at `<github-folder>/body-of-evidence/`.

---

## What this project is

**Body of Evidence** is an open-source, version-controlled evidence platform for publishing transparent, reproducible investigations built from primary sources. It is not a website, not a political project, not an opinion platform.

Its purpose: make complex investigations inspectable, auditable, reproducible, reviewable, and extendable.

The platform must support investigations such as:
- Anthony Fauci Diary
- COVID Origins
- Church Committee
- Pentagon Papers
- JFK Records
- Royal Commissions
- Parliamentary Inquiries
- Inspector General Reports
- Scientific controversies
- Historical investigations
- Corporate investigations
- Future independent investigations

The architecture must never need redesigning when new investigations are added.

**Do not** build around any specific investigation. **Do not** populate datasets, generate evidence, create claims, or create investigations. Only build the reusable platform. This is Version 0.1.

---

## Core Philosophy

- Evidence and interpretation must remain separate
- Every conclusion must be traceable
- Every revision must be documented
- Every assessment must explain its confidence
- Every source must have provenance
- Every investigation should be reproducible
- Every conclusion should be challengeable
- Optimise for transparency over advocacy

---

## Architecture

Structured data is the canonical source of truth. Everything else is generated from it.

```
Structured Data → Generated Markdown → GitHub Pages → Humans
Structured Data → MCP → AI Agents
```

Markdown is a presentation layer. GitHub Pages is a presentation layer. MCP is an interface. The structured evidence model is the canonical source of truth.

---

## What to create

### Root documentation files (all with meaningful, concise content — no filler):
- README.md
- VISION.md
- ARCHITECTURE.md
- ROADMAP.md
- METHODOLOGY.md
- GOVERNANCE.md
- CONTRIBUTING.md
- CODE_OF_CONDUCT.md
- SECURITY.md
- CHANGELOG.md
- VERSIONING.md
- STYLE_GUIDE.md
- TERMINOLOGY.md
- DISCLAIMER.md
- ETHICS.md
- AI_GUIDELINES.md
- PEER_REVIEW.md
- REPRODUCIBILITY.md
- DECISIONS.md
- LICENSE (Apache 2.0)
- CITATION.cff
- .gitignore

Also save the full founding prompt at: `docs/history/founding-prompt.md`

### Directory structure — design what makes sense, but at minimum scaffold:
- `investigations/` — per-investigation data (with a `_template/` directory)
- `schema/` — JSON Schema definitions for all entities
- `examples/` — YAML examples of each entity type
- `scripts/` — validation, generation, utility scripts
- `docs/` — extended documentation, guides, history
- `templates/` — GitHub issue/PR templates, investigation templates
- `.github/` — Actions, issue templates, PR template, CODEOWNERS
- `src/` or `lib/` — future MCP/API implementation stubs
- `tests/` — validation test stubs

### Canonical Data Model

Design JSON Schema for these entities. Every entity gets a stable immutable ID (suggest `boe:<type>:<ulid>` format):

- Investigation
- Claim
- Evidence
- Source
- Person
- Organisation
- Event
- Timeline
- Assessment (with Confidence)
- Relationship
- Revision
- Review
- Finding

Provide:
1. JSON Schema files in `schema/`
2. YAML examples in `examples/`

### Investigation Lifecycle

States: Draft → Review → Published → Revised → Superseded → Archived

Historical conclusions must never be silently rewritten.

### Confidence Framework

Based on: evidence strength, source quality, corroboration, completeness, alternative explanations, context integrity.

Design a 5-level confidence scale (document it in METHODOLOGY.md and schema).

### Validation foundations

Create stub scripts (Python or shell, your choice) for:
- schema validation
- duplicate identifier detection
- broken references
- orphan evidence
- missing provenance
- dead links

Just enough to establish the architecture.

### GitHub configuration

- Issue templates (bug report, evidence submission, challenge, new investigation proposal)
- PR template
- CODEOWNERS
- GitHub Actions stubs (validate-schema.yml, lint.yml)
- Branch strategy documented in CONTRIBUTING.md

### MCP readiness

Design the data model and directory structure to naturally support future MCP tools:
- search_claims, search_sources, search_people, search_events
- retrieve_evidence, compare_claims
- timeline, relationship_graph, confidence_lookup

Document the MCP design intent in ARCHITECTURE.md. Do not implement it.

---

## Engineering standards

- Simplicity over complexity
- Explicit over implicit
- Maintainability over cleverness
- Every file must be immediately understandable to a new engineer

---

## Final steps

1. `git init`
2. `git add -A`
3. `git commit -m "feat: bootstrap Body of Evidence v0.1 — founding repository scaffold"`

After the commit, do a self-review:
- Would an independent engineer immediately understand this?
- Are there any architectural weaknesses to address before declaring done?
- Is DECISIONS.md populated with the real decisions you made?
- Is everything consistent?

Fix anything material before reporting back.

Report what was created, any significant architectural decisions you made, and the git commit hash.

---

*This prompt was used to bootstrap the repository on 2026-08-04. It is preserved here as part of the project history.*
