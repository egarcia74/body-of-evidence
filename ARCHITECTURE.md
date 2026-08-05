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

### Identity: stable IDs and immutable versions

Every entity has two identifiers:

- **`id`** — `boe:<type>:<ulid>` — the stable identity of the entity, constant across versions. Example: `boe:claim:01HV8QKJZ9XTMK3P2R7N5W6D4F`
- **`version_id`** — a bare ULID — the immutable identifier of one specific version of that entity.

A published entity version's file is **never modified** — not its content and not its status. To change an entity, create a new file with the same `id`, a new `version_id`, and updated content. Which version is *current* is recorded in exactly one place: the investigation's **package manifest** (`package.yaml`). Supersession is a property of the manifest, never a mutation of an old file. Consumers (renderers, MCP servers, AI agents) must resolve current state from the manifest — never from filenames, statuses, or Git timestamps.

ULIDs are used (not UUIDs) because they are lexicographically sortable by creation time, making logs and audit trails naturally ordered.

### Entity Types

| Entity | Purpose |
|---|---|
| `Investigation` | A bounded inquiry with stated scope, methodology, and lifecycle state |
| `Claim` | A single falsifiable assertion made within an investigation |
| `Evidence` | A specific extraction from a source. Carries **no polarity** and no claim references |
| `ClaimEvidenceLink` | The **only** place claim–evidence connections live. Carries polarity (supports/contradicts/contextualises/corroborates/impeaches), strength, and reasoning — because the same evidence can support one claim and contradict another |
| `Source` | A primary or secondary source document, with provenance and byte-level fixity (`artifacts` with SHA-256 digests) |
| `Person` | Identity and disambiguation data for an individual. Contestable assertions about a person are Claims, never profile attributes |
| `Organisation` | An entity (government body, company, institution) relevant to an investigation |
| `Event` | A dated occurrence. Characterisation of events belongs in Claims |
| `Timeline` | A curatorial ordering of events (expected to become fully derived) |
| `Assessment` | Evaluation of a claim recording three separate dimensions: conclusion, confidence, dispute status |
| `Relationship` | A typed connection between entities; contestable relationships must reference a backing Claim |
| `Revision` | A change activity connecting an old entity version to a new one |
| `Review` | A peer review of an investigation or specific claim |
| `Finding` | A synthesis of assessed claims. Cannot introduce facts absent from its claims |
| `Package Manifest` | Per-investigation `package.yaml`: the single source of truth for which entity versions are current, plus schema/methodology versions and dependencies |

All schemas are defined in `schema/`. Examples of each entity are in `examples/`.

**Reference direction rule:** references are stored in one direction only (link → claim, link → evidence, assessment → claim). Backlinks ("all evidence for claim X") are derived by tooling. Storing both directions caused divergence risk and was removed in schema v0.2.

---

## Directory Structure

