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
**Status:** Accepted

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
**Status:** Accepted

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
**Status:** Accepted

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
**Status:** Accepted

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
