# Decisions

This document records key architectural and editorial decisions made during the development of Body of Evidence. Each decision includes the context, the options considered, and the rationale for the choice made.

For more detailed Architecture Decision Records, see `docs/adr/`.

---

## Decision Log

### D-001: Structured YAML as canonical source of truth

**Date:** 2026-08-04
**Status:** Accepted

**Context:** The platform needs a representation format for evidence data that is human-readable, version-controllable, diff-friendly, AI-parseable, and free from vendor lock-in.

**Options considered:**
- JSON — machine-readable but poor human readability for prose fields; noisy diffs
- YAML — human-readable, diff-friendly, supports multi-line text naturally; widely supported
- TOML — human-readable but weaker tooling ecosystem for validation
- SQLite — queryable but not diff-friendly and requires tooling to read
- Markdown with frontmatter — familiar but insufficient structure for complex entity relationships

**Decision:** YAML for canonical data. JSON Schema for validation (schemas are not human-authored so readability matters less). Markdown as a generated presentation layer only.

**Rationale:** YAML diffs are readable by contributors. YAML supports rich prose fields without escaping. The validation layer (JSON Schema) is independent of the storage format.

---

### D-002: ULID-based entity IDs with typed namespace

**Date:** 2026-08-04
**Status:** Modified by D-009 (2026-08-05) — stable `id` retained, immutable `version_id` added per version

**Context:** Every entity needs a stable, globally unique identifier. IDs must be immutable once assigned and should convey entity type.

**Options considered:**
- UUID v4 — universally supported but random, no time ordering, no type information
- UUID v7 — time-ordered but still no type information
- ULID — time-ordered, lexicographically sortable, 26-character string
- Sequential integers — simple but conflict-prone in distributed contribution model
- Hash-based IDs — deterministic but complex to generate correctly

**Decision:** `boe:<type>:<ulid>` format. Example: `boe:claim:01HV8QKJZ9XTMK3P2R7N5W6D4F`

**Rationale:** The type prefix makes IDs self-describing — a reader can identify the entity type from the ID alone. ULIDs sort chronologically, making audit logs naturally ordered. The `boe:` prefix namespaces the IDs and makes them globally distinct from other ID schemes.

---

### D-003: 5-level confidence scale

**Date:** 2026-08-04
**Status:** Superseded by D-010 (2026-08-05) — conflated confidence with dispute state

**Context:** Evidence quality varies. Assessments need to communicate how well-supported a claim is, in a way that is meaningful to both human readers and AI agents.

**Options considered:**
- Binary (supported / not supported) — too coarse; loses critical nuance
- 3-level (strong / moderate / weak) — better but still loses too much nuance
- 5-level (1–5 with labels) — sufficient granularity; maps well to natural language
- 10-level — too granular; false precision; contributors will disagree about 6 vs 7
- Percentage — implies precision that doesn't exist in evidence assessment

**Decision:** 5-level scale: `speculative` (1), `contested` (2), `plausible` (3), `probable` (4), `confirmed` (5).

**Rationale:** Five levels provide meaningful distinction (a 5 and a 3 are substantively different assessments) without false precision. The named labels communicate meaning without requiring knowledge of the numeric scale. The scale aligns with common intuition about evidence strength.

---

### D-004: Immutable published entities / revision-based history

**Date:** 2026-08-04
**Status:** Modified by D-009 (2026-08-05) — the original mechanism mutated old entities' status, contradicting its own principle

**Context:** Investigations evolve as new evidence emerges. But silent rewrites undermine trust. The platform needs to support updates while preserving history.

**Options considered:**
- In-place edits with Git history as the record — relies on contributors never squashing commits; not robust
- Versioned entity files (v1, v2, etc.) — verbose; complex to query
- Explicit `Revision` entity model — revisions are first-class entities; old states are preserved in place

**Decision:** Published entities are preserved. Changes create new entities and `Revision` records linking old and new. Superseded entities are marked `superseded` not deleted.

**Rationale:** Git history is an implementation detail; the data model should encode its own history. `Revision` entities make the change record queryable and visible without archaeological git archaeology. Preserving superseded content is essential: what was believed, and when, is part of the investigative record.

---

### D-005: Apache 2.0 license

**Date:** 2026-08-04
**Status:** Narrowed by D-013 (2026-08-05) — Apache 2.0 covers code/schemas/original docs only, not third-party source material

**Context:** The platform should be open-source and usable by others who want to build on it or run their own instances.

**Options considered:**
- MIT — permissive; no patent grant
- Apache 2.0 — permissive; includes explicit patent grant
- GPL v3 — copyleft; ensures derivatives remain open but may deter institutional use
- CC-BY — appropriate for content but not code
- Creative Commons for content, Apache for code — dual-licensing complexity

