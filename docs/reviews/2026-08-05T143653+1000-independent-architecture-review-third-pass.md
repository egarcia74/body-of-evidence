---
review_title: "Independent Architecture Review: Body of Evidence — Third Pass"
reviewed_at: "2026-08-05T14:36:53+10:00"
reviewed_commit: "587329961604de429d8f0fe00119278f558e1ce4"
comparison_commit: "99e70f3cd5abb250d086c72dcf48a88fa8391993"
review_type: "independent-principal-architect-follow-up"
review_status: "final"
verdict: "conditional-go-pre-alpha-no-go-evidence-release"
---

# Independent Architecture Review: Body of Evidence — Third Pass

## Verdict

**The central versioning contradiction is fixed, but the repository remains a no-go for a tagged, evidence-bearing, or foundation-endorsed release.**

The repository may be published for inspection as an explicitly labelled pre-alpha architecture and tooling scaffold after restoring a green CI and lint baseline. It is not ready to publish real investigations or claim independently reproducible evidentiary integrity.

Estimated overall readiness improves from **4.8/10 to 5.8/10**. This is material progress. The remaining critical risks are no longer accidental contradictions: they are acknowledged architectural work, principally immutable editions and version-aware references. That is a healthier position, but acknowledgement does not remove the release risk.

## Review basis

This review examined commit `587329961604de429d8f0fe00119278f558e1ce4`, comparing it with the repository state immediately after the [second-pass architecture review](2026-08-05T095947+1000-independent-architecture-review-second-pass.md), committed at `99e70f3cd5abb250d086c72dcf48a88fa8391993`.

The review treated the remediation summary as claims to verify. It covered:

- Stable identity and immutable version semantics
- Package manifest enforcement
- Revision transition integrity
- Assessment and confidence semantics
- Source artifact fixity
- Test and fixture quality
- CI and documentation quality
- Governance, licensing, privacy, and security
- AI and MCP readiness
- The proposed immutable Edition architecture in D-016

Independent runtime verification completed:

- `python -m pytest tests/ -q`: **20 passed**.
- `python scripts/validate.py --self-test --allow-empty`: **passed** with one valid and six invalid fixture packages.
- Both documented synthetic artifact byte lengths and SHA-256 digests were independently recomputed and matched.
- Python compilation completed successfully.
- Git object integrity reported no corruption; only ordinary unreachable objects were present.
- The worktree was clean before this review document was created.

Two direct semantic probes were also performed:

1. A Revision whose old and new version IDs belonged to unrelated entity files was accepted with no errors.
2. A manifest containing no Investigation entity was accepted with no errors.

The configured Markdown lint rule set failed across numerous tracked documents. `git show --check 5873299` also reported trailing whitespace introduced in the issue and pull-request templates.

## Executive Summary

### Material improvements

The remediation genuinely resolves the previous release-blocking implementation contradiction:

