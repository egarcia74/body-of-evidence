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

---

## Decisions from the 2026-08-05 Second-Pass Review

The second independent review (preserved at `docs/reviews/`, reviewed commit `0728c6f`) scored the remediation 3.5→4.8 and identified one release-blocking contradiction plus enforcement gaps. Response below.

### D-015: Repair of the D-009 implementation — repeated stable ids are valid

**Date:** 2026-08-05
**Status:** Accepted (repairs D-009's implementation; amends D-012, D-014)

**Context:** The reviewer found that D-009's versioning model could not pass D-014's validator: the model requires old and new versions to share a stable `id`, while the duplicate-ID check rejected every repeated `id`. Worse, the `duplicate-id` fixture *enshrined the wrong invariant* — the self-test proved the model could not work. The lesson recorded here deliberately: a self-consistent validation suite is not the same as a correct one; fixtures must be derived from the architectural invariants, not from the validator's current behaviour.

**Decision:**

- Repeated stable `id`s across entity files are valid — that is the versioning model working. All versions of an id must have the same entity type (guaranteed by the type prefix embedded in the id).
- `version_id`s are globally unique; `(id, version_id)` pairs are unique.
- Exactly one current version per stable id, enforced on the manifest (duplicate manifest ids rejected).
- Manifests are now mandatory: a package without `package.yaml` has no defined current state and fails validation.
- Manifest hardening: path containment (no absolute paths, no `..` — schema pattern + semantic check), listed files must exist and match their declared id/version_id, unique version_ids and paths among entries, slug must match the package directory, `investigation_id` must match the listed Investigation entity.
- Revision `old_version_id`/`new_version_id`/`revision_type` are now required by schema; both endpoints must correspond to existing version files and must differ.
- Confidence label/level pairing is enforced by schema (`if/then` on Assessment and Finding). Assessment `dispute_status`, `link_ids` (min 1), and `methodology_version` are required.
- Tier D/E source flags are now advisories, not errors — a disputed source is a legitimate, explicitly uncertain part of the record, not invalid data.
- The valid fixture contains a superseded claim version (same id, different version_id, absent from the manifest) plus the Revision connecting the versions, so the D-009 workflow is continuously proven to validate. New invalid fixtures: `duplicate-version-id`, `missing-manifest`. The false SHA-256 example (empty-string digest presented as a PDF's) was replaced with a verifiable digest of documented synthetic bytes in both examples and fixtures.
- Contributor surfaces were aligned with the model: evidence submission template now collects per-claim links with polarity (not polarity-on-evidence), PR template checks the v0.2 invariants, and the confidential-material prohibition is normative in CONTRIBUTING.md, ETHICS.md, and the templates.

**Rationale:** All of these are enforcement corrections to decisions already made — none change the model's shape. They were done immediately because every one becomes a data migration the day a real investigation lands.

### D-016 (direction, not yet designed): Immutable edition manifests

**Date:** 2026-08-05
**Status:** Accepted as direction; design ADR required before implementation

The reviewer's remaining critical findings (C-02, C-03) are correct: a mutable `package.yaml` as sole release authority means historical releases require Git archaeology to reconstruct, and references that target stable ids (not versions) can be silently re-pointed by manifest changes. The accepted direction is immutable, content-addressed Edition manifests (RFC 8785 canonical JSON, edition id + parent, exact version ids + digests, dependency edition identities), with `package.yaml` demoted to a mutable working head that compiles into editions at release time. Assessments, reviews, and revisions will pin exact versions or resolve within a declared edition. This is deliberately NOT patched here: it must be designed together with the deterministic-JSON release format (D-001 revision) and signing, as one coherent ADR, before the first real investigation. Doing it piecemeal now would create the third identity model in two days.

**Also explicitly deferred from the second review:** structured evidence selectors and evidence→artifact-digest pinning (H-04, needs the edition design), controlled relationship predicate registry (M-05), YAML resource limits (M-02), calendar-valid date checking (M-01), schema `$id` domain (placeholder until an org/domain exists — Eddie's call), Actions SHA-pinning and hash-locked deps (M-03), DCO/CLA and governance operationalisation (H-08..H-10 — require humans), semantic checks for claim-link ownership and confidence ceilings (H-03 remainder), and the deterministic build test (M-08).

---

## Decisions from the 2026-08-05 Third-Pass Review

The third review (docs/reviews/, reviewed commit `5873299`) scored 4.8→5.8, confirmed C-01 resolved via independent runtime verification, and demonstrated two semantic bypasses with direct probes.

### D-017: Semantic transition validation and hygiene baseline

**Date:** 2026-08-05
**Status:** Accepted (extends D-015; addresses third-pass immediate items)

**Context:** The reviewer probed the validators directly and found: (1) a Revision whose old/new version_ids belonged to *unrelated entities* was accepted — the version index was lossy (version_id→path), so endpoint identity could not be checked; (2) a manifest omitting its own Investigation entity was accepted; (3) manifest path containment was lexical only and could be bypassed by a tracked symlink. Additionally the declared lint gate was red and the D-015 commit itself introduced trailing whitespace.

**Decision:**

- The version index is now rich (`version_id → {path, id, type}`). Revision transition validation enforces: both endpoints exist, differ, belong to `Revision.entity_id`, and match `Revision.entity_type`; and the OLD version must not be listed as current in the package manifest. The NEW version is deliberately not required to be current, so revision chains (v1→v2→v3) keep intermediate revisions valid.
- Every manifest must list exactly one Investigation entity, whose id equals the manifest's `investigation_id`.
- Manifest containment is now resolved, not just lexical: symlinked entity paths are rejected outright, and resolved targets must remain under the package root.
- Three isolated invalid fixtures prove the new checks (`revision-unrelated-endpoints`, `manifest-no-investigation`, `manifest-symlink-escape` — the latter contains a real tracked symlink). Fixture tests now assert the *exact intended error*, not merely that the intended validator appears among failures (D-014 extension).
- Hygiene baseline: trailing whitespace stripped repo-wide; deliberate, documented lint policies in `.markdownlint.jsonc` and `.yamllint` (integrity rules enforced; style-war rules disabled on purpose); both linters verified green locally; CI workflows use the repo configs and gained a whitespace check.
- Metadata drift reconciled: SECURITY support statement matches reality (no formal support pre-1.0), CITATION.cff carries the current version and an honest placeholder note, VERSIONING no longer promises an unimplemented schema-preservation mechanism, ROADMAP reflects the review-driven history and sequences D-016 before first investigations.

**Rationale:** Both probe findings were the same failure class: existence checks standing in for identity checks. The fix is to validate what the record *means* (this revision connects versions of this entity; this package is about this investigation), not just that its references resolve. On lint: the reviewer is right that a permanently red gate is worse than none — the chosen policy is narrow, documented, and actually green, which is worth more than an aspirational strict one that everyone learns to ignore.

**Still open after this decision (tracked in ROADMAP/D-016):** C-02/C-03 (editions + version-pinned references — top of queue), H-04 (evidence→artifact anchoring), H-03 remainder (assessment graph semantics), H-07 (Event/Relationship bypass), governance/rights/privacy (require humans), Actions SHA-pinning and hash-locked deps, YAML resource limits, calendar dates.

---

## Decisions from the 2026-08-05 Fourth-Pass Review

The fourth review (docs/reviews/, reviewed commit `44d9d98`) scored 5.8→6.2, confirmed the third-pass probes now correctly rejected, and found that D-017's "exact intended error" claim was itself not enforced by the tests — plus a new cross-package Revision defect and a symlink-policy/implementation gap.

### D-018: Package-scoped revisions, structured diagnostics, and full symlink-path enforcement

**Date:** 2026-08-05
**Status:** Accepted (extends D-017; addresses fourth-pass immediate code items)

**Context:** The reviewer found: (1) H-02b — Revision transition validation checked entity identity and type but not package ownership; a Revision in one package could claim a transition using a version file that actually lives in a different package, because the version index was rich (`{path, id, type}`) but not package-aware; (2) M-07/M-10 — `test_invalid_fixture_rejected` asserted only that ONE expected substring appeared in ONE named check's errors, so a fixture producing an unintended EXTRA diagnostic (or the wrong validator entirely, coincidentally containing the substring) would still pass; the tracked `manifest-symlink-escape` fixture demonstrated this by emitting a second, cascading `MANIFEST_NO_INVESTIGATION` error that the test never noticed; (3) M-11 — SECURITY documentation and D-017 claimed "symlinked entity paths are rejected outright," but the implementation only checked whether the final path component was a symlink, not any parent directory between the package root and the file.

**Decision:**

- **Structured diagnostics.** All five validators now return `boe_files.Diagnostic` objects (`code`, `validator`, `path`, `message`) instead of free-form strings. Every distinct failure has a stable `code` (e.g. `REVISION_ENTITY_MISMATCH`, `MANIFEST_PATH_SYMLINK`, `ORPHAN_EVIDENCE`). `Diagnostic.__str__` returns `message`, so existing human-facing printing is unchanged.
- **Exact diagnostic-set fixture assertions.** `test_invalid_fixture_rejected` now runs ALL checks against each `fixtures/invalid/*` package and asserts the produced `(validator, code)` set equals an explicitly declared set — not substring membership in one named check. `manifest-symlink-escape`'s two diagnostics (`MANIFEST_PATH_SYMLINK` and the derived `MANIFEST_NO_INVESTIGATION`) are both declared, honestly, rather than one being silently tolerated.
- **Package-scoped revision endpoints (H-02b).** The version index built in `run_reference_validation` now also carries which package root (from the passed-in `investigation_paths`) owns each version file. `validate_revision_transition` rejects a Revision whose old/new endpoint belongs to a different package than the Revision itself (`REVISION_ENDPOINT_WRONG_PACKAGE`). Proven by `fixtures/cross_package/{pkg-a,pkg-b}` — two independent packages that deliberately share a stable claim id, validated together (a scenario the single-package `fixtures/invalid/*` self-test loop structurally cannot exercise, hence a dedicated pytest test rather than another self-test fixture).
- **Full-path symlink enforcement (M-11).** `_resolved_containment_error` now walks every path component from the package root down to the entity file and rejects if ANY of them is a symlink, not just the final file. Resolved-containment (target must resolve inside the package root) remains as defence-in-depth. This makes the implementation match what SECURITY/D-017 already claimed.

**Rationale:** All three findings were the same failure class as D-017's: a check proving *something* rather than the *specific thing* claimed. Package identity, exact diagnostic sets, and full-path symlink rejection are all "this specific record means what it claims" checks, consistent with D-017's rationale. Structured diagnostics are also a prerequisite named directly by the review for future editor/AI/MCP consumption (H-04, D-016) — free-form strings cannot be depended on by anything other than a human reading logs.

**Deliberately not done here (see ROADMAP/D-016 and the fourth-pass review's remaining backlog):** the public-repository operational items (CODEOWNERS, branch protection, security reporting channel, placeholder URLs, Apache-2.0 license detection, Discussions) — those are GitHub configuration and human decisions, not code; C-02/C-03 immutable editions and version-pinned references (still the central blocker); H-04 evidence→artifact anchoring; H-03/H-07 assessment and relationship graph semantics; Actions SHA-pinning; YAML resource limits; a packaged validator CLI with a stable diagnostic-JSON contract (a natural next step now that diagnostics are structured, but not required to close this review's code findings).