**Decision:** Apache 2.0 for all repository contents.

**Rationale:** Apache 2.0 is permissive (commercial use, modification, redistribution all permitted), includes a patent grant, is widely understood by organisations, and imposes minimal burden on users (attribution only). Copyleft would deter institutional adoption. Dual-licensing for content vs. code adds unnecessary complexity at this stage.

---

### D-006: Investigations as self-contained directory packages

**Date:** 2026-08-04
**Status:** Accepted

**Context:** The repository will contain multiple investigations. They need to be navigable, independently cloneable, and extensible without changing the platform.

**Options considered:**
- Flat file structure with investigation prefix — unnavigable at scale
- One repository per investigation — fragmented; complex cross-investigation linking
- Subdirectory per investigation, all entity types in typed subdirectories — current approach

**Decision:** Each investigation is a directory under `investigations/<slug>/` with typed subdirectories for each entity type (`claims/`, `evidence/`, `sources/`, etc.).

**Rationale:** Self-contained investigation directories are portable, diff-friendly, and independently navigable. The typed subdirectory structure mirrors the entity model. The `_template/` directory makes starting a new investigation trivial — copy the template and populate.

---

### D-007: MCP support as a design constraint, not a v0.1 deliverable

**Date:** 2026-08-04
**Status:** Accepted

**Context:** The platform's stated architecture includes MCP querying. But implementing an MCP server before the data model is validated against real investigations risks building tooling around the wrong schema.

**Decision:** Design the data model to support MCP from the start. Document the intended MCP tool surface. Implement in v0.3 after v0.2 validates the schema against real investigations.

**Rationale:** The schema is the foundation. Building MCP on top of a schema that later needs breaking changes would require MCP rework. Better to stabilise the schema first.

---

### D-008: Validation scripts in Python

**Date:** 2026-08-04
**Status:** Accepted

**Context:** Validation scripts need to be accessible to contributors.

**Options considered:**
- Python — widely known; excellent JSON/YAML library ecosystem
- JavaScript/Node — common in web tooling but less familiar to data/research contributors
- Shell scripts — portable but fragile for structured data parsing
- Go — fast but higher barrier to contribution

**Decision:** Python 3.9+.

**Rationale:** Python is the most accessible language for researchers, data analysts, and investigators who may contribute. `jsonschema`, `pyyaml`, and `ulid-py` are well-maintained. The lower contribution barrier outweighs any performance advantage of other options.

---

## Decisions from the 2026-08-05 Independent Architecture Review

An independent principal-architect review of commit `f758968` (preserved at `docs/reviews/`) identified material defects in the v0.1 data model. The following decisions respond to it. The guiding principle for what to fix now versus later: **schema semantics are nearly free to change before the first real dataset exists and brutally expensive after.** Infrastructure and governance operationalisation have no such closing window and are deferred.

### D-009: Stable entity IDs + immutable version IDs + manifest-based supersession

**Date:** 2026-08-05
**Status:** Accepted (modifies D-002, D-004)

**Context:** v0.1 used one ID per entity and instructed contributors to mark old entities `superseded` — a mutation of the historical record, directly contradicting the platform's own immutability principle. The review called this the model's central incoherence.

**Decision:** Every entity carries a stable `id` (`boe:<type>:<ulid>`, constant across versions) and an immutable `version_id` (ULID, unique per version). Published version files are never modified in any way. Which version is current is recorded solely in the investigation's package manifest (`package.yaml`, D-012). The `superseded` lifecycle status is removed — supersession is the absence of a version from the manifest. `Revision` entities connect `old_version_id` to `new_version_id` and record why.

**Rationale:** Immutability that depends on contributors not editing files is policy; immutability where the current-state pointer lives outside the files is architecture. This also gives consumers (renderers, MCP, agents) a single authoritative answer to "what is current" that does not depend on filenames or Git timestamps.

### D-010: Assessment = conclusion + confidence + dispute status (separate dimensions)

**Date:** 2026-08-05
**Status:** Accepted (supersedes D-003)

**Context:** The v0.1 scale used `contested` as level 2 — but "evidence on both sides" is not a *quantity* of confidence, it is a *direction* of evidence. And an active challenge is neither.

**Decision:** Assessments record `conclusion` (supported/contradicted/mixed/insufficient/not_assessed), `confidence_level` 1–5 (`speculative`, `weak`, `moderate`, `strong`, `near_certain`), and `dispute_status` (undisputed/disputed/unresolved) as independent fields. The scale is documented as ordinal, not probabilistic. `claim_status` was removed from Claim (derived from the current assessment, not stored).

