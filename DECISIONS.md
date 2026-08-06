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

---

## Decisions from the 2026-08-05 Fifth-Pass Review

The fifth review (docs/reviews/, reviewed commit `ce21593`) scored 6.2→6.4 and, treating D-018's remediation claims as propositions to falsify, found that three were only partially true and one — Apache-2.0 licensing — had failed outright despite being reported fixed.

### D-019: General package-scoped references, symlinked package roots, canonical licence text, and diagnostic multiplicity

**Date:** 2026-08-05
**Status:** Accepted (extends D-018; addresses fifth-pass immediate items)

**Context:** The reviewer found: (1) H-02c — D-018 package-scoped Revision endpoints specifically, via the version index, but the separate stable-ID index used by every ORDINARY reference (claim→investigation, evidence→source, assessment→claim, etc.) remained repository-global; a direct probe showed a Claim in one package resolving an `investigation_id` belonging to a different package with no error; (2) H-15 — the symlink-path fixes in D-017/D-018 covered symlinked *entity* paths inside a manifest, but never checked whether the *package root itself* was a symlink; package discovery's `p.is_dir()` is true for a symlink to a directory, so a symlinked investigation root was silently traversed and validated as if it were a real, contained package; (3) H-16 — my LICENSE fix in the previous round only removed the appended copyright block; the surrounding text itself was a paraphrase of Apache-2.0, not the canonical text (differences in sections covering the Work/Contribution definitions, redistribution conditions, and the disclaimer/liability sections), so GitHub's license detector correctly kept reporting `NOASSERTION`; (4) M-07b — D-018's "exact diagnostic set" fix compared a Python `set` of `(validator, code)`, which collapses duplicate diagnostics (two dangling references in one file look identical to one) and discards which field or entry each occurrence is about — a fixture could pass after fixing only one of two intended defects.

**Decision:**

