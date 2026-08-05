---
review_title: "Independent Architecture Review: Body of Evidence — Second Pass"
reviewed_at: "2026-08-05T09:59:47+10:00"
reviewed_commit: "0728c6fc84054444df4bc54a021c3c0424f35c1a"
comparison_commit: "d4288eda92e98fc06233fd7ed5d9532e882aedb8"
review_type: "independent-principal-architect-follow-up"
review_status: "final"
verdict: "conditional-go-pre-alpha-no-go-evidence-release"
---

# Independent Architecture Review: Body of Evidence — Second Pass

## Verdict

**Substantial improvement, but still no-go for a tagged, evidence-bearing, or foundation-endorsed release.**

The repository may be published for public inspection as an explicitly labelled **pre-alpha architecture scaffold**. It is not yet ready to host real investigations or claim reproducibility and evidentiary integrity.

The remediation is directionally correct and improves estimated release readiness from approximately **3.5/10 to 4.8/10**. However, the revised architecture contains one release-blocking contradiction: the documented immutable-version workflow cannot pass the validator because old and new versions correctly share a stable entity ID, while the validator rejects every repeated stable ID.

## Review basis

This follow-up reviewed the repository at commit `0728c6fc84054444df4bc54a021c3c0424f35c1a`, comparing the changes made after the [original independent architecture review](2026-08-05T001819+1000-independent-architecture-review.md), saved at commit `d4288eda92e98fc06233fd7ed5d9532e882aedb8`.

The review covered:

- Repository and information architecture
- Entity and relationship design
- Immutable versioning and package releases
- JSON Schemas and semantic validators
- Tests and GitHub Actions
- Provenance, fixity, integrity, and security
- Governance, licensing, privacy, and contributor policy
- AI, MCP, and long-term query readiness
- Documentation and template consistency

Static verification completed:

- `git diff --check` passed.
- All 16 JSON schemas parsed.
- Eight Python files parsed.
- All 33 tracked YAML files parsed.
- Git integrity checks found no corruption; only ordinary dangling commits were reported.
- The repository worktree was clean before this review document was created.

The Python test suite and `validate.py --self-test` could not be independently run in the supplied environment because PyYAML and jsonschema were unavailable, and the environment could not retrieve dependencies from PyPI. This is not evidence that the tests fail, but their runtime result remains unconfirmed by this review.

## Executive Summary

### Material improvements

The remediation addressed several important findings from the first review:

- The README now accurately labels the repository as pre-alpha and warns readers not to rely on it for evidentiary integrity yet: [README.md](../../README.md#L8).
- Empty investigation validation now fails by default, and the validator includes a positive/negative self-test: [scripts/validate.py](../../scripts/validate.py#L7).
- CI runs pytest, the validator self-test, and investigation validation with read-only permissions and a timeout: [validate-schema.yml](../../.github/workflows/validate-schema.yml#L9).
- Claim conclusion, epistemic confidence, and dispute status are now conceptually separate: [assessment.schema.json](../../schema/assessment.schema.json#L5).
- Evidence polarity correctly moved to a first-class `ClaimEvidenceLink`: [claim_evidence_link.schema.json](../../schema/claim_evidence_link.schema.json#L5).
- Stable entity identity and immutable version identity are now explicitly distinguished: [ARCHITECTURE.md](../../ARCHITECTURE.md#L30).
- Investigation packages gained manifests: [package.schema.json](../../schema/package.schema.json#L4).
- Source artifacts gained byte digests, retrieval metadata, and rights metadata: [source.schema.json](../../schema/source.schema.json#L67).
- YAML discovery is consistent for `.yaml` and `.yml`, and duplicate mapping keys are rejected: [boe_files.py](../../scripts/boe_files.py#L18).
- Schema references resolve locally and all validation errors are reported: [validate_schema.py](../../scripts/validate_schema.py#L26).
- ULID validation is materially stronger: [validate_ids.py](../../scripts/validate_ids.py#L21).

These are meaningful architectural improvements, not cosmetic changes.

### Remaining weaknesses

The central weaknesses are now concentrated in enforcement and release semantics:

1. The stable-ID/version model cannot represent two immutable versions without failing validation.
2. A mutable `package.yaml` remains the only release authority, so historical releases are not independently reconstructable without Git history.
3. References generally do not pin exact entity versions or an immutable edition context.
4. Package manifests are optional and insufficiently validated.
5. Revision, Assessment, confidence, and provenance invariants remain mostly prose.
6. Evidence does not identify the exact artifact bytes from which it was extracted.
7. Contestable assertions can still bypass the Claim-to-Evidence-to-Assessment path.
8. Governance, ownership, security contacts, inbound licensing, privacy operations, and appeals remain non-operational.

### Major risk

The principal risk remains **false assurance**, although the README now communicates the risk more honestly.

The repository records important integrity metadata, but it does not yet prove the integrity relationships it claims. In particular, a syntactically present digest is treated as fixity, a mutable manifest is treated as a release, and prose requirements are treated as semantic validation.

## Remediation assessment

| Area | Status | Assessment |
| --- | --- | --- |
| Honest release posture | **Resolved** | The README accurately describes the repository as pre-alpha. |
| Vacuous validation | **Resolved** | Empty validation fails by default; valid and invalid fixtures exercise both directions. |
| Claim/evidence polarity | **Resolved structurally** | Polarity correctly belongs on `ClaimEvidenceLink`. |
| Confidence model | **Partially resolved** | The dimensions are sound, but required fields and semantic correlations are not enforced. |
| Stable IDs and revisions | **Blocking contradiction** | Multiple immutable versions of the same entity are rejected as duplicate IDs. |
| Package manifest | **Partially resolved** | The concept is sound; the manifest remains optional, mutable, and insufficiently validated. |
| Source provenance | **Partially resolved** | Digests are recorded but not verified, and Evidence is not pinned to exact artifact bytes. |
| YAML/schema validation | **Improved but incomplete** | Local references and all-error reporting are good; formats, dates, aliases, limits, and schema meta-validation remain incomplete. |
| Governance | **Open** | Placeholder authority, contacts, ownership, quorum, succession, and appeal rules remain. |
| Licensing and privacy | **Partially resolved** | Rights metadata exists, but there is no enforceable inbound/content/confidential-data regime. |
| AI/MCP readiness | **Improved but incomplete** | The graph model is better, but exact-version resolution and deterministic query semantics are not stable. |
| Documentation consistency | **Mixed** | Release honesty improved; contributor templates, Roadmap, Versioning, CFF, and schema metadata have drifted. |

## Architecture Scorecard

| Category | Previous | Current | Assessment |
| --- | ---: | ---: | --- |
| Repository architecture | 5/10 | **6/10** | Better package and fixture boundaries; documentation still advertises nonexistent or duplicate areas. |
| Data model | 4/10 | **6.5/10** | Strong conceptual corrections, undermined by the versioning contradiction and imprecise release references. |
| Validation | 2/10 | **5/10** | Non-vacuous and broader, but core semantic invariants remain unenforced. |
| Testing and automation | 2/10 | **4.5/10** | Meaningful fixtures and CI wiring exist; the negative matrix is incomplete and runtime was not independently confirmed. |
| Documentation | 6/10 | **5/10** | More honest, but Roadmap, Versioning, examples, templates, and schema versions conflict. |
| Governance | 3/10 | **2/10** | Critical governance files remain essentially unchanged and non-operational. |
| Maintainability | 4/10 | **5/10** | Shared file loading and clearer concepts help; semantic rules remain scattered between prose and code. |
| Extensibility | 5/10 | **6/10** | Better edge and package concepts; cross-package identity remains incomplete. |
| AI readiness | 4/10 | **5/10** | Structured data remains appropriate; deterministic canonical releases are still absent. |
| MCP readiness | 3/10 | **4/10** | Query intent is clearer, but release-aware indexes and controlled predicates are not implemented. |
| Security and integrity | 2/10 | **4.5/10** | Better CI and fixity metadata; manifests, artifacts, signatures, privacy, and supply chain remain weak. |
| Open-source readiness | 2/10 | **4/10** | Honest pre-alpha posture; ownership, inbound rights, contacts, and release authority remain placeholders. |
| **Overall** | **3.5/10** | **4.8/10** | Suitable for public architecture review, not for evidence publication. |

## Release-blocking findings

### Critical: the immutable-version workflow cannot work

The architecture requires an updated entity to retain the same stable `id`, receive a new `version_id`, and leave the old file untouched: [ARCHITECTURE.md](../../ARCHITECTURE.md#L30).

The validator rejects any repeated stable entity ID across all recursively discovered entity files: [validate_ids.py](../../scripts/validate_ids.py#L88). The duplicate-ID fixture explicitly treats the same stable ID with two different version IDs as invalid: [claim-a.yaml](../../fixtures/invalid/duplicate-id/claim-a.yaml#L1), [claim-b.yaml](../../fixtures/invalid/duplicate-id/claim-b.yaml#L1).

The repository therefore cannot contain both the old and new immutable versions required by D-009.

Required correction:

- Permit repeated stable `id` values.
- Require globally unique `version_id` values.
- Require every version sharing a stable ID to have the same entity type.
- Permit exactly one current version per stable ID in an immutable edition manifest.
- Validate Revision endpoints against exact version IDs.

### Critical: releases are not independently reproducible

`package.yaml` is the authority for current versions, but it is a mutable singleton. Reconstructing a previous package composition therefore still requires Git archaeology, which D-004 and D-009 intended to avoid.

References also generally target stable IDs rather than exact versions:

- Claim/evidence links contain `claim_id` and `evidence_id` only: [claim_evidence_link.schema.json](../../schema/claim_evidence_link.schema.json#L21).
- Evidence contains only `source_id`: [evidence.schema.json](../../schema/evidence.schema.json#L21).
- Reviews contain only `subject_id`: [review.schema.json](../../schema/review.schema.json#L21).

A later manifest can therefore change the claim, evidence, source, or assessment version underlying an unchanged link or review.

The repository needs immutable, content-addressed Edition manifests. Every query, generated publication, assessment, and review should resolve within an edition. Revision and Review endpoints, and preferably evidence-link endpoints, should explicitly pin exact versions.

### High: package manifest validation has material bypasses

A missing manifest is accepted by schema and reference validation: [validate_schema.py](../../scripts/validate_schema.py#L95), [validate_references.py](../../scripts/validate_references.py#L126).

Manifest paths are unrestricted strings: [package.schema.json](../../schema/package.schema.json#L50). They are joined without containment or entity-extension checks: [validate_references.py](../../scripts/validate_references.py#L139). This permits absolute paths, `../` traversal, and non-entity files.

Validation also does not ensure:

- Every entity file is represented in the manifest.
- There is exactly one current manifest entry per stable entity ID.
- Paths and version IDs are unique.
- The package slug matches its directory.
- `investigation_id` matches the package's Investigation entity.
- Cross-package references are covered by declared dependencies.
- Dependencies have an immutable identity, URI, or digest.

The validator constructs a version index but does not use it for manifest membership or Revision validation: [validate_references.py](../../scripts/validate_references.py#L167).

### High: Revision and Assessment invariants remain largely prose

`old_version_id`, `new_version_id`, and `revision_type` are optional even though a Revision is defined as connecting versions: [revision.schema.json](../../schema/revision.schema.json#L8).

Assessment improvements are conceptually sound, but:

- `dispute_status`, `link_ids`, confidence factors, methodology version, and status are optional: [assessment.schema.json](../../schema/assessment.schema.json#L8).
- Numeric confidence and confidence labels can disagree: [common.schema.json](../../schema/common.schema.json#L29).
- Link IDs are not checked to ensure they belong to the assessed claim.
- An assessment can omit known contradictory links.
- Source-quality, corroboration, and completeness ceilings are not enforced.
- Quality-tier D/E "warnings" are appended to the error list, making disputed sources invalid rather than explicitly uncertain: [validate_provenance.py](../../scripts/validate_provenance.py#L51).

These relationships require a semantic graph validator in addition to JSON Schema.

### High: exact evidence provenance remains ambiguous

Source artifacts now have digests, which is a useful improvement. Evidence still does not identify:

- The exact Source `version_id`.
- An artifact ID or SHA-256 digest.
- A structured selector into that artifact.

The Source example uses the SHA-256 digest of the empty byte string while claiming a 24,837,201-byte PDF and saying the digest matches an archive: [examples/source.yaml](../../examples/source.yaml#L23). This is a false-integrity example and should not remain in a repository teaching provenance.

The provenance validator merely checks that a digest string exists; it never hashes available bytes or validates a signature: [validate_provenance.py](../../scripts/validate_provenance.py#L37).

### High: contestable facts can bypass Claims and Assessments

`Event`, `Relationship`, `Person`, and `Finding` can carry substantive assertions directly. Relationships retain free-text predicates, direct source references, and confidence outside the Claim/Assessment path: [relationship.schema.json](../../schema/relationship.schema.json#L41).

The platform should either:

- Restrict these entities to identity and indexing metadata, deriving contestable descriptions from assessed claims; or
- Require every contestable field to cite exact claim versions.

Otherwise generated publications can contain assertions that did not pass through the evidence-assessment process.

### High: schema identity and compatibility are inconsistent

All schema `$id` values still use the placeholder `https://github.com/your-org/...`, for example [common.schema.json](../../schema/common.schema.json#L3). Thirteen of sixteen schemas still declare version `0.1.0`, while package manifests and the changelog describe schema `0.2.0`.

Additional gaps include:

- `schema_version` and `methodology_version` accept arbitrary strings: [package.schema.json](../../schema/package.schema.json#L28).
- `isoDate` accepts impossible dates such as `2026-99-99`: [common.schema.json](../../schema/common.schema.json#L18).
- JSON Schema `format` fields are not enforced with a `FormatChecker`: [validate_schema.py](../../scripts/validate_schema.py#L47).
- Schemas are parsed as JSON but not checked against the Draft 2020-12 meta-schema.
- The compatibility policy promises preserved older schemas, but no versioned schema bundle exists.

### High: foundation governance remains non-operational

The governance layer is largely unchanged:

- CODEOWNERS still names `@your-org/maintainers`: [CODEOWNERS](../../.github/CODEOWNERS#L8).
- The security contact does not exist: [SECURITY.md](../../SECURITY.md#L22).
- One merged contribution qualifies someone to review: [GOVERNANCE.md](../../GOVERNANCE.md#L32).
- Maintainer consensus has no quorum.
- A single maintainer can make the final determination on a disputed claim: [GOVERNANCE.md](../../GOVERNANCE.md#L63).
- There is no DCO, CLA, or explicit inbound-rights attestation.
- The confidential-material prohibition is not consistently implemented in CONTRIBUTING, SECURITY, ETHICS, and submission templates.
- Package maintainers are optional and have no relationship to CODEOWNERS or branch rules.

The Evidence Submission template also directly contradicts D-011 by asking contributors to put claim IDs and global polarity on Evidence: [evidence_submission.md](../../.github/ISSUE_TEMPLATE/evidence_submission.md#L27), [evidence_submission.md](../../.github/ISSUE_TEMPLATE/evidence_submission.md#L45).

## Engineering and security review

### Validation and test assurance

The self-test and pytest suite are significant improvements, but the proving matrix remains incomplete.

Missing or insufficiently isolated cases include:

- Multiple valid versions sharing a stable ID.
- Missing manifests and incomplete manifests.
- Duplicate manifest IDs, paths, and versions.
- Absolute and traversal manifest paths.
- Cross-package references without declared dependencies.
- Revision endpoints and transitions.
- Review subject version pinning.
- Confidence level/label mismatches.
- Invalid calendar dates and URI/date-time formats.
- Claim links attached to the wrong claim.
- Confidence and source-quality ceilings.
- Artifact digest verification.
- YAML aliases, depth, size, and expansion limits.
- Duplicate-key and `.yml` behavior as explicit regression tests.

The self-test requires each invalid fixture to fail at least one check: [validate.py](../../scripts/validate.py#L104). Tests assert that the intended validator is among the failures, but do not ensure the fixture violates only the documented invariant: [test_validation.py](../../tests/test_validation.py#L156). D-014's assertion that each package violates exactly one invariant is therefore not proven.

### Supply chain and tampering resistance

Positive controls include read-only GitHub Actions permissions, a timeout, a pinned Python minor version, and exact direct Python dependency versions: [validate-schema.yml](../../.github/workflows/validate-schema.yml#L9), [requirements.txt](../../scripts/requirements.txt#L4).

Remaining weaknesses:

- GitHub Actions use mutable tags rather than full commit SHAs: [validate-schema.yml](../../.github/workflows/validate-schema.yml#L19).
- Python requirements have no hashes or complete transitive lock.
- The runner image and `3.11` patch version float.
- There are no signed release manifests or two-person release controls.
- Branch protection and CODEOWNERS enforcement cannot be verified in this checkout.

No current remote-code execution or SSRF sink was identified. Future MCP or archival fetching must constrain URL schemes, redirects, DNS/IP destinations, response sizes, and timeouts. Retrieved source text must be treated as untrusted data rather than agent instructions.

### YAML resource safety

The custom SafeLoader prevents Python object construction and rejects duplicate keys, but aliases and anchors remain accepted and there are no file-size, nesting-depth, node-count, or alias-expansion limits: [boe_files.py](../../scripts/boe_files.py#L36).

This is primarily a CI denial-of-service risk today. It becomes an ingestion-service risk if validation is later exposed through MCP or a web service.

### Privacy and confidential material

The repository states that confidential material is prohibited until a private evidence vault exists, but the prohibition appears mainly in decision and AI-instruction prose. It is not consistently enforced through schemas, CONTRIBUTING, SECURITY, ETHICS, or issue templates.

Person records can hold employment, affiliation, nationality, date-of-birth, pseudonym, and relevance data without sensitivity, legal-basis, public-interest, redaction, or retention metadata. That is insufficient before investigations involving living people are accepted.

## MCP and AI readiness

The revised model improves confidence lookups and claim/evidence relationship queries, but the following capabilities are not naturally reliable yet:

| Capability | Current readiness | Required change |
| --- | --- | --- |
| Semantic search | Partial | Derived full-text/vector index with stable chunk identities and edition-aware results. |
| Evidence retrieval | Partial | Exact Source version, artifact digest, and structured selector. |
| Relationship queries | Weak | Controlled, versioned predicate vocabulary with direction, inverse, domain, and range. |
| Timeline queries | Weak | Date intervals, precision semantics, and generated rather than manually duplicated ordering. |
| Confidence lookup | Partial | One current Assessment per Claim per edition and enforced dimension completeness. |
| Provenance traversal | Partial | End-to-end path from claim version through link, evidence version, source version, artifact digest, and selector. |
| Cross-package queries | Weak | Publisher namespace, immutable dependency edition URI/digest, and dependency enforcement. |

Every future MCP response should identify its `edition_id`, `entity_id`, `version_id`, and, where evidence is involved, the artifact digest and selector. Results need deterministic ordering and pagination.

AI agents should not parse arbitrary filesystem YAML at query time. They should consume a generated, edition-pinned read model.

## ADR Review

| Decision | Verdict | Reason |
| --- | --- | --- |
| D-001: YAML canonical | **Modify** | Keep YAML for authoring; canonical releases should be deterministic JSON. |
| D-002: typed ULID IDs | **Replace with D-009** | Stable typed IDs remain useful, but entity and version identity must be distinct. |
| D-003: original confidence scale | **Replace with D-010** | Correctly superseded. |
| D-004: original revision model | **Replace with D-009** | Correctly superseded conceptually; the new implementation is currently contradictory. |
| D-005: Apache 2.0 | **Modify** | Appropriate for software; package data, quotations, and third-party artifacts need an explicit rights regime. |
| D-006: self-contained packages | **Modify** | Add publisher namespace, immutable edition identity, dependency URI, and digest. |
| D-007: defer MCP | **Keep** | Correct sequencing; do not build MCP on the current unstable release model. |
| D-008: Python validation | **Keep** | Accessible and appropriate; package it as a reproducible CLI. |
| D-009: stable/version identity | **Keep concept, repair implementation** | The right model, but currently impossible to validate. |
| D-010: three assessment dimensions | **Keep, strengthen** | Good conceptual correction; require and enforce the dimensions. |
| D-011: ClaimEvidenceLink | **Keep, strengthen** | Correct edge model; add exact endpoint versions or edition-bound resolution. |
| D-012: package manifests | **Modify substantially** | Replace the mutable singleton release authority with immutable Edition manifests. |
| D-013: artifact fixity | **Keep, strengthen** | Require exact artifact anchoring, rights basis, and optional byte verification. |
| D-014: self-proving validation | **Keep, extend** | Add isolated negative fixtures and exact failure assertions for every declared invariant. |

## Technical Debt Register

### Critical

| ID | Debt | Exit condition |
| --- | --- | --- |
| C-01 | Stable-ID/version validation contradiction | Multiple immutable versions with one stable ID validate, while every `version_id` remains globally unique. |
| C-02 | No immutable, content-addressed release edition | Historical releases are reconstructable from model artifacts without relying on Git archaeology. |
| C-03 | Historical references are not version- or edition-pinned | Assessments, reviews, revisions, links, and publications resolve exact immutable versions. |

### High

| ID | Debt | Exit condition |
| --- | --- | --- |
| H-01 | Manifest omission, traversal, completeness, and uniqueness gaps | Mandatory manifests are path-contained, exhaustive, unique, and dependency-aware. |
| H-02 | Revision transitions are not validated | Old/new versions exist, differ, share stable identity/type, and match the released edition. |
| H-03 | Assessment semantics are not enforced | Required dimensions, link ownership, contrary evidence, labels, and confidence ceilings are validated. |
| H-04 | Evidence is not anchored to exact artifact bytes | Evidence identifies Source version, artifact digest, and structured selector. |
| H-05 | False SHA-256 example | Examples use verified synthetic bytes or explicitly non-digest placeholders that cannot imply verification. |
| H-06 | Schema identity/version contract is inconsistent | Canonical versioned schema URIs, a coherent bundle version, preserved predecessors, and migration policy exist. |
| H-07 | Contestable facts bypass Claim/Assessment | Every contestable assertion is derived from or cites assessed claim versions. |
| H-08 | Operational governance is absent | Real ownership, quorum, succession, appeals, security/CoC contacts, and release authority exist. |
| H-09 | Inbound and third-party rights are unenforced | DCO/CLA decision, structured rights basis, package-data licence, and quotation/artifact policy are implemented. |
| H-10 | Privacy/confidential-data controls are inadequate | Normative prohibition and privacy/sensitivity/redaction policy are enforced before real investigations. |
| H-11 | Contributor templates contradict the model | Issue and PR templates implement D-009 through D-013, confidential-data rules, and AI disclosure. |

### Medium

| ID | Debt | Exit condition |
| --- | --- | --- |
| M-01 | Date/URI formats and schema meta-validity are incomplete | Calendar dates, URI/date-time formats, and every schema are validated with appropriate checkers. |
| M-02 | YAML resource limits are absent | File size, depth, node count, and alias expansion are bounded and tested. |
| M-03 | CI supply-chain inputs float | Actions are SHA-pinned and dependencies are hash-locked. |
| M-04 | Cross-package resolution ignores declared dependencies | Only declared, immutable package editions can satisfy external references. |
| M-05 | Relationship predicates are free text | A versioned predicate registry defines direction, inverse, domain, range, and contestability. |
| M-06 | Lifecycle status is inconsistent across entities | Publication eligibility is machine-determinable for every current entity version. |
| M-07 | Negative fixtures are not isolated | Every fixture proves one intended invariant with exact expected failures. |
| M-08 | No deterministic build/reproducibility test | Repeated builds yield identical canonical JSON and generated publication digests. |
| M-09 | Documentation and metadata drift | Roadmap, Versioning, CFF, README, terminology, examples, schemas, and templates agree. |

### Low

| ID | Debt | Exit condition |
| --- | --- | --- |
| L-01 | README advertises nonexistent or duplicate directories | Repository map matches tracked structure. |
| L-02 | Default developer command fails in the intentionally empty checkout | Onboarding documents the self-test and intentional `--allow-empty` behavior. |
| L-03 | Public AI instructions contain individual/local-path assumptions | Instructions use formal roles and repository-neutral paths. |

## Recommended target architecture

YAML should remain the contributor-facing authoring format, but it should not be the immutable release format.

```text
Version-controlled YAML authoring
              |
      validate + normalize
              v
Immutable RFC 8785 JSON Edition
  - edition ID and parent edition
  - exact entity versions and digests
  - schema/methodology URIs
  - dependency edition URIs/digests
  - release digest/signature
              |
      +-------+----------+
      |       |          |
      v       v          v
SQLite/FTS  Markdown    JSON-LD
MCP index   publication interop export
```

The immutable release envelope should contain `entity_id`, `version_id`, canonical schema URI, payload digest, creation metadata, and exact dependency identities.

SQLite should be generated rather than canonical. DuckDB is suitable for analytical exports, not the core entity graph. JSON-LD/RDF should be an interoperability projection rather than the contributor-facing source format.

Markdown should remain generated. Generated publications must identify the exact edition from which they were built and should be reproducible byte-for-byte where practical.

## Recommendations

### Immediate — before any evidence-bearing or tagged release

1. Repair stable-ID/version validation.
2. Introduce immutable Edition manifests.
3. Make package manifests mandatory and enforce path containment, completeness, uniqueness, slug identity, and dependencies.
4. Pin Revision, Review, claim/evidence links, and evidence provenance to exact versions or a rigorously enforced edition context.
5. Add semantic validation for assessments, revision transitions, claim-link ownership, contrary evidence, and confidence ceilings.
6. Remove the false digest and add a verifiable synthetic artifact fixture.
7. Replace placeholder schema URIs and publish one coherent, versioned schema bundle.
8. Correct issue/PR templates and contributor documentation.
9. Establish real ownership, security/CoC contacts, quorum, appeals, inbound rights, and release authority.
10. Put the confidential-material prohibition into normative contributor-facing policy.
11. Run the complete suite in a clean, provisioned environment and preserve the result.

### Near-term — v0.2

1. Add structured evidence selectors.
2. Introduce controlled relationship predicates.
3. Resolve the Event/Relationship/Finding assertion bypass.
4. Add privacy, sensitivity, redaction, retention, and legal/public-interest basis metadata.
5. Add manifest-attack, version-transition, confidence, cross-package, YAML-limit, and exact-provenance fixtures.
6. Generate deterministic JSON and Markdown in CI.
7. Pin Actions to commit SHAs and use hashed dependency locking.

### Medium-term — v0.5

1. Build the SQLite/FTS read model and edition-aware MCP server.
2. Implement dependency-aware cross-package resolution.
3. Add schema and edition migration tooling.
4. Add reproducibility verification, signed manifests, and two-person evidence-release approval.
5. Test the model with several materially different pilot investigations before freezing the schema.

### Long-term — v1.0

1. Publish compatibility, preservation, and deprecation commitments.
2. Operate maintainer succession, quorum, and independent appeal structures in practice.
3. Establish archival storage and routine artifact-integrity audits.
4. Support reproducible exports and long-term schema migrations.
5. Seek foundation adoption only after the governance and release processes are demonstrably operational.

## Final Verdict

### 1. Would I approve this repository for public release?

**Only as a clearly labelled, source-only pre-alpha scaffold for public inspection.** I would not approve a tagged platform release, publication of a real investigation, or foundation endorsement.

### 2. What prevents approval?

The broken immutable-version workflow, mutable and non-reproducible release authority, incomplete manifest validation, insufficient exact provenance, unenforced assessment semantics, and non-operational governance.

### 3. What would I change before release?

Fix D-009 and D-012 together, introduce immutable editions and version-aware references, enforce provenance and assessment invariants, then operationalise ownership, rights, privacy, and peer-review policy.

### 4. Could this realistically become a decade-long open-source project?

**Yes.** The mission and revised conceptual model are strong enough. The identity and release model must be corrected before real datasets make those changes expensive.

### 5. What would I revisit immediately if this repository were my own?

In order:

1. D-009 and D-012 as one coherent versioning/release design.
2. D-001's definition of canonical data.
3. D-013's Evidence-to-artifact chain.
4. D-006's cross-package identity model.
5. Governance authority, independence, and appeals.

## Approval condition

This review should be revisited after the Critical items and H-01 through H-06 are addressed and the complete runtime validation suite has been independently executed. Governance, rights, privacy, and operational ownership must be resolved before accepting real investigation contributions.