- Repeated stable entity IDs are now valid across immutable version files: [validate_ids.py](../../scripts/validate_ids.py#L54).
- `version_id` values remain globally unique and `(id, version_id)` pairs remain unique: [validate_ids.py](../../scripts/validate_ids.py#L97).
- The valid fixture contains two versions of one Claim and a connecting Revision: [claim-scoring-v1-superseded.yaml](../../fixtures/valid/harbour-tender-inquiry/claims/claim-scoring-v1-superseded.yaml), [revision-scoring-precision.yaml](../../fixtures/valid/harbour-tender-inquiry/revisions/revision-scoring-precision.yaml).
- Manifests are mandatory and enforce lexical containment, duplicate entry checks, path existence, path-to-entity identity, slug consistency, and partial Investigation consistency: [validate_references.py](../../scripts/validate_references.py#L138).
- Revision endpoints and revision type are required by schema: [revision.schema.json](../../schema/revision.schema.json#L8).
- Assessment dimensions are required and confidence labels are paired with levels: [assessment.schema.json](../../schema/assessment.schema.json#L8).
- Tier D and E sources are advisories rather than invalid records: [validate_provenance.py](../../scripts/validate_provenance.py#L51).
- The false digest example has been replaced with honestly labelled, independently verifiable synthetic bytes: [source.yaml](../../examples/source.yaml#L23).
- Contributor templates now put polarity on ClaimEvidenceLink rather than Evidence and include confidentiality and AI-assistance declarations: [evidence_submission.md](../../.github/ISSUE_TEMPLATE/evidence_submission.md#L35).
- The confidential-material prohibition is now normative in contributor-facing policy: [CONTRIBUTING.md](../../CONTRIBUTING.md#L81).
- All 16 schemas now declare version `0.2.0`.
- D-016 correctly records immutable editions, canonical JSON, and version-aware references as one coherent design problem: [DECISIONS.md](../../DECISIONS.md#L260).

These are substantive corrections rather than documentation-only changes.

### Remaining weaknesses

The most important remaining issues are:

1. There is still no immutable, content-addressed release Edition.
2. References generally identify stable entities, not exact versions or a binding Edition context.
3. Revision validation proves endpoint existence, but not that the endpoints are versions of the revised entity.
4. A manifest can omit its Investigation entity and still validate.
5. Manifest containment is lexical and can be bypassed through repository symlinks.
6. Evidence remains unpinned to an exact Source version, artifact digest, and structured selector.
7. Assessment link ownership, contrary-evidence completeness, and confidence ceilings remain unenforced.
8. Contestable Event and Relationship assertions can still bypass the Claim/Assessment path.
9. Governance, security contacts, inbound rights, privacy controls, release authority, and appeals remain non-operational.
10. The declared Markdown lint gate is not clean.

### Major risk

The principal risk remains **false assurance**, but it is now narrower.

The ID workflow is no longer contradictory. The remaining false-assurance risk is that syntactically valid manifests, Revisions, and provenance metadata can imply stronger historical and evidentiary guarantees than are actually enforced. In particular, a Revision can connect unrelated versions, and a digest can be present without any Evidence record proving which exact artifact bytes it was extracted from.

## Architecture Scorecard

| Category | Second pass | Third pass | Assessment |
| --- | ---: | ---: | --- |
| Repository architecture | 6.0 | **6.2** | Package and fixture boundaries remain sound; documentation and placeholder areas still drift. |
| Data model | 6.5 | **6.8** | Stable/version identity now works; exact release and reference identity remain unresolved. |
| Validation | 5.0 | **6.5** | Core enforcement improved and runs successfully; semantic transition holes remain. |
| Testing and automation | 4.5 | **6.0** | Twenty tests and the self-test pass; negative coverage and lint health remain incomplete. |
| Documentation | 5.0 | **5.3** | D-015/D-016 are clear; Roadmap, Versioning, Security, CFF, URLs, and lint state conflict. |
| Governance | 2.0 | **2.5** | Confidentiality policy improved; authority and human processes remain placeholders. |
| Maintainability | 5.0 | **5.8** | Better invariants and fixtures; semantic indices remain lossy and rules are split across code and prose. |
| Extensibility | 6.0 | **6.2** | Direction is credible; cross-package and Edition identity are still absent. |
| AI readiness | 5.0 | **5.2** | Structured authoring is appropriate; agents still lack an immutable query context. |
| MCP readiness | 4.0 | **4.3** | Deferred MCP remains correct; deterministic Edition-aware retrieval is not yet possible. |
| Security and integrity | 4.5 | **5.0** | Better manifest checks and honest digests; signing, exact provenance, resource limits, and supply-chain controls remain. |
| Open-source readiness | 4.0 | **4.8** | Suitable for pre-alpha inspection after CI hygiene, not foundation adoption. |
| **Overall** | **4.8** | **5.8** | Meaningful remediation, with acknowledged critical architecture still unimplemented. |

## Remediation Assessment

| Finding | Status | Assessment |
| --- | --- | --- |
| C-01: stable/version ID contradiction | **Resolved** | Implementation now matches D-009. |
| C-02: immutable editions | **Open, accepted** | D-016 is the correct direction, but no release artifact exists. |
| C-03: version-pinned references | **Open, accepted** | Still a release blocker. |
| H-01: manifest validation | **Mostly resolved** | Mandatory, unique, and path-checked; Investigation omission, resolved containment, completeness, and dependencies remain. |
| H-02: Revision transitions | **Partially resolved** | Fields exist and endpoints must exist and differ; endpoint identity and release transition are not validated. |
| H-03: Assessment semantics | **Partially resolved** | Required dimensions and label pairing are fixed; graph semantics remain open. |
| H-04: Evidence artifact anchoring | **Open** | Correctly recognised as part of the Edition/provenance design. |
| H-05: false SHA-256 example | **Resolved** | Both synthetic examples are honest and reproducible. |
| H-06: schema identity/version contract | **Partially resolved** | Bundle versions agree; placeholder `$id` URIs and preservation/migration remain. |
| H-07: contestable fact bypass | **Open** | Event and Relationship remain alternative assertion paths. |
| H-08: governance | **Open** | Ownership, quorum, succession, appeals, and release authority remain absent. |
| H-09: inbound and third-party rights | **Open** | DCO/CLA and package-data/content licensing decisions remain. |
| H-10: privacy and confidential data | **Partially resolved** | Prohibition is normative; sensitivity, legal basis, redaction, retention, and incident operations remain. |
| H-11: contributor templates | **Substantially resolved** | Templates reflect the current model, but contain lint defects. |
| M-07: isolated negative fixtures | **Partially resolved** | Isolation improved, but semantic transition and attack cases remain absent. |
| M-09: documentation drift | **Open** | Roadmap, CFF, security support, repository URLs, and current version disagree. |

## Release-Blocking Findings

### Critical: no immutable, content-addressed Edition

`package.yaml` remains a mutable working head. A historical publication cannot be reconstructed solely from immutable model artifacts without locating the corresponding Git state.

D-016 correctly proposes:

- RFC 8785 canonical JSON
- Edition identity and parent identity
- Exact entity version membership and payload digests
- Immutable dependency identities
- Release digest and optional signature

This design is not implemented. Until it is, `release_version` is metadata on a mutable file rather than a self-verifying release object.

### Critical: references are not version- or Edition-pinned

ClaimEvidenceLink, Evidence, Assessment, Review, Finding, Event, and Relationship references generally resolve stable IDs against a mutable current manifest. A later manifest can silently change which exact Claim, Evidence, Source, or Assessment version a historical record appears to reference.

Every generated publication and MCP response ultimately needs a declared Edition context. Where a relationship must remain valid across Editions, the model should state that intentionally; it must not happen accidentally through stable-ID lookup.

### High: Revision endpoints can belong to unrelated entities

[`validate_revision_versions`](../../scripts/validate_references.py#L243) checks only that `old_version_id` and `new_version_id` occur in the version index and are different.

It does not establish that:

- Both version files share `Revision.entity_id`.
- Both version files match `Revision.entity_type`.
- The old and new versions belong to the same investigation.
- The old version is excluded from the released current set.
- The new version is included in the released current set.
- The transition is chronologically and semantically plausible.

A direct probe supplied existing version IDs mapped to unrelated entity paths. The function returned an empty error list.

Required correction: change `version_index` from `version_id -> path` to `version_id -> {path, id, type, investigation_id, manifest_membership}` and validate the complete transition.

### High: a manifest may omit its Investigation entity

[`validate_manifest`](../../scripts/validate_references.py#L218) compares the manifest's `investigation_id` only if an Investigation entry is encountered. If no Investigation entry exists, validation succeeds.

A direct probe using a claim-only manifest returned an empty error list.

Required correction:

- Require exactly one Investigation entry in every manifest.
- Require its stable ID to equal `manifest.investigation_id`.
- Require its version and path to match the referenced file.
- Require every investigation-scoped current entity to belong to that Investigation.

### High: Revision and manifest fixtures do not falsify the full claims

The valid fixture proves that repeated stable IDs can pass. It does not prove that Revision semantics are correct. There are no isolated invalid fixtures for:

- Revision endpoints belonging to different entities
- Revision `entity_type` disagreement
- Revision old version being current and new version being absent
- Missing Investigation manifest entry
- Duplicate or absent Investigation entries
- Manifest symlink escape
- Entity belonging to a different Investigation

D-014 should require exact expected error categories, not merely that the intended validator appears among failures.

## Engineering and Security Review

### Runtime validation

The project now has independently confirmed executable tests. This materially improves confidence over the second pass, where dependencies were unavailable.

Verified results:

- Twenty pytest tests passed.
- The valid Harbour Tender fixture passed every validator.
- All six invalid fixture packages were rejected.
- `duplicate-version-id` failed only ID validation.
- `missing-manifest` failed only reference validation.
- `broken-reference` failed only reference validation.
- `orphan-evidence` failed only orphan validation.

The suite is useful, but it is still a small proof matrix for a model that intends to carry contested public claims. The next test expansion should target semantic graph invariants rather than additional schema happy paths.

### Manifest containment

[`_path_is_contained`](../../scripts/validate_references.py#L126) rejects absolute paths and literal `..` path segments. That closes ordinary traversal. It does not resolve the target and prove that it remains below the package root.

A tracked symlink can therefore point outside the investigation package while passing lexical containment. Either prohibit symlinked entity paths or resolve the package root and target with strict containment before loading.

### Markdown and commit hygiene

The local Markdown lint run using the repository workflow's enabled rule set failed across many tracked files. Failures include list and heading spacing, fenced-code language declarations, table formatting, and duplicate headings.

The remediation commit also adds trailing whitespace to:

- `.github/ISSUE_TEMPLATE/evidence_submission.md`
- `.github/PULL_REQUEST_TEMPLATE.md`

Consequently, `git show --check 5873299` reports errors. Before public release, either make the documentation conform or deliberately configure a narrower lint policy. A permanently red quality gate is worse than no gate.

### Supply-chain and tampering resistance

The positive controls remain:

- Read-only GitHub Actions permissions
- Job timeout
- Exact direct Python dependency versions
- Local JSON Schema reference resolution
- Safe YAML loading with duplicate-key rejection

Remaining gaps:

- GitHub Actions use mutable tags.
- Python dependencies are not hash-locked with their complete transitive graph.
- Runner image and Python patch version float.
- No signed Edition or release manifest exists.
- No two-person evidence-release control exists.
- Branch protection and CODEOWNERS enforcement are not represented as verifiable repository policy.
- YAML size, depth, node-count, and alias-expansion limits remain absent.

### Governance, privacy, and rights

The confidential-material prohibition is now clear and appropriately strict. This resolves the immediate contradiction in contributor guidance.

It does not replace operational governance:

- CODEOWNERS still names `@your-org/maintainers`: [CODEOWNERS](../../.github/CODEOWNERS#L8).
- The security email is still unavailable: [SECURITY.md](../../SECURITY.md#L22).
- One merged contribution still qualifies a contributor to review: [GOVERNANCE.md](../../GOVERNANCE.md#L32).
- Maintainer consensus still lacks a quorum and succession rule.
- A single maintainer may still make the final determination on a disputed claim: [GOVERNANCE.md](../../GOVERNANCE.md#L63).
- There is no independent appeal path.
- No DCO/CLA or equivalent inbound-rights attestation exists.
- Apache 2.0 still does not answer the licensing treatment of package data, quotations, or third-party artifacts.
- Person data lacks sensitivity, legal/public-interest basis, redaction, retention, and correction metadata.

These issues require human decisions. That makes them non-automatable, not optional.

## MCP and AI Readiness

The model is more coherent for AI consumption than it was at the second pass, but current-state lookup is not historical reproducibility.

| Capability | Readiness | Remaining requirement |
| --- | --- | --- |
| Semantic search | Partial | Edition-aware derived index with stable chunk identities. |
| Evidence retrieval | Weak-to-partial | Source version, artifact digest, selector, and Edition identity. |
| Relationship queries | Weak | Controlled predicate registry and exact endpoint resolution. |
| Timeline queries | Weak | Valid date intervals, precision semantics, and derived ordering. |
| Confidence lookup | Partial | One applicable current Assessment per Claim per Edition and semantic validation. |
| Revision history | Weak | Verified same-entity transitions and immutable Edition ancestry. |
| Provenance traversal | Partial | Claim version → link version → evidence version → Source version → artifact digest → selector. |
| Cross-package queries | Weak | Publisher namespace and immutable dependency Edition identities. |

AI agents should continue to consume generated read models rather than recursively parsing YAML at query time. Every MCP response should identify its Edition, stable entity ID, exact version ID, and provenance chain. Retrieved source text must remain untrusted data rather than agent instructions.

## ADR Review

| Decision | Verdict | Reason |
| --- | --- | --- |
| D-001: YAML canonical | **Modify through D-016** | Keep YAML for authoring; deterministic JSON should become the release representation. |
| D-002: typed ULID IDs | **Superseded by D-009** | Stable typed identity remains useful; version identity is separate. |
| D-003: original confidence model | **Superseded by D-010** | The replacement is materially better. |
| D-004: original revision model | **Superseded by D-009/D-015** | Immutable versions now work, but transition enforcement remains incomplete. |
| D-005: Apache 2.0 | **Modify** | Appropriate for software, insufficient as the complete content and data rights policy. |
| D-006: self-contained packages | **Modify** | Add immutable Edition identity, publisher namespace, and dependency digests. |
| D-007: deferred MCP | **Keep** | Correct sequencing; do not implement MCP before D-016. |
| D-008: Python validation | **Keep** | Appropriate and accessible; evolve it into a reproducible CLI. |
| D-009: stable/version identity | **Keep** | The implementation contradiction is resolved. |
| D-010: assessment dimensions | **Keep, strengthen** | Structure is sound; semantic relationships require enforcement. |
| D-011: ClaimEvidenceLink | **Keep, strengthen** | Correct edge model; exact endpoint resolution is still needed. |
| D-012: package manifest | **Modify substantially** | Retain as mutable authoring head; compile immutable Editions. |
| D-013: artifact fixity | **Keep, strengthen** | Honest digests are present; Evidence must anchor exact bytes and selectors. |
| D-014: self-proving validation | **Keep, extend** | Add falsification cases for every semantic claim. |
| D-015: versioning repair | **Keep with follow-up** | C-01 is fixed; H-01/H-02 claims are broader than current enforcement. |
| D-016: immutable Edition direction | **Keep and prioritise** | This is the correct next architectural milestone. |

## Technical Debt Register

### Critical

| ID | Debt | Status | Exit condition |
| --- | --- | --- | --- |
| C-02 | No immutable, content-addressed Edition | Open | Historical releases reconstruct from immutable model artifacts without Git archaeology. |
| C-03 | References are not version- or Edition-pinned | Open | Historical relationships resolve exact immutable versions in a declared Edition. |

### High

| ID | Debt | Status | Exit condition |
| --- | --- | --- | --- |
| H-01 | Manifest enforcement remains incomplete | Partial | Exactly one Investigation, resolved containment, package membership, and dependency rules are enforced. |
| H-02 | Revision transitions are only superficially validated | Partial | Endpoints exist, differ, share ID/type/investigation, and represent the released transition. |
| H-03 | Assessment graph semantics are incomplete | Partial | Link ownership, contrary evidence, uniqueness, and confidence ceilings are validated. |
| H-04 | Evidence is not anchored to exact artifact bytes | Open | Evidence identifies Source version, artifact digest, and structured selector. |
| H-06 | Schema identity and preservation contract is incomplete | Partial | Canonical versioned URIs, preserved bundles, and migration policy exist. |
| H-07 | Contestable assertions bypass Claim/Assessment | Open | Every contestable assertion cites assessed Claim versions or is derived. |
| H-08 | Operational governance is absent | Open | Real owners, quorum, succession, appeals, contacts, and release authority exist. |
| H-09 | Inbound and third-party rights are unresolved | Open | DCO/CLA decision and explicit software/data/content/artifact policies exist. |
| H-10 | Privacy operations are inadequate | Partial | Sensitivity, legal basis, redaction, retention, correction, and incident processes exist. |
| H-12 | Declared lint gate is not clean | Open | Repository lint passes under an intentional, documented configuration. |

### Medium

| ID | Debt | Status | Exit condition |
| --- | --- | --- | --- |
| M-01 | Calendar dates, formats, and schema meta-validity are incomplete | Open | Calendar-valid dates, format checking, and meta-schema validation run in CI. |
| M-02 | YAML resource limits are absent | Open | File size, depth, nodes, and aliases are bounded and tested. |
| M-03 | CI supply-chain inputs float | Open | Actions are SHA-pinned and dependencies are fully hash-locked. |
| M-04 | Cross-package resolution is not dependency-aware | Open | Only declared immutable dependency Editions satisfy external references. |
| M-05 | Relationship predicates are free text | Open | A versioned registry defines predicate semantics. |
| M-06 | Publication eligibility is not uniform | Open | Current and publishable status is machine-determinable for every entity type. |
| M-07 | Negative fixtures do not cover full semantics | Partial | Each invariant has an isolated positive/negative proof and exact failure assertion. |
| M-08 | No deterministic build test exists | Open | Repeated builds produce identical canonical JSON and publication digests. |
| M-09 | Documentation and metadata drift | Open | Roadmap, Versioning, Security, CFF, URLs, schemas, and release state agree. |

### Low

| ID | Debt | Status | Exit condition |
| --- | --- | --- | --- |
| L-01 | Repository maps include planned or duplicated areas | Open | Maps distinguish tracked, generated, and planned paths. |
| L-02 | Empty-checkout onboarding remains awkward | Partial | Default contributor workflow clearly starts with self-test. |
| L-03 | AI instructions retain individual/local assumptions | Open | Public instructions use roles and repository-neutral examples. |

## Recommended Target Architecture

The target architecture from the second review remains appropriate:

```text
Version-controlled YAML authoring
              |
      validate + normalize
              v
Immutable RFC 8785 JSON Edition
  - edition ID and parent edition
  - exact entity versions and payload digests
  - schema and methodology URIs
  - dependency Edition identities and digests
  - release digest and optional signature
              |
      +-------+----------+
      |       |          |
      v       v          v
SQLite/FTS  Markdown    JSON-LD
MCP index   publication interop export
```

`package.yaml` should remain the contributor-friendly mutable working head. It should not itself be called the immutable release. A release command should validate the working package, normalize it, generate an immutable canonical Edition, calculate digests, build deterministic publications and indexes, and record the Edition identity in every output.

SQLite should be generated and Edition-specific. DuckDB remains appropriate for analytical exports, not canonical identity. JSON-LD/RDF should remain interoperability projections rather than the authoring source of truth.

## Recommendations

### Immediate — before public pre-alpha release

1. Fix Revision same-entity/type/investigation validation.
2. Require exactly one Investigation manifest entry.
3. Resolve manifest paths and reject symlink escape.
4. Add isolated fixtures for those three cases.
5. Restore a green Markdown lint and `git show --check` baseline.
6. Reconcile Roadmap, Security support, CFF, repository URLs, and current version metadata.
7. Retain explicit pre-alpha and no-evidence-use warnings.

### Near-term — v0.2, before real investigation data

1. Complete the D-016 Edition ADR before further identity changes.
2. Implement immutable canonical Editions and deterministic build verification.
3. Make all historical references exact or rigorously Edition-scoped.
4. Add Evidence-to-Source-version, artifact-digest, and selector anchoring.
5. Add Assessment link-ownership and confidence-ceiling validation.
6. Establish real CODEOWNERS, security/CoC contacts, quorum, appeals, and release authority.
7. Decide DCO/CLA and software/data/content/artifact licensing policy.
8. Add privacy, redaction, retention, and public-interest/legal-basis policy.

### Medium-term — v0.5

1. Generate an Edition-aware SQLite/FTS read model.
2. Implement the MCP server over the generated read model, not raw YAML.
3. Add controlled relationship predicates and temporal interval semantics.
4. Implement dependency-aware cross-package resolution.
5. Add schema and Edition migration tooling.
6. Add signed releases and two-person approval for evidence publication.
7. Validate the architecture with several materially different pilot investigations.

### Long-term — v1.0

1. Publish compatibility, preservation, and deprecation commitments.
2. Operate independent governance and appeal processes in practice.
3. Establish archival storage and routine artifact-integrity audits.
4. Support reproducible exports and long-term migrations.
5. Seek foundation adoption only after release, governance, and preservation controls have operated successfully.

## Final Verdict

### 1. Would I approve this repository for public release?

**Only as a clearly labelled pre-alpha source and architecture preview, after the declared lint/CI baseline is green.**

### 2. What prevents evidence-bearing approval?

C-02 and C-03, incomplete Revision transition validation, incomplete exact provenance, unenforced Assessment graph semantics, and non-operational governance.

### 3. Was the remediation successful?

**Yes for C-01, digest honesty, confidence pairing, contributor surfaces, schema bundle consistency, and much of manifest enforcement.** It did not fully resolve H-01 or H-02.

### 4. What should change before release?

For public pre-alpha inspection: repair the two semantic validator bypasses, resolved-path containment, tests, lint, and metadata drift.

For real evidence publication: implement D-016, exact provenance, semantic assessment validation, operational governance, rights policy, privacy operations, and release controls.

### 5. Could this realistically become a decade-long open-source project?

**Yes.** The project now has a coherent stable/version identity foundation and a credible direction for immutable Editions. The decisive condition is completing D-016 before real datasets accumulate around the mutable manifest model.

### 6. What would I revisit immediately if this repository were my own?

In order:

1. The Revision validator's lossy version index.
2. Manifest Investigation membership and resolved containment.
3. The D-016 Edition ADR.
4. Evidence-to-artifact selector design.
5. Governance authority, rights, privacy, and appeals.

## Approval condition

Re-run this review after D-016 is implemented, the Revision and manifest semantic holes are closed, and the complete suite—including lint and deterministic release tests—passes in a clean environment. No real investigation should be accepted until ownership, rights, privacy, and security contacts are operational.
