---
review_title: "Independent Architecture Review: Body of Evidence"
reviewed_at: "2026-08-05T00:18:19+10:00"
reviewed_commit: "f758968d815fa0a03f9829dc8fc75b2db5158b3f"
review_type: "independent-principal-architect"
review_status: "final"
verdict: "no-go"
---

# Independent Architecture Review: Body of Evidence

## Verdict

**No-go for release as a trustworthy evidence-publishing platform.**

The repository could be published as an explicitly labelled **pre-alpha architecture RFC**, but it should not claim platform readiness, MCP readiness, reproducibility, or evidentiary integrity in its current form.

This is a thoughtful constitution for a platform, but not yet the platform itself. The written guarantees are materially stronger than the implemented controls.

## Review basis

The review covered the repository architecture, schemas, examples, validators, tests, automation, governance, security policies, methodology, versioning, and proposed MCP interface.

Verified facts:

- 84 tracked files and 14 syntactically valid JSON schema documents.
- One scaffold commit, no release tags or configured remote in the reviewed checkout.
- No populated investigation package exists.
- Git integrity and whitespace checks completed cleanly.
- A repository-wide local Markdown scan found one broken path in the [investigation template](../../investigations/_template/README.md#L34).
- The Python test suite could not run in the supplied environment because its dependencies were absent. More importantly, pytest is not declared in [requirements.txt](../../scripts/requirements.txt#L4), and the GitHub workflow does not run it.
- The top-level validator returns success when there are no investigation packages, before performing substantive validation: [validate.py](../../scripts/validate.py#L69).

No repository files other than this review were changed.

## Executive Summary

### Strengths

The repository gets several foundational ideas right:

- The mission is clear, important, and domain-independent.
- Primary sources, provenance, uncertainty, and falsifiability are treated as first-class concerns.
- Separating sources, evidence, claims, and assessments is directionally correct.
- Investigation packages are a useful ownership and release boundary.
- Generated publications should remain downstream from structured data.
- Deferring a public MCP implementation is sensible.
- Git-based review and schema-driven authoring are appropriate for an open research platform.
- The documentation shows unusually good awareness of methodological and governance issues for an early scaffold.

These strengths justify continued investment.

### Weaknesses

The central problem is **false assurance**. The architecture document says identifiers, references, orphans, provenance, and links are validated in CI, while the [roadmap describes those mechanisms as stubs](../../ROADMAP.md#L7). With no real investigation, the current workflow can remain green without proving that a coherent evidence graph can be accepted or rejected.

The most serious architectural defects are:

1. Conceptual entity identity is conflated with immutable versions and revisions.
2. Evidence polarity is stored on evidence rather than on the claim-evidence relationship.
3. Contested status is conflated with confidence.
4. Provenance records locations and acquisition narratives but not the integrity of exact source bytes.
5. Events, findings, and relationships can assert facts outside the Claim to Evidence to Assessment path.
6. The repository lacks a package manifest, release manifest, and schema/methodology version boundary.
7. Governance, ownership, and security contacts are placeholders.
8. Confidential-source handling is incompatible with an ordinary public Git repository.
9. Licensing treats authored code, structured data, and third-party source material as if they were equivalent.
10. The proposed MCP server has a tool list, not yet a durable query architecture.

### Major risk

The main risk is not that the project cannot scale. It is that users could reasonably infer a level of evidentiary integrity that the software does not provide.

A validator that reports success without validating a populated investigation is worse than no validator if that green result is presented as evidence of reproducibility.

## Architecture Scorecard

| Category | Score | Assessment |
| --- | ---: | --- |
| Repository architecture | 5/10 | Understandable small-repository structure, but documentation, specifications, tooling, and future placeholders are mixed together. |
| Data model | 4/10 | Good domain vocabulary; weak identity, revision, relationship, and provenance semantics. |
| Validation | 2/10 | Structural beginnings exist, but important graph and methodological invariants are absent or bypassable. |
| Testing and automation | 2/10 | Tests do not prove end-to-end acceptance/rejection and are not run in CI. |
| Documentation | 6/10 | Extensive and thoughtful, but contains drift, placeholders, and claims about unimplemented capabilities. |
| Governance | 3/10 | Policies exist, but authority, independence, quorum, appeals, and succession are inadequate. |
| Maintainability | 4/10 | Small today, but duplicated links, revision layers, and coupled versioning will create migration debt. |
| Extensibility | 5/10 | Domain-neutral intent is strong; uncontrolled predicates and absent extension/version contracts weaken it. |
| AI readiness | 4/10 | Machine-readable, but ambiguity, missing fixity, and missing release context make reliable agent consumption unsafe. |
| MCP readiness | 3/10 | Proposed operations are sensible; storage and query semantics are not ready. |
| Security and integrity | 2/10 | No cryptographic source/release integrity, weak privacy boundary, and insufficient supply-chain hardening. |
| Open-source readiness | 2/10 | Placeholder ownership, release metadata, governance, and rights handling prevent serious foundation approval. |

**Unweighted overall score: 3.5/10.**

That score reflects implementation readiness, not the quality of the project's mission.

## Detailed Architectural Findings

### 1. Repository architecture

The self-contained investigation-package concept should be retained, but the current package is incomplete. The documented structure does not include first-class relationship, revision, publication, or dependency areas, and several documented root directories do not exist. Compare the [documented layout](../../ARCHITECTURE.md#L61) with the actual template.

Every investigation needs a machine-readable package manifest containing at least:

- Package and investigation identifiers.
- Package release version.
- Schema and methodology versions.
- Entity-version membership.
- Cross-package dependencies.
- Source-artifact manifest and rights status.
- Publication editions.
- Maintainers and review policy.
- Generation tool versions.
- Release digest and signatures.

Without this, self-contained is an aspiration rather than an enforceable property.

At scale, the repository should become a specification/tooling repository with independently releasable investigation packages and a signed catalog. Keeping packages in one monorepo initially is reasonable, provided the package contract does not assume that all investigations will always share one checkout.

### 2. Data architecture

| Area | Current problem | Recommended model |
| --- | --- | --- |
| Identity | One ID is expected to represent both a continuing concept and an immutable record. | Stable entity ID, immutable version ID, and release manifests selecting accepted versions. |
| Revision | Git history, revision entities, revision-history arrays, and mutable supersession state overlap. | Immutable versions plus a versioned ChangeSet or revision activity joining old and new versions. |
| Evidence | Evidence type makes support or contradiction intrinsic to evidence. | A claim-evidence edge carries polarity, relevance, strength, and reasoning. |
| Confidence | Label and numeric level can diverge; contested is treated as a confidence level. | Separate conclusion, epistemic confidence, dispute status, source quality, and completeness. |
| Provenance | Acquisition narrative exists but exact bytes are not securely identified. | Source work to exact artifact to evidence fragment, with SHA-256, byte length, media type, edition, and selector. |
| Assertions | Events, findings, and relationships can contain contestable facts without assessments. | Profile entities contain identity only; contestable attributes become claims or assertions. |
| Timeline | Ordered event lists duplicate data and do not model uncertain dates well. | Derive timelines from event assertions using earliest/latest bounds, precision, and timezone. |
| Publication | No structured narrative model exists. | Add publication editions and section trees referencing exact entity versions. |
| Versioning | One repository SemVer stream covers schemas, tools, and investigations. | Version specification, tools, methodology, and investigation releases independently. |

#### Identity and revision

The repository correctly values immutability, but its operational description contradicts that principle. The methodology tells contributors to preserve an old entity and then edit its status to superseded, which is still a mutation of the old record: [METHODOLOGY.md](../../METHODOLOGY.md#L117).

The current [Revision schema](../../schema/revision.schema.json#L8) does not clearly distinguish:

- The enduring conceptual entity.
- The old immutable version.
- The new immutable version.
- The activity that caused the transition.
- The release in which each version was selected.

Recommended invariant:

> Published entity-version bytes never change. A later release selects a new version and records why. Supersession is a property of the release graph, not a mutation of the old file.

#### Evidence relationships

The [Evidence schema](../../schema/evidence.schema.json#L53) makes evidence globally supporting, contradicting, or contextual. That is semantically wrong.

The same document may support claim A, contradict claim B, and merely contextualise claim C. Polarity therefore belongs on a versioned ClaimEvidenceLink.

Canonical backlinks should not be stored in both directions. The current claim/evidence arrays create divergence and cascade-update risk. Store one directional edge; generate backlinks.

#### Confidence

The current model separates labels and levels without enforcing their pairing: [common.schema.json](../../schema/common.schema.json#L29). More fundamentally, contested is not a point on the same scale as low or high confidence.

An assessment should separately record:

- Conclusion: supported, contradicted, mixed, insufficient, or not assessed.
- Epistemic confidence: a documented ordinal level.
- Dispute status: undisputed, disputed, or unresolved.
- Completeness: known evidentiary gaps.
- Quality dimensions: authenticity, proximity, independence, and corroboration.
- Methodology version.
- Exact claim and evidence-link versions considered.

Avoid pretending that an arbitrary integer is probabilistic unless the project develops and validates a calibration method.

#### Sources, artifacts, and evidence fragments

A URL does not identify evidence. URLs rot and their contents can change.

Use a minimal three-part model:

1. SourceWork: the intellectual work or record.
2. SourceArtifact: a particular edition or exact byte representation.
3. EvidenceFragment: a structured selector into that artifact.

Artifacts require:

- Cryptographic digest, preferably SHA-256 or stronger.
- Byte length and media type.
- Edition/version and acquisition time.
- Archive location and verification time.
- Rights, licence, and redistribution status.
- OCR, transcription, or translation activity and tool versions.

Selectors should use structured page, timestamp, character-range, or region coordinates rather than only free-form locators. The [W3C Web Annotation model](https://www.w3.org/TR/annotation-model/) offers useful selector vocabulary, while [PROV-O](https://www.w3.org/TR/prov-o/) provides an interoperability target for provenance.

#### Facts bypassing assessment

The [Event schema](../../schema/event.schema.json#L24) and [Finding schema](../../schema/finding.schema.json#L33) can state conclusions and attach sources or confidence directly. This bypasses the repository's claimed epistemic path.

Person and organisation records should contain identity and disambiguation data. Claims such as employment, participation, causation, or responsibility should remain assessable assertions.

Timelines and findings are better treated as derived views or publication components, not independent sources of truth.

### 3. Engineering quality

The most consequential implementation defect is the vacuous validation path. With no non-template investigation, [validate.py](../../scripts/validate.py#L69) exits successfully.

Other material gaps include:

- Schema validation scans .yaml and .yml; ID, reference, orphan, and provenance validators scan only .yaml, allowing .yml files to bypass semantic checks.
- Reference validation omits several reference-bearing fields and does not verify endpoint-type consistency or reciprocity.
- A full-repository run can accidentally legitimise undeclared cross-package references, while a package-specific run rejects them.
- The ID validator uses a permissive regex rather than actually decoding and validating a ULID.
- Date validation checks textual shape, not calendar validity.
- Duplicate YAML keys, aliases, tags, and ambiguous implicit scalar conversions are not explicitly rejected.
- jsonschema validation returns the first error and is used without an explicit local registry or format checker. The library's official guidance distinguishes [schema/resource registration](https://python-jsonschema.readthedocs.io/en/v4.18.6/referencing/) and [format validation](https://python-jsonschema.readthedocs.io/en/stable/validate/).
- The tests mostly prove that schemas and examples parse; they do not demonstrate that valid packages pass and deliberately invalid graphs fail: [test_validation.py](../../tests/test_validation.py#L20).
- The [validation workflow](../../.github/workflows/validate-schema.yml#L24) does not run the test suite.
- Dependencies are lower-bound-only and unlocked.
- GitHub Actions use mutable version tags. GitHub recommends pinning third-party actions to full commit SHAs for immutable workflow dependencies: [GitHub secure-use guidance](https://docs.github.com/en/actions/reference/security/secure-use).
- The template's ULID command uses the API from ulid-py, while the declared dependency is python-ulid: [template investigation](../../investigations/_template/investigation.yaml#L6), [python-ulid usage](https://pypi.org/project/python-ulid/).
- scripts/init-repo.command deletes a Git lock, rewrites Git identity, and stages everything. It should not be distributed as a normal public maintenance utility.

The validator should be a packaged CLI with a locked environment, typed internal model, and deterministic output, not a collection of loosely coupled scripts.

### 4. Governance and open-source readiness

An experienced maintainer should not approve the present governance model for a contentious evidence platform.

Specific blockers:

- CODEOWNERS contains placeholder teams: [CODEOWNERS](../../.github/CODEOWNERS#L8).
- Security reporting provides no operational address: [SECURITY.md](../../SECURITY.md#L22).
- A contributor may become a reviewer after one merged contribution: [GOVERNANCE.md](../../GOVERNANCE.md#L32).
- One maintainer can make a binding unresolved-challenge decision: [GOVERNANCE.md](../../GOVERNANCE.md#L63).
- Quorum, maintainer appointment/removal, succession, deadlock, and appeal procedures are absent or ambiguous.
- CODEOWNERS cannot itself enforce reviewer independence, subject-matter expertise, or a required number of approvals.
- Conflict-of-interest disclosure is described but optional in the contributor schema.
- There is no declared inbound-contribution mechanism such as DCO or CLA.
- Right-of-response is policy text rather than a structured, reviewable workflow record.
- CITATION.cff contains placeholders and lacks required author metadata; compare the local [citation file](../../CITATION.cff#L1) with the [CFF schema guide](https://github.com/citation-file-format/citation-file-format/blob/main/schema-guide.md).

Apache 2.0 is a sound code licence. It cannot automatically grant permission to redistribute third-party documents, quotations, images, or archives. Replace Apache 2.0 for all contents with:

- Apache 2.0 for original software.
- An explicit selected licence for original documentation and original datasets.
- Per-artifact rights and redistribution metadata.
- SPDX/REUSE declarations; the [REUSE specification](https://reuse.software/spec/) provides a practical mechanism.
- Legal review before redistributing source artifacts.
- A documented inbound-contribution policy.

Editorial and technical authority should also be separated. Technical maintainers should not unilaterally decide contested historical or scientific conclusions.

### 5. MCP and AI readiness

The proposed MCP operations are reasonable, but the current [MCP design](../../src/mcp/README.md#L38) plans to parse YAML on startup and asserts that no schema changes will be required. That claim is unjustified.

A durable MCP implementation needs:

- Release-aware and as-of queries.
- Exact entity-version selection.
- Typed relationship traversal.
- Pagination and deterministic ordering.
- Structured uncertainty filters.
- Provenance-chain traversal.
- Query result citations to exact artifact fragments.
- Incremental indexing.
- Index build provenance.
- Stable extension vocabularies.
- Explicit public/private data boundaries.

Use a derived SQLite database containing entity versions, edges, release membership, source manifests, and FTS indexes. Thousands of evidence records are trivial for SQLite; repeated YAML parsing and graph reconstruction are not a sensible serving design.

Semantic embeddings must remain disposable indexes. Record their model, model version, chunking method, and source digest. An embedding result must never become canonical evidence.

For AI agents:

- Keep Markdown generated.
- Preserve exact citations and selectors in every tool response.
- Mark source text as untrusted data to reduce prompt-injection risk.
- Record AI-assisted contribution activities and require accountable human approval.
- Do not let agents infer current state from filenames or Git timestamps; the release manifest must say which versions are current.

## Security and Integrity Review

| Threat | Current exposure | Required control |
| --- | --- | --- |
| Silent evidence replacement | URLs and narrative provenance do not fix exact content. | Artifact digests, archived representations, and verification records. |
| History rewriting or maintainer compromise | Git history alone is not an immutable public ledger. | Signed tags/manifests, two-person releases, and an independently mirrored transparency record. |
| Malicious YAML | Untrusted contributions can exploit aliases, ambiguity, or resource exhaustion. | Strict YAML subset, duplicate-key rejection, size/depth limits, and isolated parsing. |
| Confidential-source disclosure | Public Git history is extremely difficult to purge safely. | Separate private evidence vault, redacted public manifests, and explicit clearance workflow. |
| PII or harmful allegations | Person records lack sensitivity, redaction, and publication controls. | Data classification, field-level visibility, risk-tier review, and takedown process. |
| Dependency/workflow compromise | Unlocked dependencies and mutable action tags. | Lockfiles/hashes, full-SHA actions, least-privilege workflow permissions, and timeouts. |
| Future link-checker SSRF | Contributor-controlled URLs may cause CI to access internal services. | Separate restricted job, scheme allowlist, private-address blocking, time and size caps. |
| MCP prompt injection | Primary-source text may contain adversarial instructions. | Treat retrieved text as untrusted, typed responses, bounded output, and exact provenance. |
| Governance capture | One maintainer can decide disputed content. | Quorum, independent review, appeal, and logged recusals. |

GitHub artifact attestations can prove where a generated release bundle came from, but cannot prove that its historical or scientific conclusions are true. They are still useful for build provenance: [GitHub artifact attestations](https://docs.github.com/en/actions/concepts/security/artifact-attestations).

The policy allowing confidential provenance to be held internally has no defined private system: [ETHICS.md](../../ETHICS.md#L29). That must be resolved before any confidential-source workflow is permitted.

## Simplicity and Ten-Year Sustainability

### Overengineered

- Thirteen entity types before one real investigation has tested the model.
- Generic Relationship entities alongside bespoke cross-reference arrays.
- Revision entities, embedded revision histories, mutable statuses, and Git history all representing change.
- Timeline entities that manually duplicate ordered events.
- Empty or aspirational directories and extensive root-level documentation.
- A public MCP tool surface before the internal query model has been proven.

### Underengineered

- Source artifact integrity and preservation.
- Package and release manifests.
- Schema migration and compatibility testing.
- Rights, privacy, and redaction.
- Structured publication narratives.
- Independent review and appeals.
- Negative test fixtures.
- Reproducible builds and signed releases.
- Cross-investigation identity and dependency management.

### Decisions likely to age poorly

- YAML as the release/canonical serialization.
- One version number for schema, tooling, and investigations.
- Bidirectional reference arrays.
- In-place supersession state.
- Global evidence polarity.
- Global source-quality tiers detached from particular claims.
- Filesystem scans as the query layer.
- Deferring shared identity until many investigations already exist.
- Storing large or sensitive source material directly in normal Git history.

### Decisions worth retaining

- Structured data upstream of human-readable publications.
- JSON Schema as one validation layer.
- Investigation packages as ownership boundaries.
- Git-based public review.
- Explicit uncertainty.
- Read-only initial MCP scope.
- Delaying public MCP implementation until the data contract is sound.

## ADR Review

| Decision | Verdict | Reason |
| --- | --- | --- |
| D001 - YAML is canonical | **Replace** | Keep YAML as a constrained authoring format; publish deterministic JSON as the canonical release representation. |
| D002 - Typed ULIDs | **Modify** | Separate stable entity IDs from immutable version IDs. Prefer resolvable URIs/CURIEs with standard UUIDv7 identifiers; typed aliases may remain for human use. |
| D003 - Five-level confidence | **Replace** | Separate conclusion, confidence, dispute status, completeness, and source-quality dimensions. |
| D004 - Immutable entities and Revision entities | **Modify** | Keep immutability, but use immutable versions and release membership. Retain revision/change activities only to connect old and new versions. |
| D005 - Apache 2.0 for all contents | **Replace** | Keep Apache 2.0 for code; introduce explicit documentation/data licences and per-source rights metadata. |
| D006 - Self-contained packages | **Modify** | Add manifests, declared dependencies, shared identity resolution, and independently versioned releases. |
| D007 - Defer MCP | **Keep** | Correct decision. Prove the internal read model now, but do not ship the public server until schemas stabilise. |
| D008 - Python 3.9+ validation | **Keep** | Python is appropriate. Package the CLI, choose a currently supported minimum runtime, lock dependencies, and test a declared matrix. |

UUIDv7 is now standardised by [RFC 9562](https://www.rfc-editor.org/rfc/rfc9562.html). Either UUIDv7 or ULID can work, but neither substitutes for the conceptual-ID versus version-ID distinction.

## Technical Debt Register

### Critical

| ID | Debt |
| --- | --- |
| C1 | Validation and CI can succeed without validating a populated investigation graph. |
| C2 | Immutability, supersession, and revision identity are contradictory and unenforced. |
| C3 | Source records lack exact-byte fixity, durable preservation, and artifact identity. |
| C4 | Maintainers, owners, security contacts, and release authority are placeholders. |
| C5 | Confidential-source and PII handling is incompatible with an ordinary public Git repository. |
| C6 | Rights and licensing for structured data, quotations, and third-party source artifacts are unresolved. |

### High

| ID | Debt |
| --- | --- |
| H1 | YAML has no strict profile or deterministic canonicalisation. |
| H2 | Reference validation is incomplete and can be bypassed by .yml files. |
| H3 | Confidence labels, numeric levels, and dispute state are semantically inconsistent. |
| H4 | Evidence polarity is attached to evidence rather than claim-evidence edges. |
| H5 | Events, findings, and relationships bypass assessed claims. |
| H6 | Entities and packages lack schema, methodology, and release-version context. |
| H7 | No package manifest or cross-package dependency declaration exists. |
| H8 | Tests do not exercise full valid and invalid packages and are not run in CI. |
| H9 | Dependencies and CI actions are not immutably pinned. |
| H10 | Reviewer independence, quorum, recusal, and appeal controls are inadequate. |
| H11 | Versioning couples schema, tooling, methodology, and investigation releases. |
| H12 | MCP query semantics, release selection, and index provenance are undefined. |
| H13 | Shared person/organisation identity and merge policy are deferred too late. |
| H14 | No structured publication-edition model exists. |

### Medium

| ID | Debt |
| --- | --- |
| M1 | Date validation permits invalid dates and does not adequately model uncertain intervals. |
| M2 | Bidirectional references and revision-history arrays can diverge. |
| M3 | Relationship predicates and tags are uncontrolled free text. |
| M4 | Source taxonomy conflates medium, epistemic role, and quality. |
| M5 | Validation reports too few errors and lacks explicit schema registries and format checking. |
| M6 | Startup-wide YAML parsing will not provide an efficient query service. |
| M7 | Documentation refers to missing directories and unimplemented guarantees. |
| M8 | Citation, release, and repository metadata contain placeholders or contradict repository state. |
| M9 | Python tooling is not packaged and has no lockfile or supported-version matrix. |
| M10 | There is no large-artifact storage and preservation strategy. |
| M11 | Right-of-response and unresolved-evidence searches are not structured records. |
| M12 | AI-generated contribution provenance and prompt-injection handling are undefined. |

### Low

| ID | Debt |
| --- | --- |
| L1 | Dependencies include unused or premature libraries. |
| L2 | CI repeats checks without improving coverage. |
| L3 | scripts/init-repo.command is hazardous and repository-specific. |
| L4 | Root-level documentation is sprawling and lacks a versioned information architecture. |
| L5 | Example data is not sufficiently neutral or cross-domain to test generality. |
| L6 | One broken template documentation link remains. |

## Recommended Alternative Architecture

The strongest long-term foundation is a **compiled, content-addressed evidence graph**, not YAML-only, database-first, or RDF-first.

    Strict YAML authoring
            |
            v
    Validator + normaliser + graph invariant engine
            |
            v
    Signed release bundle
    JCS JSON + manifest + artifact digests
            |
            +--> Generated Markdown/HTML
            +--> SQLite + FTS + MCP
            +--> JSON-LD / RDF provenance export
            +--> Parquet / DuckDB analytics export

### Representation responsibilities

| Representation | Role |
| --- | --- |
| Strict YAML 1.2 subset | Human authoring and review |
| Deterministic JSON | Canonical semantic release artifact |
| Signed manifest | Release membership, dependencies, hashes, and tool versions |
| Markdown/HTML | Generated human publication |
| SQLite/FTS | Derived local and MCP query model |
| JSON-LD/RDF | Derived interoperability and graph exchange |
| Parquet/DuckDB | Derived bulk analysis |
| Content-addressed artifact storage | Exact primary-source preservation |

Deterministic JSON should follow [RFC 8785 JSON Canonicalization Scheme](https://www.rfc-editor.org/rfc/rfc8785.html), with the repository restricting data to its interoperable JSON subset.

JSON-LD is useful as an export because it preserves normal JSON usability while enabling linked-data semantics: [JSON-LD 1.1](https://www.w3.org/TR/json-ld11/). RDF should not be the contributor-facing authoring format.

SQLite should not be canonical because binary database diffs and merges are hostile to peer review. DuckDB is excellent for analytics but unnecessary as the primary serving store. RDF-first would add ontology and contributor complexity before the domain model is stable.

### Reduced canonical core

A simpler core would contain:

1. Investigation package.
2. Entity and immutable entity version.
3. Source work.
4. Source artifact.
5. Evidence fragment.
6. Claim.
7. Claim-evidence link.
8. Assessment.
9. Review/change activity.
10. Publication edition.

Person, organisation, and event profiles can be typed subject entities. Timelines, findings, backlinks, and current views should be derived.

### Recommended repository layout

    /
    +-- README.md
    +-- LICENSES/
    +-- docs/
    |   +-- architecture/
    |   +-- methodology/
    |   +-- governance/
    |   +-- adr/
    |   +-- reviews/
    +-- spec/
    |   +-- v1/
    |       +-- schema/
    |       +-- vocab/
    |       +-- context/
    +-- packages/
    |   +-- boe-cli/
    |   |   +-- pyproject.toml
    |   |   +-- src/
    |   |   +-- tests/
    |   +-- renderer/
    +-- investigations/
    |   +-- <slug>/
    |       +-- package.yaml
    |       +-- entities/
    |       +-- publications/
    +-- migrations/
    +-- fixtures/
        +-- valid/
        +-- invalid/

Do not split into many repositories immediately. Establish the package contract first, then permit independently hosted investigation packages once scale or governance requires it.

## Recommendations

### Immediate - before public release

1. Reclassify the repository as 0.0.x pre-alpha and remove claims that current controls already provide reproducibility or complete validation.
2. Resolve the identity/version/revision model before any real dataset accumulates.
3. Move evidence polarity onto versioned claim-evidence links.
4. Replace the confidence model with separate conclusion, confidence, and dispute dimensions.
5. Add source artifacts, cryptographic digests, structured selectors, and explicit rights metadata.
6. Add investigation and release manifests with schema/methodology versions and package dependencies.
7. Implement a strict YAML profile and deterministic JSON compiler.
8. Make CI fail when no required fixture or investigation is validated.
9. Add coherent valid fixtures and deliberately invalid fixtures for every invariant.
10. Run unit, schema, graph, migration, link, and reproducibility tests in CI.
11. Pin dependencies and GitHub Actions; set minimal permissions and job timeouts.
12. Replace all organisation, contact, citation, and release placeholders.
13. Establish maintainers, quorum, recusal, appeals, succession, and two-person release rules.
14. Resolve code, data, and source-artifact licensing.
15. Prohibit confidential material in public Git until a private/redacted publication architecture exists.
16. Use fictional or legally safe multi-domain examples rather than one politically sensitive fixture set.
17. Create a real signed/tagged release only after these controls pass.

### Near-term - v0.2

- Run at least three heterogeneous pilot investigations before freezing the schema.
- Build the packaged validator/compiler and deterministic renderer.
- Introduce publication editions and section manifests.
- Add shared identity resolution and declared cross-package dependencies.
- Add source preservation workflows and verification checks.
- Separate schema, tooling, methodology, and investigation version streams.
- Implement a SQLite query CLI proving evidence, relationship, confidence, timeline, and provenance queries.
- Add schema migrations and backwards-compatibility tests.
- Establish risk-tiered editorial, domain, and legal review.
- Structure right-of-response, challenge, and resolution records.

### Medium-term - v0.5

- Build the derived SQLite/FTS index and read-only MCP server.
- Require MCP queries to specify or return package release and entity versions.
- Add optional semantic indexing with reproducible index metadata.
- Export JSON-LD/PROV-O and Parquet datasets.
- Introduce a signed package catalog and independently releasable investigations.
- Add incremental validation and index rebuilding.
- Add preservation, link-health, and source-fixity monitoring.
- Establish reviewer and governance dashboards.

### Long-term - v1.0

- Stabilise the specification only after diverse external implementations exist.
- Publish compatibility, migration, and deprecation guarantees.
- Produce signed and attested release bundles.
- Maintain external mirrors or transparency records for important releases.
- Conduct periodic privacy, integrity, security, and source-fixity audits.
- Establish independent technical and editorial governance with succession planning.
- Define sustainable funding, archival ownership, and end-of-life procedures.

## Direct Final Answers

### 1. Would I approve this repository for public release?

**No, not as an evidence platform or foundation-ready open-source project.**

I would permit publication only as a clearly labelled pre-alpha design scaffold after fixing ownership, security contact, licensing, citation metadata, and misleading readiness claims.

### 2. What prevents approval?

- Vacuous validation and untested graph integrity.
- An incoherent immutable revision model.
- No cryptographic source or release integrity.
- Incorrect claim-evidence and confidence semantics.
- Missing package, schema, and methodology version boundaries.
- Placeholder governance and security ownership.
- Inadequate privacy, confidential-source, and rights architecture.
- No operationally proven publication or query path.

### 3. What would I change before release?

I would redesign identity/versioning, claim-evidence links, confidence, and source artifacts first. Then I would build a non-vacuous validator around complete valid and invalid fixtures, establish deterministic releases, and make governance and licensing operational.

These are pre-release changes because there is currently almost no migration cost. Deferring them until after the first real dataset would turn avoidable design corrections into politically and operationally difficult data migrations.

### 4. Could this become a decade-long open-source project?

**Yes, but not on the current implementation alone.**

The mission, package concept, and evidence-first philosophy are strong enough. A decade-long project requires enforceable invariants, independent governance, preservation infrastructure, representation boundaries, and migrations, not merely extensive documentation.

### 5. What would I revisit immediately if this were my repository?

In this order:

1. YAML as canonical release format.
2. Entity identity versus immutable version identity.
3. Evidence polarity and duplicated backlinks.
4. Confidence versus dispute state.
5. Source-artifact integrity and preservation.
6. Package and release manifests.
7. Coupled versioning.
8. Governance, appeals, and reviewer independence.
9. Licensing, privacy, and confidential-source handling.
10. The claim that the existing design is already MCP-ready.

The repository has a credible purpose and a promising start. It is not yet trustworthy infrastructure.
