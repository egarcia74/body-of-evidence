# Architecture

## Overview

Body of Evidence is built around a single architectural principle: **structured data is the canonical source of truth.** Everything else — markdown files, web pages, API responses — is a generated view over that data.

```
┌─────────────────────────────────────────────────────────────┐
│                    Canonical Source of Truth                 │
│              Structured YAML/JSON Evidence Data              │
│           (investigations/, schema/, examples/)              │
└─────────────┬───────────────────────────────┬───────────────┘
              │                               │
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────────┐
│   Generated Markdown    │     │      MCP Server (future)     │
│   + GitHub Pages        │     │   search_claims,             │
│   → Human Readers       │     │   retrieve_evidence,         │
└─────────────────────────┘     │   timeline, compare_claims   │
                                │   → AI Agents                │
                                └─────────────────────────────┘
```

If there is ever a conflict between a rendered page and the underlying structured data, the structured data is correct.

---

## Entity Model

All entities share a common identity scheme: `boe:<type>:<ulid>`

Examples:
- `boe:investigation:01HV8QKJZ9XTMK3P2R7N5W6D4E`
- `boe:claim:01HV8QKJZ9XTMK3P2R7N5W6D4F`
- `boe:source:01HV8QKJZ9XTMK3P2R7N5W6D4G`

ULIDs are used (not UUIDs) because they are lexicographically sortable by creation time, making logs and audit trails naturally ordered.

### Entity Types

| Entity | Purpose |
|---|---|
| `Investigation` | A bounded inquiry with stated scope, methodology, and lifecycle state |
| `Claim` | A single falsifiable assertion made within an investigation |
| `Evidence` | A specific piece of evidence supporting or contradicting a claim |
| `Source` | A primary or secondary source document or artefact |
| `Person` | An individual relevant to an investigation |
| `Organisation` | An entity (government body, company, institution) relevant to an investigation |
| `Event` | A dated occurrence relevant to an investigation |
| `Timeline` | An ordered sequence of events within an investigation |
| `Assessment` | A structured evaluation of a claim's validity with confidence rating |
| `Relationship` | A typed connection between any two entities |
| `Revision` | A documented change to any entity, preserving history |
| `Review` | A peer review of an investigation or specific claim |
| `Finding` | A high-level conclusion synthesised from multiple claims and evidence |

All schemas are defined in `schema/`. Examples of each entity are in `examples/`.

---

## Directory Structure

```
body-of-evidence/
├── investigations/              # Per-investigation data packages
│   ├── _template/               # Copy this to start a new investigation
│   │   ├── README.md
│   │   ├── investigation.yaml
│   │   ├── claims/
│   │   ├── evidence/
│   │   ├── sources/
│   │   ├── people/
│   │   ├── organisations/
│   │   ├── events/
│   │   ├── timelines/
│   │   ├── assessments/
│   │   ├── findings/
│   │   └── reviews/
│   └── {slug}/                  # One directory per investigation
│
├── schema/                      # JSON Schema for all entity types
│   ├── common.schema.json        # Shared definitions (id, confidence, etc.)
│   ├── investigation.schema.json
│   ├── claim.schema.json
│   ├── evidence.schema.json
│   ├── source.schema.json
│   ├── person.schema.json
│   ├── organisation.schema.json
│   ├── event.schema.json
│   ├── timeline.schema.json
│   ├── assessment.schema.json
│   ├── relationship.schema.json
│   ├── revision.schema.json
│   ├── review.schema.json
│   └── finding.schema.json
│
├── examples/                    # Annotated YAML examples per entity
│
├── scripts/                     # Validation and utility scripts
│   ├── validate.py              # Master validation runner
│   ├── validate_schema.py       # JSON Schema validation
│   ├── validate_ids.py          # Duplicate/format ID check
│   ├── validate_references.py   # Broken reference detection
│   ├── validate_orphans.py      # Orphan evidence detection
│   ├── validate_provenance.py   # Missing provenance check
│   └── requirements.txt
│
├── docs/
│   ├── guides/                  # How-to guides
│   ├── history/                 # Founding documents
│   │   └── founding-prompt.md
│   └── adr/                     # Architecture Decision Records
│
├── templates/
│   └── investigations/          # Investigation starter templates
│
├── src/
│   └── mcp/                     # Future MCP server stub
│
├── lib/                         # Shared library code (future)
│
├── tests/                       # Test stubs
│
└── .github/
    ├── ISSUE_TEMPLATE/
    ├── PULL_REQUEST_TEMPLATE.md
    ├── CODEOWNERS
    └── workflows/
```

---

## Investigation Lifecycle

Each investigation passes through defined states. State transitions are documented in the investigation's `revision` history.

```
Draft → Review → Published → Revised → Superseded
                     ↓
                  Archived
```

| State | Meaning |
|---|---|
| `draft` | Work in progress, not ready for review |
| `review` | Submitted for peer review |
| `published` | Approved and publicly visible |
| `revised` | A published investigation with updates pending |
| `superseded` | Replaced by a newer version (old version preserved) |
| `archived` | Closed, no further updates expected |

**Historical conclusions are never silently rewritten.** Any change to a published investigation creates a `Revision` entity documenting what changed, when, who made the change, and why.

---

## Confidence Framework

Every `Assessment` carries a confidence level on a 5-point scale. See [METHODOLOGY.md](METHODOLOGY.md) for the full framework. The levels are:

| Level | Label | Meaning |
|---|---|---|
| 5 | `confirmed` | Established beyond reasonable doubt from multiple independent primary sources |
| 4 | `probable` | Strongly supported; minor gaps or single-source dependency |
| 3 | `plausible` | Supported by available evidence; alternative explanations remain viable |
| 2 | `contested` | Evidence exists on multiple sides; no clear preponderance |
| 1 | `speculative` | Limited or indirect evidence; significant uncertainty |

---

## MCP Design Intent

The structured evidence model is designed from the ground up to be queryable by AI agents via the Model Context Protocol. Future MCP tools will include:

```
search_claims(query, investigation?, confidence_min?)
search_sources(query, type?, date_range?)
search_people(query)
search_events(date_range?, query?)
retrieve_evidence(evidence_id)
compare_claims(claim_id_a, claim_id_b)
get_timeline(investigation_id)
get_relationship_graph(entity_id, depth?)
confidence_lookup(claim_id)
```

These tools are not implemented in v0.1. The data model is designed so they can be added without schema changes.

The MCP stub lives in `src/mcp/`. Implementation will begin in v0.3 after the data model is validated against real investigations.

---

## Validation Architecture

All structured data is validated before merge. The validation pipeline checks:

1. **Schema validity** — every entity validates against its JSON Schema
2. **ID integrity** — no duplicate IDs, all IDs match `boe:<type>:<ulid>` format
3. **Reference integrity** — every referenced ID resolves to an existing entity
4. **Orphan detection** — every piece of evidence is attached to at least one claim
5. **Provenance completeness** — every source has documented provenance
6. **Link health** — external URLs are resolvable (CI check)

Validation runs in GitHub Actions on every PR. Local validation: `python scripts/validate.py`

---

## Design Decisions

Key architectural decisions are documented in [DECISIONS.md](DECISIONS.md) and in `docs/adr/`. When in doubt about why something is structured the way it is, check there first.
