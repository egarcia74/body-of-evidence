# Changelog

All notable changes to Body of Evidence are documented here.

This project adheres to [Semantic Versioning](VERSIONING.md). Dates are ISO 8601.

---

## [Unreleased]

### Changed — response to sixth-pass review (2026-08-05, D-020)

- `id_index` is now a multimap (stable id -> list of owning files/packages), not a lossy single-owner map; a reference resolvable within the referencing entity's own package is preferred over a same-id entry in another package, fixing a false-positive `REF_WRONG_PACKAGE` the D-019 test fixture itself was producing
- Reference checking is now driven by a declarative `REFERENCE_FIELDS`/`NESTED_REFERENCE_FIELDS` registry instead of a hand-maintained dispatch; five previously-unchecked schema fields (`event`/`person`/`organisation`/`relationship.investigation_ids`, `review.specific_concerns[].referenced_entity_id`) are now validated, plus a sixth (`investigation.related_investigations`) found by the new completeness test that scans every schema for reference-shaped fields and asserts the registry matches exactly
- Symlinked entity files (and a symlinked `package.yaml` itself) are now rejected everywhere, not only symlinked package roots or manifest-listed paths — closes the gap where an unmanifested historical-version symlink could read content from outside the package, or crash validation if broken
- `load_yaml` now catches filesystem errors (e.g. a dangling symlink) as a diagnostic instead of an uncaught exception
- `validate.py --root` now validates the path exists, isn't a symlink, and is a directory before use, instead of crashing
- 44 tests (was 32)

### Changed — response to fifth-pass review (2026-08-05, D-019)

- Package-scoping now applies to EVERY cross-entity reference (claim→investigation, evidence→source, assessment→claim, etc.), not only Revision endpoints; a reference crossing a package boundary is rejected (`REF_WRONG_PACKAGE`) by default until an explicit dependency-declaration mechanism exists
- A symlinked investigation package ROOT (not just a symlinked entity path inside one) is now rejected before any file discovery, everywhere — `boe_files.find_entity_files`/`find_manifest` refuse to descend into one, `references` reports the precise cause
- `LICENSE` replaced with the byte-for-byte official Apache-2.0 text (the previous "fix" only removed an appended block; the surrounding text itself was a paraphrase, which is why GitHub kept reporting `NOASSERTION`)
- `Diagnostic` gained a `location` field; invalid-fixture tests now assert an exact, duplicate-preserving list of `(validator, code, path, location)`, not a deduplicating set — closes the gap where a fixture with two intended defects could pass after fixing only one
- `validate.py --root` added so the actual CLI multi-package discovery path can be tested against a throwaway directory; new subprocess-level integration tests cover a valid package, a cross-package reference, and a symlinked sibling package
- CODEOWNERS and CITATION.cff comments corrected to describe actual repository state
- Dependabot vulnerability alerts enabled
- 32 tests (was 25)

### Changed — response to fourth-pass review (2026-08-05, D-018)