- **General reference package-scoping (H-02c).** The stable-ID index built in `run_reference_validation` now carries package identity, the same way the version index already did for D-018. Every `check_ref`/`check_ref_list` call — covering all reference types listed in the module docstring, not only Revision endpoints — compares the referencing entity's package against the target's package and raises `REF_WRONG_PACKAGE` on a mismatch. Proven by extending the existing `fixtures/cross_package/pkg-a` fixture with an ordinary Claim whose `investigation_id` points at package B.
- **Symlinked package roots (H-15).** `boe_files.find_entity_files` and `find_manifest` now refuse to descend into an investigation root that is itself a symlink — every validator is protected centrally, not just `references`. `run_reference_validation` additionally reports the precise root cause (`INVESTIGATION_ROOT_SYMLINK`) rather than letting the symlinked package fail silently or for a misleading reason. Proven by a new tracked-symlink fixture, `fixtures/invalid/investigation-root-symlink`, pointing at the otherwise-valid `harbour-tender-inquiry` package — proof that rejection is about the symlink, not broken content.
- **Canonical Apache-2.0 text (H-16).** `LICENSE` is now byte-for-byte identical to `https://www.apache.org/licenses/LICENSE-2.0.txt`, appendix included, unfilled placeholder brackets included (the same convention GitHub's own license-template generator uses). Project attribution remains in `NOTICE`.
- **Diagnostic multiplicity and location (M-07b).** `Diagnostic` gained a `location` field (the field name or JSON pointer segment a diagnostic is about; empty for whole-file or whole-package diagnostics). `test_invalid_fixture_rejected` now asserts an exact, duplicate-preserving, sorted LIST of `(validator, code, path, location)` tuples per fixture, not a deduplicating set — a fixture with two dangling references now requires both to be fixed, and a Revision with both endpoints wrong is distinguishable from one with a single wrong endpoint.
- **Production discovery integration test (M-15).** Added `--root` to `validate.py` so the actual CLI discovery path (`argv` → `investigations_dir.iterdir()`) can be exercised against a throwaway directory in tests, not just the hand-built `investigation_paths` lists the unit tests were already using. Three subprocess-level tests cover: a valid package accepted, a cross-package reference rejected, and a symlinked sibling package rejected — all via the real CLI entry point.
- **Comment accuracy (M-16, L-05).** CODEOWNERS no longer claims a "two reviewers" requirement that branch protection does not enforce; CITATION.cff's placeholder comment no longer describes the live repository URL as a placeholder.
- **Stale type hints (L-06).** `validate_ids.py`, `validate_orphans.py`, `validate_provenance.py`, and `validate_schema.py` return type hints now say `List[Diagnostic]`, matching what they have actually returned since D-018.
- **Dependency visibility (M-17).** Dependabot vulnerability alerts enabled via the GitHub API (dependency graph is automatic for public repositories). Automated dependency-update PRs deliberately NOT enabled yet — that needs a review policy first, per the reviewer's own phrasing.

**Rationale:** Every one of H-02c, H-15, and M-07b is the SAME failure class D-017 and D-018 already named: a check or test proving something narrower than what it was claimed to prove (Revision endpoints scoped but not general references; entity-path symlinks caught but not the package root itself; a code SET asserted as "exact" when it silently drops multiplicity). H-16 is different in kind — an honest mistake, not a narrower-than-claimed check — but the fix follows the same principle: verify the actual GitHub-facing outcome (the license API response), not just that the file "looks trimmed."

**Still open after this decision (tracked in ROADMAP/D-016):** C-02/C-03 (editions + version-pinned references), H-04 (evidence→artifact anchoring), H-03/H-07 (assessment/relationship graph semantics), H-08/H-09/H-10 (governance, rights, privacy), Actions SHA-pinning, YAML resource limits, a packaged validator CLI with a stable diagnostic-JSON contract, Dependabot automated updates (needs a review policy decision first), schema `$id` namespace and CITATION.cff authors (need Eddie's decisions, not code).

---

## Decisions from the 2026-08-05 Sixth-Pass Review

The sixth review (docs/reviews/, reviewed commit `d6209f1`) scored 6.4→6.6, verified H-16/M-07b/M-15/M-16/L-05/L-06/M-17 in full, and found D-019's two broadest claims — "every reference is package-scoped" and "symlinks are rejected everywhere" — were each true only for the cases the fifth-pass review had specifically probed, not in general.

### D-020: Multimap identity resolution, a declarative reference registry, and unconditional entity-symlink rejection

**Date:** 2026-08-05
**Status:** Accepted (extends D-019; addresses sixth-pass immediate items)

**Context:** The reviewer found: (1) H-17 — the stable-ID index (`id_index[id] = {path, package}`) could record only ONE owner per id, so when the same stable id legitimately appeared in two packages (exactly what the D-019 test fixture does on purpose), the later-indexed package silently won; a reference resolvable LOCALLY within the referencing entity's own package was misreported as cross-package because the index had already forgotten the local entry — a false positive in the fixture that was supposed to prove the fix. (2) H-18 — the hand-maintained if/elif dispatch in `validate_references_in_file` never covered `event`/`person`/`organisation`/`relationship.investigation_ids` or `review.specific_concerns[].referenced_entity_id`; dangling or cross-package values in those fields produced zero diagnostics, so "every reference is package-scoped" was false for whichever fields the dispatch happened to omit. (3) H-19 — D-019's symlink fixes covered a symlinked package ROOT and symlinked paths LISTED in a manifest, but not an ordinary entity file that is a symlink and simply isn't listed — which describes every historical/superseded version file by design (D-009); such a file could read content from outside the package and pass every check, and a DANGLING one crashed validation outright with an uncaught `FileNotFoundError`. (4) M-18 — a nonexistent `--root` reached `iterdir()` unguarded and crashed with a traceback instead of a diagnostic.

**Decision:**

- **Multimap identity resolution (H-17).** `id_index` now maps each stable id to a LIST of `{path, package}` entries, not one. `check_ref` prefers an entry owned by the referencing entity's own package when one exists, and only reports `REF_WRONG_PACKAGE` when no same-package entry exists at all. `version_index` was NOT changed the same way — version_ids are globally unique by invariant #8, so a single-entry map is correct there.
- **Declarative reference registry (H-18).** `validate_references.py` now exposes `REFERENCE_FIELDS` (a dict of entity_type → `[(field, is_list, want_type), ...]`) and `NESTED_REFERENCE_FIELDS` (for array-of-object fields like `review.specific_concerns[].referenced_entity_id`) as the single source of truth for what gets checked. `validate_references_in_file` is now driven by the registry instead of a hand-written dispatch. A new completeness test (`TestReferenceRegistryCompleteness`) recursively scans every schema for boe-ID-pattern-constrained properties and asserts the registry covers exactly that set — in both directions, so schema evolution that adds OR removes a reference field is caught by a test rather than silently validating nothing (or carrying dead registry entries). This same scan additionally found `investigation.related_investigations`, a sixth reference field the sixth-pass review itself did not catch.
- **Unconditional entity-symlink rejection (H-19).** `boe_files.find_entity_files` now excludes any individual file that is a symlink, in addition to the existing symlinked-root exclusion — regardless of whether it's manifest-listed. `find_manifest` likewise refuses a `package.yaml` that is itself a symlink. `boe_files.find_symlinked_entity_paths` surfaces what was excluded so `run_reference_validation` can report it explicitly (`ENTITY_FILE_SYMLINK`) rather than the package silently appearing to have fewer files. `load_yaml` also now catches `OSError` (not just `yaml.YAMLError`), turning a dangling-symlink read failure into a diagnostic-friendly error string as a defensive backstop for any other call site.
- **`--root` input validation (M-18).** `validate.py` now checks `--root` exists, is not a symlink, and is a directory before calling `iterdir()`, printing a diagnostic and exiting 1 instead of raising.
- **CI hygiene fix.** The new `broken-unmanifested-symlink` fixture — a real tracked symlink whose target does not exist, needed to prove H-19's crash fix — made `yamllint` itself crash (not just error) when it tried to open the dangling symlink. Added to `.yamllint`'s `ignore` list; the validators, not the YAML linter, are what's supposed to examine that file.

**Rationale:** All three High findings are the same failure class named in D-017/D-018/D-019: a check or claim that was true for the specific case tested, not for the general case claimed. The registry-plus-completeness-test pattern (H-18) is a structural fix to that recurring problem, not just a patch — it makes "we forgot a field" a test failure instead of a silent gap, and it already found one field none of the six review passes had caught. Multimap identity resolution (H-17) exists because self-contained packages (D-006) and undeclared cross-package id collisions are currently indistinguishable to a lossy index; representing multiplicity honestly is the minimum fix until D-016/dependency declarations give the model an actual way to express "these two packages both know about this entity, and that's fine."

**Still open after this decision:** C-02/C-03, H-03/H-04/H-07, H-08–H-10, Actions SHA-pinning, hash-locked dependencies, a stable diagnostic-JSON CLI contract, YAML resource limits, calendar-valid dates, schema `$id` namespace and CITATION.cff authors (Eddie's decisions). The registry now also names a design gap D-016 will need to resolve: whether a globally unique stable id may be owned by exactly one package, or whether deliberate multi-package mirroring/import is a real use case — D-020's multimap fix makes both cases behave sanely today, but does not decide between them.

---

## Decisions from the 2026-08-05 Seventh-Pass Review

The seventh review (docs/reviews/, reviewed commit `cc6294e`) scored 6.6→6.8, verified all four sixth-pass claims for the EXACT probes demonstrated, and found each was still narrower than its general statement: the reference registry didn't cover every schema field's *semantic scope* (only the ones checked existed at all — the fields themselves were fine, but resolution ignored manifest state), the nested registry was descriptive rather than executable, and the symlink/root-error handling covered the specific inputs probed rather than the general case.

### D-021: Manifest-current reference resolution, an executable nested registry, whole-package symlink rejection, and CLI enumeration errors

**Date:** 2026-08-05
**Status:** Accepted (extends D-020; addresses seventh-pass immediate items)

**Context:** The reviewer found: (1) H-20 — the highest-severity finding of the round — reference resolution checked that a stable id existed as a file, owned by the right package, but never checked whether that id was the package manifest's CURRENT version of anything. A probe removed a Claim's manifest entry while leaving its file and all references to it (a ClaimEvidenceLink, an Assessment, a Revision) in place; every check still passed, meaning the released graph could depend on entities the release manifest does not actually contain — undermining the manifest's role as release authority, the same concern C-03 names at the Edition level but independently fixable now. (2) M-19 — `NESTED_REFERENCE_FIELDS` was introduced in D-020 as if it drove validation, but runtime validation still ran a hardcoded `review.specific_concerns` loop with no actual connection to the registry; a future nested field could be added to a schema AND the registry, pass the completeness test, and still never be checked at runtime. (3) M-20 — D-020's symlink scan only walked `*.yaml`/`*.yml` files; a symlinked SUBDIRECTORY, or a symlink to a non-YAML file, was invisible to it. In this repo's Python/pathlib version `rglob` does not currently follow a symlinked directory (so nothing inside one is actually read), but the symlink itself went completely undetected — a policy violation independent of whether today's traversal happens to be safe. (4) M-21 — `--root` gained existence/type/symlink checks in D-020 (M-18), but enumeration itself (`iterdir()`) could still raise `PermissionError` on an unreadable directory, producing a traceback.

**Decision:**

- **Manifest-current reference resolution (H-20).** `run_reference_validation` now parses every package's manifest — building each package's current-entity map — BEFORE ordinary reference validation runs, not after. `check_ref` gained a `current_maps` parameter: once a reference resolves to the correct package, it must ALSO be a key in that package's current map, or `REF_NOT_CURRENT` is raised. This applies uniformly to every stable-id (id_index-based) reference; version-pinned checks (Revision `old_version_id`/`new_version_id` via `version_index`) are deliberately unaffected — they already have their own, more precise, historical-vs-current logic (D-018), which this reuses rather than duplicates.
- **Executable nested registry (M-19).** `NESTED_REFERENCE_FIELDS` changed shape from bare path strings to `(array_field, item_field, want_type)` tuples that `validate_references_in_file` traverses generically at runtime — the hardcoded `specific_concerns` loop is gone. A new `nested_field_schema_paths()` helper renders the tuples back into the `array[].item` string shape the completeness test needs, so the executable and descriptive representations can't drift from each other by construction. A new behavioural test (`test_every_registered_field_actually_validates_when_dangling`) constructs a synthetic dangling reference for every registry entry, flat and nested, and asserts each one actually produces `REF_NOT_FOUND` — completeness (the field is *listed*) is no longer conflated with correctness (the field is *checked*).
- **Whole-package symlink rejection (M-20).** `boe_files.find_all_symlinks` replaces the YAML-only scan, walking every package with `os.walk(followlinks=False)` — deliberately not relying on pathlib glob's symlink-traversal behaviour, which differs across versions — so it detects (without ever descending into) a symlinked directory, and detects a symlinked file of any extension. The diagnostic code changed from `ENTITY_FILE_SYMLINK` to `PACKAGE_SYMLINK` to match the broadened scope.
- **CLI enumeration errors (M-21).** `validate.py`'s investigation-path enumeration (`--investigation` existence check and the default `iterdir()` listing) is now wrapped in `try/except OSError`, printing a diagnostic and exiting 1 instead of propagating a `PermissionError` traceback.

**Rationale:** H-20 is the clearest instance yet of the pattern named in D-017 through D-020: a check that was true for the property tested (id exists, in the right package) but false for the property actually claimed (the release contains this entity). It is also the first finding this round that is directly about the manifest's authority — which is exactly what D-016's Edition work will need to get right at a stronger level (exact version bindings, not just current-vs-not); fixing it now, at the current stable-id-resolution layer, is compatible with and a prerequisite for that later work, not a competing design. M-19's fix is structural for the same reason M-19 itself was found: a registry that is merely *descriptive* re-creates exactly the hand-maintained-dispatch problem H-18 was meant to eliminate, just one level removed — the fix generalizes execution over the registry AND adds a test that would fail if a future entry were added without wiring it in.

**Still open after this decision:** C-02/C-03 (D-016 remains the complete answer — exact version/Edition bindings, not "current" as a boolean), H-03/H-04/H-07, H-08–H-10, Actions SHA-pinning, hash-locked dependencies, a stable diagnostic-JSON CLI contract, YAML resource limits, calendar-valid dates, schema `$id` namespace, CITATION.cff authors.

---

## D-022: PR-required branch protection, CodeRabbit, SonarQube Cloud, and Dependabot version updates

**Date:** 2026-08-06
**Status:** Accepted

**Context:** All prior review-response ADRs (D-017 through D-021) were fixes to gaps an external "Codex" architecture-review pass found AFTER a round of changes had already been committed and, in most cases, already pushed to `origin/main`. There was no gate between a local commit and the public remote other than the maintainer's own judgement and (as of the previous session) a self-imposed habit of running `/code-review` locally before pushing. `main`'s branch protection required four CI status checks but neither required a pull request nor enforced protection on the repository owner (`enforce_admins: false`), so a direct push to `main` remained possible at any time. No automated code-quality scanning (as opposed to the repo's own domain-specific validators) existed, and Dependabot was configured only for vulnerability alerts (D-018/M-17), not version-update PRs — so dependency drift was invisible until a CVE made it an alert.

**Decision:**

- **PR-required branch protection.** `main`'s branch protection now sets `required_pull_request_reviews` (`required_approving_review_count: 0`, so a solo maintainer can still self-merge without waiting on another human) and `enforce_admins: true`. The owner is not exempt: every change, including the maintainer's own, must go through a PR. The four existing required status checks (Lint YAML, Lint Markdown, Whitespace hygiene, Validation suite) are unchanged; force-push and branch deletion remain blocked.
- **CodeRabbit as an automatic PR reviewer.** The CodeRabbit GitHub App is authorized on all of the maintainer's repositories (a decision made outside this repo, in CodeRabbit's own settings) and now has access to this one. Combined with PR-required protection, every change gets an automatic CodeRabbit review in addition to the local `/code-review` pass already established as a pre-push habit — the local pass catches issues before a PR exists at all; the PR-triggered one is a second, independent pass that also covers Dependabot-authored PRs the maintainer didn't write by hand.
- **SonarQube Cloud, informational-first.** A new workflow (`.github/workflows/sonarcloud.yml`) and `sonar-project.properties` run a SonarQube Cloud scan (`SonarSource/sonarqube-scan-action`) on every push to `main` and every same-repository, non-Dependabot PR, scoped to `scripts/` and `tests/` and excluding `fixtures/` (deliberately-invalid/example content by design — see fixtures README notes elsewhere in this file) and `examples/`. The quality gate is deliberately NOT enforced yet (the scan reports to the Cloud dashboard without failing CI; the separate `sonarqube-quality-gate-action` is unsupported for SonarQube Cloud, so gating — when promoted — will use `sonar.qualitygate.wait=true` in `sonar-project.properties`): this is the first scan the codebase has ever had, so there is no known-clean baseline to gate on. The plan is to promote the gate to required once a scan establishes that baseline — recorded here so a future session doesn't mistake "not required yet" for "forgotten."
- **Dependabot version updates.** `.github/dependabot.yml` adds weekly version-update PRs for the `pip` ecosystem (`scripts/requirements.txt`) and the `github-actions` ecosystem (workflow action versions), on top of the vulnerability alerts already enabled (D-018/M-17). These PRs now flow through CodeRabbit and the lint/validate checks instead of being invisible until Dependabot separately flags a CVE. The Sonar scan does NOT run on them: GitHub withholds repository Actions secrets from Dependabot-triggered `pull_request` runs the same way it withholds them from fork PRs (`sonarcloud.yml`'s job condition excludes `github.actor == 'dependabot[bot]'` for exactly this reason, rather than letting the scan step fail on a missing `SONAR_TOKEN`) — using `pull_request_target` to work around that was considered and rejected, since it would run untrusted PR code with secret access.

**Rationale:** Every review-response ADR to date has been reactive — found by an external pass after the fact. This decision adds gates that run before a change reaches `origin/main` at all, closing (for ordinary changes; it does not replace independent architecture review) the same class of gap the "fixed the specific case, not the general claim" pattern (documented in `CLAUDE.md`'s Current State section) has repeatedly exposed after the fact. `enforce_admins: true` specifically exists because a PR requirement that exempts the only committer is not a requirement — it was a deliberate strengthening beyond what the maintainer initially proposed. SonarQube is informational-first rather than required because turning on an unknown, potentially large, initial finding set as a hard gate risks either blocking all future work until fully triaged, or training the maintainer to routinely override a red gate — both worse than a temporarily advisory one.

**Still open after this decision:** Promote the SonarQube quality gate to a required check once a baseline scan is clean. Actions SHA-pinning (unchanged position: deferred to first tagged release, `sonarcloud.yml` carries the same TODO as the pre-existing workflows). Whether CodeRabbit or Sonar findings should ever block Dependabot auto-merge (no auto-merge is configured; every PR, including Dependabot's, requires manual merge). C-02/C-03, H-03/H-04/H-07, H-08–H-10, hash-locked dependencies, a stable diagnostic-JSON CLI contract, YAML resource limits, calendar-valid dates, schema `$id` namespace, CITATION.cff authors.

---

## Decisions from the 2026-08-06 Eighth-Pass Review

The eighth review (docs/reviews/, reviewed commit `b712c6c`, comparison commit `975fea1`) scored 6.8→6.9, verified the seventh-pass fixes for the exact cases they addressed, and found two further High-severity integrity defects plus one Medium, all in code the seventh-pass round had just changed. CodeRabbit CLI, run independently over the same commit range, found two of the three (M-22 and H-22) but not H-21 — "useful evidence for the adopted policy: automated review broadens coverage but cannot replace independent architectural reasoning and adversarial runtime probes," per the review itself.

### D-023: Historical-reference exemption from manifest currency, dangling package-root symlink discovery, and fail-closed traversal

**Date:** 2026-08-06
**Status:** Accepted (extends D-021; addresses eighth-pass immediate items)

**Context:** The reviewer found: (1) H-21 — D-021's H-20 fix requires every reference to resolve to its target package manifest's CURRENT version, but applied that rule unconditionally, including to references made by entities that are themselves historical/superseded and legitimately unmanifested by design (D-009). An adversarial probe added a superseded, unmanifested ClaimEvidenceLink referencing a retired, unmanifested Evidence entity — the historical link was rejected with `REF_NOT_CURRENT`, meaning a historical record could be invalidated merely by the later retirement of something it once pointed at, directly opposing the project's immutability/provenance principles. (2) H-22 — `validate.py`'s default package discovery filtered candidates with `p.is_dir()`, which is `False` for a DANGLING symlink; such a symlink vanished before ever reaching the symlink-rejection logic, and — unlike a live symlinked directory, already handled — was invisible to both the reference validator and any diagnostic. Independently reproduced; CodeRabbit found this one too. (3) M-22 — `boe_files.find_all_symlinks`'s `os.walk` call had no `onerror` handler; Python's default behavior for an unreadable subdirectory is to silently omit it from results, so a package with an inaccessible subtree — which could easily be hiding a prohibited symlink — was certified as clean without having actually been fully inspected. Also independently reproduced; also found by CodeRabbit. (4) L-07/L-08 — the registry-behavioral test used membership assertions (missing an extra/duplicate diagnostic) and covered only `REF_NOT_FOUND`, not `REF_NOT_CURRENT`, across the registry; the unreadable-root test's skip condition (checking the CLI's exit code) could skip for the wrong reason in a privileged environment.

**Decision:**

- **Referencing-entity currency gate (H-21).** `validate_references_in_file` now computes, once per file, whether THAT file is itself current (`current_maps[entity_package].get(data["id"]) == data["version_id"]`) and threads a `referencing_is_current` flag through `check_ref`/`check_ref_list`. The `REF_NOT_CURRENT` check in `check_ref` is now gated on this flag; `REF_NOT_FOUND`, `REF_TYPE_MISMATCH`, and `REF_WRONG_PACKAGE` are unaffected, since those are basic integrity facts about a reference, not release-graph membership, and apply regardless of whether the referencing file is current. This is explicitly framed (in code comments and this ADR) as an INTERIM rule for the current stable-id-resolution layer — D-016's Edition work is expected to replace it with resolution against the historical immutable Edition that actually contained the referencing source version, a stronger and more precise guarantee than "was the referencing file current."
- **Symlink-inclusive discovery (H-22).** `validate.py`'s default `iterdir()` filter and its `--investigation`-path existence check both changed from `p.is_dir()` / `path.exists()` alone to `p.is_symlink() or p.is_dir()` / `path.exists() or path.is_symlink()` — a dangling symlink now reaches `run_reference_validation`'s existing `INVESTIGATION_ROOT_SYMLINK` check (which already handled both live and dangling cases correctly; the bug was purely in what reached it) instead of disappearing beforehand.
- **Fail-closed traversal (M-22).** `boe_files` gained a shared `_walk_package` helper — a single `os.walk(onerror=<collect>, followlinks=False)` walk used by both `find_entity_files` (replacing the previous `rglob`-based version, which has the identical silent-skip behavior for the same underlying reason) and `find_all_symlinks`, so both see the same tree and the same failures. A new `find_traversal_errors` surfaces every subdirectory that could not be listed. **Two follow-ups caught by automated PR review (Codex/CodeRabbit) before merge, both the same underlying gap at a different scope:** (1) the initial fix wired `find_traversal_errors` into `run_reference_validation` only, so a standalone `--check schema`/`--check ids`/`--check orphans`/`--check provenance` invocation could still certify an incompletely-inspected package on its own — every one of those validators also calls `find_entity_files`/`iter_entities`, the same silent-skip surface. A new `boe_files.traversal_error_diagnostics(paths, validator)` helper is now called at the top of all five `run_*_validation` functions. (2) The identical gap existed for a symlinked package ROOT (not just an unreadable subtree): `find_entity_files` silently skips a symlinked root by design, and only `references` had ever reported that explicitly (`INVESTIGATION_ROOT_SYMLINK`) — the other four validators just saw zero files and passed vacuously. A parallel `boe_files.symlinked_root_diagnostics(paths, validator)` closes the same gap for package roots. Two parameterized tests (`test_every_single_check_fails_closed_on_unreadable_subtree`, `test_every_single_check_fails_closed_on_symlinked_root`) prove both for all five validators independently, not just the combined `--check all` path; the pre-existing `investigation-root-symlink` fixture's expected-diagnostics list grew from 2 entries (`references` + `schema`'s incidental `SCHEMA_VACUOUS_RUN`) to 5 explicit `INVESTIGATION_ROOT_SYMLINK` diagnostics, one per validator.
- **Test rigor (L-07/L-08).** The registry-behavioral test now asserts an exact sorted diagnostic list (`==`, not `in`) for the existing `REF_NOT_FOUND` parameterization, and a new parallel test parameterizes `REF_NOT_CURRENT` across every `REFERENCE_FIELDS`/`NESTED_REFERENCE_FIELDS` entry the same way, constructing a target that exists in the right package and type but is absent from a synthetic current-map. The unreadable-root CLI test now attempts `list(unreadable.iterdir())` directly and skips only if that succeeds, invoking the CLI (and asserting on its diagnostic) only once `PermissionError` is confirmed to fire in the current environment.
- **SonarCloud disposition (out of the eighth-pass review, raised separately in the same session).** Of 19 SonarCloud findings on `main`: 7 Critical cognitive-complexity findings are deliberately deferred — the flagged functions (`validate_manifest`, `run_reference_validation`, `validate_revision_transition`, `run_id_validation`, `run_schema_validation`, `validate.py:main`) carry eight rounds of review-hardened behavior each, and `validate_references.py` specifically is what D-016's Editions work will reshape; refactoring now risks churning the same code twice. 8 Major unused-parameter findings: 4 were genuinely dead (`label` in two `validate.py` helpers, `id_index`/`version_index` on `validate_manifest`, none referenced in their function bodies) and removed; the other 4 (`schema_dir` on `run_id_validation`/`run_orphan_validation`/`run_provenance_validation`/`run_reference_validation`) are required by `run_all_checks`'s uniform `check_fn(investigation_paths=, schema_dir=, verbose=)` dispatch — removing them would break that interface for the sake of one validator not personally needing the argument — and are marked accepted in SonarCloud rather than left as recurring noise. 4 Major test/style findings (three composite-assertion splits, one nested-if merge) were fixed as straightforward, zero-risk cleanups.

**Rationale:** H-21 is the same failure class named in every round since D-017: a check that was true for the property actually tested (H-20's probe: does the target exist in the manifest) but false for the property the invariant actually requires (does invalidating a HISTORICAL record's own historical references serve any release-integrity purpose — it doesn't; it only punishes keeping history at all). It is also the first finding to surface a case D-016 needs to resolve properly rather than merely patch: today's fix is explicitly interim, gated on "was the referencing file ever current," because the repository has no concept yet of "the Edition that was current AT THE TIME this historical file was written." H-22 and M-22 share a root cause — code that reports what it looked at, without regard to whether it looked at everything it should have — which is precisely the "certify a package it did not completely inspect" failure mode the review named as the pattern connecting both. The SonarCloud disposition follows the same review discipline as the architecture-review responses: fix what's genuinely wrong, document why what's left is left, and don't silently suppress an interface constraint by calling it done.

**Still open after this decision:** D-016 remains the complete answer for H-21 (Edition-scoped historical resolution, not a current/not-current boolean substitute) as well as C-02/C-03. H-03/H-04/H-07, H-08–H-10, hash-locked dependencies, a stable diagnostic-JSON CLI contract, YAML resource limits, calendar-valid dates, schema `$id` namespace, CITATION.cff authors, and the 7 deferred SonarCloud complexity findings (to be revisited alongside, not before, D-016's `validate_references.py` reshape).

---

## Decisions from the 2026-08-06 Tenth-Pass Review

The tenth review (docs/reviews/, reviewed commit `258e257`, comparison commit `4e759f1`) scored the response to the eighth pass at 7.0 (unchanged from the ninth pass, referenced but not separately filed) — the H-21/H-22/M-22 fixes were verified as behaviorally correct for their own demonstrated cases and generalized across all five validators by the PR-review follow-ups already captured in D-023, but the review found two claims made about the SHAPE of that generalization were themselves overstated, plus one unaddressed performance/atomicity gap and one accurate-but-overlooked documentation gap.

### D-024: Centralized single-walk package discovery, closing internal-symlink and historical-registry-test coverage gaps

**Date:** 2026-08-06
**Status:** Accepted (extends D-023; addresses tenth-pass immediate items 1–4)

**Context:** The reviewer found: (1) M-27 — D-023's PR-review follow-up added `symlinked_root_diagnostics`/`traversal_error_diagnostics` to all five `run_*_validation` functions, but never gave the other four validators (`schema`, `ids`, `orphans`, `provenance`) an equivalent for ORDINARY internal symlinks — only `run_reference_validation` called `find_all_symlinks` and emitted `PACKAGE_SYMLINK`. An adversarial probe against the committed `fixtures/invalid/unmanifested-symlink` package, run one `--check` at a time, showed `schema`/`ids`/`orphans`/`provenance` all passing while only `references` failed — the same vacuous-pass failure class as H-22/M-22, at a different scope. (2) M-28 — `test_every_registered_field_enforces_currency_when_historical` (added by D-023 for L-07) was misnamed and its docstring overclaimed: its synthetic referencing entity's own id/version_id WERE present in the test's `current_maps`, meaning `referencing_is_current` was `True` throughout, so it parameterized H-20 current-source currency enforcement across all 32 registry locations, not the H-21 historical-source exemption it claimed to prove. (3) M-24 — `_walk_package` (D-023) is a shared IMPLEMENTATION, not a shared RESULT: `find_traversal_errors`, `find_entity_files`, and `find_all_symlinks` each still called it independently, meaning a single validator run performed up to three separate filesystem walks of the same package tree, with a time-of-check/time-of-use window between the safety preflight and the entity-reading pass. (4) L-11 — `CLAUDE.md` claimed `symlinked_root_diagnostics` was called by all five validators (true) via a shared traversal with `find_entity_files`/`find_all_symlinks` (not true — they called the same function, not the same walk).

**Decision:**

- **One walk per package, one immutable result (M-24, and the structural fix M-27 is built on).** `boe_files.py` gained `PackageDiscovery` (a frozen dataclass: `root`, `entity_files`, `root_is_symlink`, `internal_symlinks`, `traversal_errors`) and `discover_package`/`discover_packages`, which call `_walk_package` exactly ONCE per root and return every fact a validator needs. `preflight_diagnostics(discoveries, validator)` replaces the separate `symlinked_root_diagnostics`/`traversal_error_diagnostics` helpers, emitting `INVESTIGATION_ROOT_SYMLINK`, `PACKAGE_SYMLINK`, and `PACKAGE_SUBTREE_UNREADABLE` from the SAME discovery. `entity_files_from`/`entities_from` replace `find_entity_files`/`iter_entities` as the entity-iteration path for every `run_*_validation` function, consuming the same discovery instead of re-walking. The lower-level `find_entity_files`/`find_all_symlinks`/`find_traversal_errors` functions are retained (they are directly unit-tested as primitives) but are no longer called from any validator entry point — `_walk_package` is still their shared implementation, but no production code path calls it more than once per package per CLI invocation anymore.
- **Internal-symlink rejection under every standalone check (M-27).** Because `preflight_diagnostics` is now the ONLY diagnostic-generation path for symlink/traversal preflight, and because it includes `internal_symlinks` (which `symlinked_root_diagnostics`/`traversal_error_diagnostics` never covered), all five validators reject an ordinary internal symlink identically — this was a natural consequence of centralizing rather than a separate patch, which is the structural fix the review specifically asked for over "add PACKAGE_SYMLINK to four more validators individually." Four `TestInvalidFixtures` fixtures (`manifest-symlink-escape`, `unmanifested-symlink`, `broken-unmanifested-symlink`, `symlinked-subdirectory`) had their expected-diagnostics lists extended from references-only to all five validators, matching the pattern D-023 already established for `investigation-root-symlink`. A new parameterized test, `test_every_single_check_fails_closed_on_internal_symlink`, proves it independently of the fixtures.
- **Corrected historical-registry test coverage (M-28).** The existing test was renamed to `test_every_registered_field_enforces_currency_when_source_is_current` with a docstring explaining what it actually proves and why the old name/claim was wrong. A new test, `test_every_registered_field_exempts_historical_source_from_currency`, constructs a referencing entity whose own id/version_id are deliberately ABSENT from `current_maps` (making it historical per D-023/H-21) pointing at an existing, correctly-typed, same-package but non-current target, and asserts NO diagnostics are produced — for every flat and nested registry entry, closing the coverage gap the review demonstrated.
- **Documentation correction (L-11).** `CLAUDE.md`'s `scripts/boe_files.py` layout note was rewritten to describe the actual mechanism (`PackageDiscovery`/`discover_packages`/`preflight_diagnostics`, one walk per package) instead of the superseded D-023 description it had drifted from.

**Rationale:** M-27 and M-24 are two faces of the same root cause the review named directly: D-023's PR-review follow-up generalized ROOT-symlink and TRAVERSAL-error handling to all five validators by adding two new helper functions, but stopped short of also generalizing INTERNAL-symlink handling, and never actually merged the underlying walks — so "all five validators fail closed" was true for two of three symlink/traversal facts and false for the third, while "the consumers share one traversal" was a claim about the code's shape, not its runtime behavior. Building `PackageDiscovery` as one shared IMMUTABLE result, rather than adding a fourth helper function alongside the existing three, is the structural fix the tenth-pass review explicitly asked for over "another layer of per-validator patches" — the same critique leveled, in slightly different words, at every prior round's remediation. M-28 is a different kind of gap: not a missing runtime check, but a test whose construction silently failed to exercise the case its name and docstring claimed — a reminder that "the assertion is exact" (L-07's own fix) does not guarantee "the setup constructs the case under test."

**Still open after this decision:** M-25 (SonarCloud coverage input, Codacy disposition) is being addressed as a separately scoped tooling change, deliberately kept out of this response so architecture-review remediation and CI-tooling changes don't land in the same diff. M-26 (GitHub CodeRabbit reporting green under rate-limiting) is a process gap, not a code gap — noted for PR review practice, not fixed by this ADR. D-016 remains the complete answer for H-21's interim exemption, as well as C-02/C-03. H-03/H-04/H-07, H-08–H-10, hash-locked dependencies, a stable diagnostic-JSON CLI contract, YAML resource limits, calendar-valid dates, schema `$id` namespace, CITATION.cff authors, and the 7 deferred SonarCloud complexity findings.