```
body-of-evidence/
├── investigations/              # Per-investigation data packages
│   ├── _template/               # Copy this to start a new investigation
│   │   ├── README.md
│   │   ├── package.yaml         # Manifest: which entity versions are current
│   │   ├── investigation.yaml
│   │   ├── claims/
│   │   ├── evidence/
│   │   ├── links/               # ClaimEvidenceLink entities
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
│   ├── common.schema.json        # Shared definitions (ids, versions, confidence, etc.)
│   ├── package.schema.json       # Package manifest
│   ├── investigation.schema.json
│   ├── claim.schema.json
│   ├── claim_evidence_link.schema.json
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
├── fixtures/                    # Validator proof fixtures
│   ├── valid/                   # Complete packages that must pass every check
│   └── invalid/                 # Packages that must each be rejected
│
├── scripts/                     # Validation and utility scripts
│   ├── validate.py              # Master runner (fails on vacuous runs; --self-test)
│   ├── boe_files.py             # Shared file discovery (.yaml + .yml, strict YAML)
│   ├── validate_schema.py       # JSON Schema validation
│   ├── validate_ids.py          # ULID validity, duplicate IDs and version_ids
│   ├── validate_references.py   # Reference + manifest integrity
│   ├── validate_orphans.py      # Evidence not referenced by any link
│   ├── validate_provenance.py   # Provenance and artifact fixity
│   └── requirements.txt         # Pinned dependencies
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

Each entity version carries a lifecycle status:

```
Draft → Review → Published → Archived
```

| State | Meaning |
|---|---|
| `draft` | Work in progress, not ready for review |
| `review` | Submitted for peer review |
| `published` | Approved and publicly visible |
| `archived` | Closed, no further updates expected |

There is deliberately **no `superseded` status**. Supersession is a fact about the package manifest (an old `version_id` stops being listed as current), never an edit to the old file. Marking an old version "superseded" in place would itself be a mutation of the historical record — the exact thing this platform exists to prevent.

**Historical conclusions are never silently rewritten.** Any change to a published entity creates a new version plus a `Revision` entity documenting what changed, when, who made the change, and why, and updates the manifest.

---

## Assessment Framework

Every `Assessment` records three independent dimensions — see [METHODOLOGY.md](METHODOLOGY.md) for the full framework:

- **Conclusion** — `supported` / `contradicted` / `mixed` / `insufficient` / `not_assessed`
- **Confidence** — ordinal 1–5: `speculative`, `weak`, `moderate`, `strong`, `near_certain`
- **Dispute status** — `undisputed` / `disputed` / `unresolved`

Evidence on both sides of a claim is `conclusion: mixed`, not a confidence level. An active challenge is `dispute_status: disputed`, not a confidence level. The scale is ordinal, not probabilistic.

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

These tools are not implemented, and the claim that they will require no schema changes is unprovable until real investigations exist — expect schema iteration in v0.2 before any MCP work begins. A durable implementation will additionally need: release-aware queries (results pinned to a package release and exact entity versions), pagination with deterministic ordering, provenance-chain traversal down to artifact digests, and a derived index (likely SQLite + FTS) rather than filesystem YAML parsing at query time. Retrieved source text must be treated as untrusted data by consuming agents (prompt-injection surface).

The MCP stub lives in `src/mcp/`. Implementation will begin in v0.3 after the data model is validated against real investigations.

---

## Validation Architecture

The validation pipeline currently checks:

1. **Schema validity** — every entity validates against its JSON Schema (all errors reported, local `$ref` registry, no network resolution)
2. **ID integrity** — repeated stable ids across version files are valid (that is the versioning model); version_ids are globally unique, (id, version_id) pairs are unique, IDs are genuinely valid ULIDs (charset and timestamp constraints), and the ID type prefix matches the entity type
3. **Reference and manifest integrity** — every referenced ID resolves to an existing entity of the expected type; manifests are mandatory, path-contained (no absolute or `..` paths), internally unique, list exactly one current version per entity, match the files they reference, and agree with the package slug and Investigation entity; Revision endpoints reference existing, distinct version files. Schema-level `if/then` rules enforce confidence label/level pairing.
4. **Orphan detection** — every evidence entity is referenced by at least one ClaimEvidenceLink
5. **Provenance and fixity** — sources have provenance; tier A/B sources have authentication notes and at least one SHA-256 artifact digest
6. **YAML strictness** — duplicate keys are rejected; `.yaml` and `.yml` are treated identically

**Non-vacuous by construction:** `validate.py` fails if there is nothing to validate, and `validate.py --self-test` proves the validators work by requiring that `fixtures/valid/` passes every check and every `fixtures/invalid/*` package is rejected. CI runs the self-test, the unit tests, and investigation validation on every PR.

Not yet implemented (see [ROADMAP.md](ROADMAP.md)): dead-link checking, calendar-valid date checking, cross-package dependency resolution, finding-confidence-ceiling enforcement, deterministic canonical JSON output. These are listed here so the documentation does not claim more than the code does.

Local validation: `python scripts/validate.py --self-test` then `python scripts/validate.py`

---

## Design Decisions

Key architectural decisions are documented in [DECISIONS.md](DECISIONS.md) and in `docs/adr/`. When in doubt about why something is structured the way it is, check there first.