**Rationale:** The review proposed a five-dimension model (adding completeness and per-source quality dimensions); we adopted three, keeping completeness and quality inside the existing `confidence_factors` structure. Full decomposition can be revisited after pilot investigations show whether contributors can use it consistently. Overweighting assessment structure before real usage data exists is its own failure mode.

### D-011: Polarity lives on ClaimEvidenceLink; references are single-direction

**Date:** 2026-08-05
**Status:** Accepted

**Context:** v0.1 stored `evidence_type: supporting` on Evidence — semantically wrong, since the same extraction can support claim A and contradict claim B. v0.1 also stored claim→evidence and evidence→claim arrays in both directions, a guaranteed divergence bug.

**Decision:** A new `ClaimEvidenceLink` entity is the only place claim–evidence connections exist. It carries `polarity` (supports/contradicts/contextualises/corroborates/impeaches), `strength`, and `reasoning`. Evidence carries no claim references and no polarity. Claims carry no evidence references. Backlinks are derived by tooling. Orphan detection now means "evidence referenced by no link."

**Rationale:** Edges with properties belong on edge entities. One direction of storage means one source of truth.

### D-012: Package manifests per investigation

**Date:** 2026-08-05
**Status:** Accepted (extends D-006)

**Context:** "Self-contained investigation packages" was an aspiration without a contract. Nothing declared which entity versions were current, what schema version a package conformed to, or what it depended on.

**Decision:** Every investigation carries a `package.yaml` (validated against `schema/package.schema.json`) declaring: investigation ID, package release version (independent SemVer), schema version, methodology version, the current `version_id` for every entity, cross-package dependencies, and maintainers. Validators check manifest entries against the files they reference.

**Rationale:** This is the minimum manifest that makes supersession (D-009) mechanical, release-aware queries possible, and future independently-hosted packages feasible. Release digests and signatures are deferred to the signed-release milestone — they harden the mechanism but do not change its shape.

### D-013: Source fixity via artifact digests; licence scope narrowed

**Date:** 2026-08-05
**Status:** Accepted (narrows D-005)

**Context:** A URL locates a source but does not identify its content; URLs rot and contents change silently. And Apache 2.0 cannot grant redistribution rights over third-party documents.

**Decision:** Source entities gain an `artifacts` array: SHA-256 digest, byte length, media type, retrieval time/URL, storage location, and per-artifact `rights` metadata. Provenance validation requires tier A/B sources to carry at least one digest. The repository licence is documented as covering original software, schemas, and documentation only; a full SPDX/REUSE per-artifact policy is a pre-1.0 requirement. Large artifacts are stored outside Git history (storage location recorded, bytes preserved in archives).

**Rationale:** The digest is what makes "the source said X" checkable years later. The full SourceWork/SourceArtifact/EvidenceFragment three-entity split recommended by the review is deferred — the artifacts array captures the fixity guarantee without a third entity layer; structured selectors (W3C Annotation style) are noted in the Evidence schema as a planned evolution.

### D-014: Validation must be non-vacuous and self-proving

**Date:** 2026-08-05
**Status:** Accepted

**Context:** The v0.1 validator exited green with zero investigations. For a platform whose pitch is "trust our validation," a green badge that proves nothing is worse than no badge — it is false assurance. This was the review's most serious engineering finding.

**Decision:** `validate.py` fails when nothing was validated (explicit `--allow-empty` required, used in CI only alongside the self-test during pre-content pre-alpha). `fixtures/valid/` contains a complete fictional package that must pass every check; `fixtures/invalid/` contains packages each violating exactly one invariant that must be rejected. `validate.py --self-test` and the pytest suite enforce both directions in CI. Additional fixes from the same review: `.yml` files can no longer bypass semantic checks (shared file discovery), duplicate YAML keys are rejected, all schema errors are reported (not just the first), `$refs` resolve from a local registry, ULID validation enforces charset and timestamp constraints (which immediately caught three invalid IDs in our own v0.1 examples), reference validation checks endpoint types, and dependencies are pinned.

**Rationale:** A validator's claims should be tested the same way the platform tests evidence: against cases designed to falsify them.

### Deferred review recommendations (tracked, not lost)

Deliberately not done now, in rough priority order for later milestones: deterministic canonical JSON release representation (RFC 8785) with YAML demoted to authoring format; signed release manifests and two-person release rules; SQLite/FTS derived query index for MCP; structured evidence selectors; SourceWork/SourceArtifact/EvidenceFragment split; publication editions; cross-package identity resolution; governance quorum/appeals/succession (requires real humans, not schema); operational security contact; CITATION.cff completion; GitHub Actions SHA-pinning; private evidence vault for confidential sources (until it exists, confidential material is prohibited in this repository). See ROADMAP.md.