- All validators now emit structured diagnostics (`code`, `validator`, `path`, `message`) instead of free-form strings; fixture tests assert the exact `(validator, code)` set per invalid fixture across all checks, not a substring in one named check (the tracked manifest-symlink-escape fixture's previously-unnoticed second diagnostic is now declared explicitly)
- Revision transition validation is now package-scoped: an endpoint version file owned by a different package than the Revision itself is rejected (new `REVISION_ENDPOINT_WRONG_PACKAGE` diagnostic), proven by a dedicated two-package fixture pair validated together
- Manifest path containment now rejects a symlink anywhere between the package root and the entity file, not just the final path component, matching the documented no-symlink policy
- 25 tests (was 23)

### Changed — response to third-pass review (2026-08-05, D-017)

- Revision transition validation: endpoints must belong to the revised entity and match its type; superseded versions cannot remain current (rich version index replaces the lossy one — the reviewer's unrelated-endpoints probe now fails as intended)
- Manifests must list exactly one Investigation entity matching investigation_id (the omission probe now fails as intended)
- Manifest containment is resolved, not lexical: symlinked entity paths rejected, resolved targets must stay under the package root
- Three new isolated invalid fixtures (revision-unrelated-endpoints, manifest-no-investigation, manifest-symlink-escape); fixture tests assert exact intended errors, not just failing-validator membership; 23 tests
- Green hygiene baseline: trailing whitespace stripped repo-wide, deliberate documented lint policies (.markdownlint.jsonc, .yamllint) verified green locally, CI uses repo configs plus a whitespace check
- Metadata drift reconciled: SECURITY support statement, CITATION.cff version/authors note, VERSIONING schema-preservation claim softened to planned, ROADMAP resequenced (D-016 editions before first investigations)

### Changed — response to second-pass review (2026-08-05, D-015)

- FIXED the release-blocking versioning contradiction: repeated stable ids across version files now validate (that IS the model); version_ids globally unique; (id, version_id) pairs unique; one current version per id enforced on the manifest
- Manifests now mandatory; path containment, existence, id/version match, entry uniqueness, slug and investigation_id consistency all enforced
- Revision old/new version_ids + revision_type required; endpoints must exist and differ
- Assessment dispute_status, link_ids, methodology_version required; confidence label/level pairing enforced by schema on Assessment and Finding
- Tier D/E source flags demoted from errors to advisories
- Replaced the false SHA-256 example (empty-string digest) with verifiable digests of documented synthetic bytes
- Valid fixture now contains a superseded entity version + connecting Revision, proving the versioning workflow validates; new invalid fixtures: duplicate-version-id, missing-manifest (old duplicate-id fixture removed — it enshrined the wrong invariant)
- Evidence submission and PR templates aligned with the v0.2 model (polarity on links, digests, version workflow); confidential-material prohibition made normative in CONTRIBUTING, ETHICS, and templates
- All schemas declare version 0.2.0 (one coherent bundle)
- Accepted direction for immutable edition manifests recorded as D-016 (design ADR required before implementation)

### Changed — response to independent architecture review (2026-08-05)

Schema version 0.2.0. Breaking changes; no migration needed (no investigation data existed). Full reasoning in DECISIONS.md D-009 through D-014; the review itself is preserved in docs/reviews/.

- Identity/version split: every entity now carries a stable `id` plus an immutable per-version `version_id`; supersession moved to package manifests; `superseded` and `revised` lifecycle statuses removed
- New `ClaimEvidenceLink` entity: claim-evidence connections and polarity moved off Evidence; dual backlink arrays removed from Claim and Evidence
- Assessment split into three dimensions: `conclusion`, `confidence_level` (relabelled: speculative/weak/moderate/strong/near_certain), `dispute_status`; `claim_status` removed from Claim
- Source entities gain `artifacts` with SHA-256 fixity and per-artifact rights metadata; tier A/B sources require digests
- New `package.yaml` manifest per investigation (schema/package.schema.json)
- Validator overhaul: fails on vacuous runs; `--self-test` proves valid fixtures pass and invalid fixtures fail; .yml bypass closed; duplicate YAML keys rejected; all schema errors reported; local $ref registry; real ULID validation (charset + timestamp constraint); reference type-checking; manifest consistency checks
- New fixtures/: one valid fictional package, five invalid packages (one invariant violated each)
- Tests rewritten around fixtures and run in CI; dependencies pinned
- README reclassified as pre-alpha; ARCHITECTURE.md now separates implemented from planned validation; licence scope narrowed to original work only
- Fixed: three v0.1 example IDs contained characters invalid in Crockford Base32 (caught by the new ULID validation); broken relative link in investigation template; ulid-py/python-ulid API mismatch in template comments

### Removed

- `scripts/init-repo.command` (bootstrap workaround; deleted git locks and rewrote git identity — unsafe as a distributed utility)

---

## [0.1.0] — 2026-08-04

### Added

- Complete repository scaffold for Body of Evidence platform
- Root documentation: README, VISION, ARCHITECTURE, METHODOLOGY, GOVERNANCE, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, VERSIONING, STYLE_GUIDE, TERMINOLOGY, DISCLAIMER, ETHICS, AI_GUIDELINES, PEER_REVIEW, REPRODUCIBILITY, DECISIONS
- JSON Schema definitions for all 13 entity types: Investigation, Claim, Evidence, Source, Person, Organisation, Event, Timeline, Assessment, Relationship, Revision, Review, Finding
- Shared common schema (`schema/common.schema.json`) defining reusable definitions
- YAML examples for each entity type in `examples/`
- Investigation `_template/` directory for bootstrapping new investigations
- Validation script stubs: `validate.py`, `validate_schema.py`, `validate_ids.py`, `validate_references.py`, `validate_orphans.py`, `validate_provenance.py`
- GitHub Actions workflow stubs: `validate-schema.yml`, `lint.yml`
- GitHub issue templates: bug report, evidence submission, claim challenge, new investigation proposal
- GitHub PR template
- CODEOWNERS file
- Apache 2.0 license
- CITATION.cff for academic citation
- `.gitignore`
- `docs/history/founding-prompt.md` — the founding specification

### Architecture Decisions

- YAML as canonical source of truth (D-001)
- ULID-based entity IDs with `boe:<type>:<ulid>` format (D-002)
- 5-level confidence scale (D-003)
- Immutable published entities with revision history (D-004)
- Apache 2.0 license (D-005)
- Self-contained investigation directory packages (D-006)
- MCP support as design constraint, not v0.1 deliverable (D-007)
- Python for validation scripts (D-008)

---

[Unreleased]: https://github.com/egarcia74/body-of-evidence/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/egarcia74/body-of-evidence/releases/tag/v0.1.0
