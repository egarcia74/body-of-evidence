---
review_title: "Independent Architecture Review: Body of Evidence — Fourth Pass"
reviewed_at: "2026-08-05T16:40:53+10:00"
reviewed_commit: "44d9d9890e8e3f41fca48102f00b5efb6b70ab2b"
comparison_commit: "c6947b7dc5f6be48580ade7d9bc11c34fa9c279b"
review_type: "independent-principal-architect-follow-up"
review_status: "final"
verdict: "conditional-go-public-pre-alpha-no-go-evidence-release"
---

# Independent Architecture Review: Body of Evidence — Fourth Pass

## Verdict

**The remediation is materially successful, but the claim that all seven immediate items are closed is too strong.**

The repository may remain public as an explicitly labelled pre-alpha source and architecture preview. It should not yet publish an evidence-bearing investigation, create a tagged stability release, or seek foundation endorsement.

Estimated overall readiness improves from **5.8/10 to 6.2/10**. The original Revision-identity and missing-Investigation defects are fixed. The validation suite, CI baseline, documentation hygiene, and fixture coverage are substantially better. However, the fourth pass found a remaining cross-package Revision integrity hole and demonstrated that the fixture tests do not enforce the exact-failure guarantees claimed by D-017.

Publication also turns several previously deferred placeholders into live operational defects. Broken ownership, reporting, repository-policy, and canonical-URL metadata should now be corrected immediately, even if the project remains pre-alpha.

## Review basis

This review examined commit `44d9d9890e8e3f41fca48102f00b5efb6b70ab2b`, comparing it with the [third-pass review](2026-08-05T143653+1000-independent-architecture-review-third-pass.md), committed at `c6947b7dc5f6be48580ade7d9bc11c34fa9c279b`.

The remediation summary was treated as a set of claims to falsify, not as evidence of completion. The review covered:

- Revision endpoint identity, type, package ownership, and manifest state
- Manifest subject requirements and resolved path containment
- Negative-fixture isolation and assertion strength
- Documentation and lint hygiene
- CI and dependency integrity
- Public GitHub configuration and community health
- Licensing, security reporting, governance, and contributor routing
- The unchanged Edition, version-pinning, provenance, AI, and MCP architecture

Independent verification produced the following results:

- `python -m pytest tests/ -q`: **23 passed**.
- `python scripts/validate.py --self-test --allow-empty`: **passed** with one valid and nine invalid fixture packages.
- Markdown lint: **passed**.
- YAML lint: **passed**, with non-failing line-length and truthy-value warnings.
- Python compilation: **passed**.
- `git diff --check c6947b7..44d9d98` and `git show --check 44d9d98`: **passed**.
- `CITATION.cff` validated with `cffconvert` 1.2.0.
- The local worktree was clean and matched `origin/main` before this report was created.
- Both GitHub Actions workflows passed at the reviewed commit: [Lint](https://github.com/egarcia74/body-of-evidence/actions/runs/30979437315) and [Validate](https://github.com/egarcia74/body-of-evidence/actions/runs/30979437287).

The two direct probes reported in the third pass were replayed and now fail correctly:

1. A Revision whose endpoints belong to an unrelated entity is rejected.
2. A manifest without exactly one matching Investigation is rejected.

Additional probes found:

1. A Revision can still connect two versions held in different investigation packages when their stable ID and type match.
2. The `manifest-symlink-escape` fixture produces its intended error plus an unintended cascading error, while its test still passes.
3. A symlink in a parent directory component is accepted when its resolved target remains inside the package.

## Executive Summary

### Strengths

The fourth-pass implementation is a genuine improvement:

- Revision endpoints must now match the declared stable entity ID and entity type: [validate_references.py](../../scripts/validate_references.py#L348).
- A superseded version cannot remain current in the package manifest.
- Every manifest must contain exactly one Investigation matching `investigation_id`.
- Resolved containment blocks path escape, and a tracked symlink fixture proves the attack case.
- Nine isolated invalid packages exercise the principal semantic validators.
- Repository-wide trailing whitespace has been removed.
- Markdown and YAML linting are controlled by repository configuration and run in CI.
- The workflow includes a whitespace integrity check.
- Security, citation, versioning, and roadmap statements are more honest about current capability.
- D-017 records a defensible decision not to require every Revision's `new_version_id` to be current; such a rule would invalidate legitimate chains such as `v1 -> v2 -> v3`.
- D-016 remains correctly prioritised as a coherent Edition and reference-identity redesign rather than a series of incompatible patches.

The remediation has moved the repository from contradictory semantics toward an explicit, testable pre-alpha architecture.

### Weaknesses

The principal remaining weaknesses are:

1. Revision validation is globally indexed but not package-scoped.
2. Negative fixtures assert error-message fragments, not exact diagnostic sets.
3. The documented no-symlink rule is stricter than its implementation.
4. GitHub Actions remain tag-pinned rather than commit-SHA-pinned.
5. Public repository ownership, security reporting, links, branch policy, licensing recognition, and contributor routing are not operational.
6. There is still no immutable, content-addressed Edition.
7. References remain mutable-head lookups rather than exact version or Edition bindings.
8. Evidence is not cryptographically and structurally anchored to exact source bytes and selectors.
9. Assessment and assertion graph semantics remain under-enforced.
10. Human governance, rights, privacy, appeals, and release authority remain incomplete.

### Major risks

The primary architectural risk remains **historical reinterpretation**. A repository checkout can validate while future manifest changes alter which versions a relationship appears to reference. Until Edition identity and version-aware references exist, the platform cannot prove that a publication, review, or MCP response is being evaluated against the same body of evidence as an earlier one.

The primary immediate public-repository risk is **false operational readiness**. Contributor documentation now points real users toward owner teams, security channels, discussions, and URLs that either do not exist or are not configured.

## Architecture Scorecard

| Category | Third pass | Fourth pass | Assessment |
| --- | ---: | ---: | --- |
| Repository architecture | 6.2 | **6.5** | Layout and package boundaries are credible; public metadata and release boundaries remain incomplete. |
| Data model | 6.8 | **6.9** | Revision semantics improved; immutable Edition and exact references remain the central missing model. |
| Validation | 6.5 | **7.1** | Stronger identity and containment checks; package ownership and structured diagnostics are missing. |
| Testing and automation | 6.0 | **6.8** | Twenty-three tests and green CI are useful; substring assertions overstate fixture isolation. |
| Documentation | 5.3 | **5.8** | Hygiene and honesty improved; live placeholder URLs and policy/configuration drift remain. |
| Governance | 2.5 | **2.7** | Publication raises urgency, but ownership and human decision processes are still non-operational. |
| Maintainability | 5.8 | **6.3** | Cleaner tooling and decision records; string diagnostics and global indices will age poorly. |
| Extensibility | 6.2 | **6.4** | Package model is promising; cross-package semantics and dependency identity need design. |
| AI readiness | 5.2 | **5.4** | Structured canonical data is appropriate; agents still lack immutable query scope and stable diagnostics. |
| MCP readiness | 4.3 | **4.5** | Query primitives are plausible; deterministic Edition-aware retrieval remains impossible. |
| Security and integrity | 5.0 | **5.1** | Resolved containment is stronger; public reporting, branch policy, action pinning, and provenance remain weak. |
| Open-source readiness | 4.8 | **5.5** | Public pre-alpha is defensible; contributor-facing operations require immediate repair. |
| **Overall** | **5.8** | **6.2** | Material progress, with risk concentrated in known architecture and newly visible public operations. |

## Remediation Assessment

| Third-pass item | Status | Fourth-pass assessment |
| --- | --- | --- |
| Revision endpoint entity identity | **Resolved** | Endpoints must match `entity_id`. |
| Revision endpoint entity type | **Resolved** | Endpoint type must match `entity_type`. |
| Superseded version remains current | **Resolved** | Old version is rejected if still current. |
| Require every Revision new version to be current | **Correctly not implemented** | D-017's chain-preservation reasoning is sound. |
| Exactly one matching Investigation | **Resolved** | Missing, duplicate, or mismatched package subject is rejected. |
| Resolved path containment | **Substantially resolved** | Escape is blocked; the broader no-symlink policy is not fully enforced. |
| Exact invalid-fixture failure | **Not resolved** | Tests accept message fragments and tolerate extra errors and validators. |
| Repository hygiene | **Resolved** | Whitespace and configured linters are green. |
| Metadata drift | **Partially resolved** | Capability statements improved; public URLs and repository settings now expose additional drift. |
| C-02/C-03 Edition architecture | **Open, accepted** | Still the main evidence-release blocker. |

## Release-Blocking Architecture

### Critical: no immutable, content-addressed Edition

The repository still lacks an immutable object that binds:

- The investigation and release identity
- The exact version of every included entity
- Canonical payload digests
- Parent Edition identity
- Immutable dependency identities
- Schema and generator versions
- A release digest and optional signature

Without this object, `package.yaml` remains a mutable working-head index. Git can preserve history, but Git history is not a domain-level release contract and should not be the only way to reconstruct an evidentiary publication.

D-016 should remain the next architectural milestone. The preferred direction remains canonical JSON for hashing and interchange, with YAML retained as an authoring projection if desired. Generated Markdown should remain non-canonical.

### Critical: references are not exact version or Edition bindings

Stable IDs are appropriate for conceptual identity but insufficient for reproducibility. Historical ClaimEvidenceLinks, Assessments, Reviews, Findings, Events, and Relationships can be reinterpreted when the current manifest advances to a later version.

The model needs an explicit distinction between:

- A reference to a stable entity concept
- A reference to an immutable entity version
- A reference resolved within a declared Edition

Publication generation, peer review, and MCP responses must always declare the Edition context used to resolve stable references.

### High: Revision endpoints are not package-scoped

The version index now retains `{path, id, type}`, which fixes the previous entity-identity defect. It still lacks package identity. [`validate_revision_transition`](../../scripts/validate_references.py#L348) validates against a repository-global index and does not require the old and new endpoint paths to belong to the package containing the Revision.

A direct probe used two versions with the same stable ID and type but paths under different packages. Validation returned no errors.

This permits one investigation to claim a transition between versions owned by another package. It also creates ambiguity for future cross-package dependency support.

Required correction:

- Add package identity to every version-index entry, or pass the current package root into transition validation.
- Require both endpoints to be owned by the current package.
- Later permit cross-package references only through an explicit immutable dependency declaration, never by accidental global lookup.

### High: evidence provenance remains insufficiently anchored

Evidence still needs to identify the exact Source version, exact artifact digest, and a structured selector into those bytes. A stable Source ID plus a prose locator cannot prove that two reviewers examined the same material.

At minimum, an evidence-bearing release should bind:

- Source stable ID and version ID
- Artifact digest and media type
- Selector type and value, such as page, byte range, timestamp, or region
- Extraction/transcription method and tool version where applicable
- Transform lineage for OCR, transcription, translation, redaction, or derived media

This should be designed with the Edition architecture, not added as isolated strings.

## New Engineering Findings

### High: fixture tests do not assert exact failure semantics

[`tests/test_validation.py`](../../tests/test_validation.py#L191) stores an `expected_error_fragment` and passes when any emitted error contains that fragment. This does not prove that:

- The fixture failed only for the intended reason.
- The intended validator was the only failing validator.
- No additional regressions or cascading diagnostics occurred.
- A wording change did not accidentally satisfy the fragment.

The tracked `manifest-symlink-escape` fixture demonstrates the problem. It emits the intended symlink diagnostic and an additional `Manifest lists no Investigation entity` error. The test passes despite the extra failure.

This contradicts D-017's claim that each fixture asserts its exact intended error and cannot silently fail for the wrong reason.

Required correction:

1. Replace free-form error strings with structured diagnostics containing at least `code`, `validator`, `path`, and `message`.
2. Declare the exact expected diagnostic-code set for each fixture.
3. Assert equality of diagnostic sets, not substring membership.
4. Separate root-cause diagnostics from derived or cascading diagnostics where both are useful.

Structured diagnostics will also improve CLI stability, AI consumption, MCP error reporting, and future editor integration.

### Medium: symlink policy and implementation disagree

Resolved containment correctly rejects a path whose final resolution escapes the package. The implementation also rejects an entity file that is itself a symlink. It does not reject a symlink in a parent path component when that symlink resolves inside the package.

This is not a demonstrated traversal vulnerability: outside-root resolution remains blocked. It is a policy mismatch. The project should choose one rule and state it precisely:

- If all symlinked entity paths are prohibited, inspect every component between package root and entity file.
- If only escape is prohibited, document resolved containment as the invariant and remove the broader no-symlink claim.

The simpler long-term rule for reproducible packages is to prohibit symlinks anywhere in canonical package paths.

### Medium: CI dependencies are not immutable

GitHub Actions are referenced by release tags in [lint.yml](../../.github/workflows/lint.yml#L18) and related workflows. Tags can be moved or upstream accounts can be compromised. Evidence-integrity projects should use full commit SHAs, with version comments and automated dependency updates.

This is not unique to this repository, but the project's stated integrity standard justifies a stricter supply-chain posture before a tagged release.

### Medium: YAML lint is green but not warning-free

The repository configuration deliberately allows warnings. Current warnings include long lines and YAML 1.1 truthiness around the `on` workflow key. This is acceptable for pre-alpha CI, but documentation should say the lint baseline is non-failing rather than warning-free.

## Public Open-Source Readiness

Publication changes the priority of repository administration. These are no longer hypothetical placeholders.

### High: CODEOWNERS is invalid

[CODEOWNERS](../../.github/CODEOWNERS#L9) references `@your-org/maintainers`, which GitHub cannot resolve. The public repository currently reports multiple CODEOWNERS errors.

Until an organisation team exists, use `@egarcia74` for the owned paths. Invalid CODEOWNERS silently removes the review-routing protection the file appears to provide.

### High: the documented private security channel does not exist

[SECURITY.md](../../SECURITY.md) directs reporters toward private security reporting, but GitHub private vulnerability reporting is disabled and no security email is supplied.

Either enable private vulnerability reporting immediately or publish a monitored security contact. A public issue tracker is not an acceptable fallback for undisclosed vulnerabilities or sensitive provenance failures.

### High: `main` is unprotected

The public repository has no branch protection or ruleset for `main`. At minimum:

- Require the Lint and Validate status checks.
- Require pull requests before merge once more than one maintainer exists.
- Block force pushes and branch deletion.
- Require conversation resolution for review threads.
- Consider signed commits or signed release tags when Edition signing is introduced.

### Medium: contributor routing is broken

[CONTRIBUTING.md](../../CONTRIBUTING.md) directs contributors to GitHub Discussions, but Discussions are disabled. It also contains placeholder organisation URLs. Enable the feature or remove the guidance; do not direct contributors to a channel that does not exist.

### Medium: placeholder canonical URLs remain live

`your-org` URLs remain in CODEOWNERS, CHANGELOG, CITATION, CONTRIBUTING, README, and the schema `$id` values.

Ordinary repository links should be changed to `egarcia74/body-of-evidence` immediately. Schema identifiers require a deliberate decision: choose a stable, versioned namespace that can survive repository transfer. Do not blindly substitute the current GitHub owner if that URI is intended as a permanent schema identity.

### Medium: Apache-2.0 is not recognised by GitHub

GitHub currently reports the repository license as `Other`/`NOASSERTION`. The present LICENSE contains Apache terms but is not the conventional unmodified distribution and appends attribution material.

Use the canonical Apache License 2.0 text unmodified in `LICENSE`. Put project attribution and required notices in `NOTICE`. Confirm GitHub then detects `Apache-2.0` and that package metadata uses the same SPDX identifier.

### Medium: project-facing metadata is incomplete

The GitHub repository description is empty. Community health is reported at 85%. Before inviting contributions, add a concise description, repository topics, an explicit pre-alpha notice, and a release/readiness statement that matches this review.

## Governance, Rights, and Security

The technical controls continue to outpace the human operating model.

Before evidence publication, the project needs explicit decisions for:

- Maintainer appointment, removal, succession, and quorum
- Review authority for schemas, conclusions, security, and releases
- Conflicts of interest and recusal
- Appeals, corrections, takedowns, and contested-source handling
- DCO versus CLA for inbound contributions
- Licensing of repository code versus investigation data and third-party source material
- Privacy classification, redaction, retention, and incident response
- Release signing authority and key rotation
- Handling allegations involving living persons

Apache-2.0 is a sound code licence, but it does not resolve copyright, database rights, privacy, confidentiality, defamation, or redistribution rights for investigation content.

## AI and MCP Readiness

YAML should remain acceptable for human authoring, but should not be the only canonical release representation.

Recommended representation stack:

1. **Authoring:** YAML files optimised for reviewable diffs.
2. **Validation:** JSON Schema plus cross-entity semantic validation with structured diagnostics.
3. **Release canonicalisation:** RFC 8785 canonical JSON payloads and a content-addressed Edition manifest.
4. **Query projection:** generated SQLite or DuckDB for local analytical queries and MCP serving.
5. **Semantic projection:** optional JSON-LD contexts or RDF export after the core ontology stabilises.
6. **Publication:** generated Markdown and static web output, never canonical.

SQLite or DuckDB should be derived build artefacts rather than the collaborative source of truth. RDF should not replace the current authoring model yet; it would add ontology and tooling complexity before the project's evidentiary invariants are settled. JSON-LD export is a lower-risk path to linked-data interoperability.

An MCP server should require an Edition ID for reproducible operations and expose:

- Entity and exact-version retrieval
- Evidence-to-source traversal with artifact digest and selector
- Relationship and timeline queries
- Assessment dimensions, confidence, and dissent
- Provenance and transform lineage
- Semantic search results scoped to an Edition
- Machine-readable validation diagnostics

Without Edition scope, semantic search can answer against a moving head and produce irreproducible results.

## Architecture Decision Review

| Decision | Verdict | Fourth-pass rationale |
| --- | --- | --- |
| YAML as canonical authoring format | **Modify** | Keep for authoring; canonicalise immutable releases to JSON. |
| JSON Schema validation | **Keep** | Appropriate structural layer; semantic invariants must remain explicit code. |
| Immutable entity versions | **Keep** | The model now works and should underpin Editions. |
| Explicit Revision entities | **Keep with modification** | Valuable audit trail; add package ownership and Edition transition semantics. |
| ULID identifiers | **Keep** | Suitable if generation and global uniqueness remain enforced. |
| Self-contained investigation packages | **Keep with modification** | Make package ownership explicit and dependencies immutable. |
| Python validation | **Keep** | Practical and maintainable; stabilise diagnostics and package the CLI. |
| Apache-2.0 | **Keep, repair distribution** | Use canonical LICENSE and NOTICE; define investigation-content licensing separately. |
| Generated Markdown | **Keep** | Correctly non-canonical and reproducible from an Edition. |
| Deferred MCP implementation | **Keep** | Correct until Edition-aware retrieval semantics exist. |
| D-014 isolated fixtures | **Modify** | Require exact structured diagnostic sets, not message fragments. |
| D-016 immutable Editions | **Keep and prioritise** | Still the key release architecture. |
| D-017 Revision transition rules | **Keep with follow-up** | Identity/type and subject fixes are sound; package scope and exact-fixture claims remain incomplete. |
| Tag-pinned GitHub Actions | **Replace** | Pin full commit SHAs before release. |
| Global mutable-head lookup | **Replace** | Use exact version and Edition-aware resolution. |

## Technical Debt Register

### Critical

| ID | Debt | Consequence |
| --- | --- | --- |
| C-02 | No immutable content-addressed Edition | Historical publications cannot be reconstructed and verified as domain objects. |
| C-03 | References are not version- or Edition-pinned | Relationships can be reinterpreted as manifests advance. |

### High

| ID | Debt | Consequence |
| --- | --- | --- |
| H-02b | Revision endpoints are not package-scoped | One package can claim transitions over another package's versions. |
| H-03 | Assessment graph semantics are incomplete | Confidence may not reflect all supporting, contrary, or disputed evidence. |
| H-04 | Evidence lacks exact Source-version, digest, and selector anchoring | Reviewers cannot prove they examined the same bytes. |
| H-07 | Event and Relationship can bypass the Claim/Assessment path | Contestable assertions may avoid evidentiary review. |
| H-08 | Governance authority is non-operational | Release and dispute decisions lack legitimate ownership. |
| H-09 | Inbound and investigation-content rights are unresolved | Contribution and redistribution rights remain ambiguous. |
| H-10 | Privacy and confidential-data operations are incomplete | Sensitive investigations may create legal and safety exposure. |
| H-12 | Public security reporting channel is unavailable | Vulnerabilities and sensitive integrity defects may be disclosed publicly. |
| H-13 | Public `main` branch is unprotected | Maintainer error or compromise can bypass CI and review. |
| H-14 | CODEOWNERS is invalid | Required-review routing is illusory. |

### Medium

| ID | Debt | Consequence |
| --- | --- | --- |
| M-07 | Negative tests use substring assertions | Fixtures can fail for extra or unintended reasons. |
| M-10 | Diagnostics are unstructured strings | Tests, AI agents, editors, and MCP clients depend on unstable wording. |
| M-11 | Symlink policy exceeds implementation | Security documentation and behaviour disagree. |
| M-03 | Actions are not commit-SHA-pinned | CI supply-chain integrity is weaker than project goals imply. |
| M-09 | Placeholder URLs and repository metadata remain | Public contributors encounter broken or misleading guidance. |
| M-12 | GitHub does not detect Apache-2.0 | Automated compliance and contributor expectations are impaired. |
| M-13 | No resource limits for hostile input | Pathological YAML or graph data may exhaust CI or future MCP services. |
| M-14 | No packaged validator CLI or compatibility contract | External adopters cannot depend on stable invocation or diagnostics. |

### Low

| ID | Debt | Consequence |
| --- | --- | --- |
| L-01 | YAML lint emits accepted warnings | A nominally green baseline is not warning-free. |
| L-02 | Repository description and topics are absent | Discovery and project positioning are weaker. |
| L-03 | Schema namespace ownership is undecided | Future repository transfer may force identity migration. |
| L-04 | Fixture data remains narrow | Domain-general assumptions may go undetected. |

## Recommendations

### Immediate — while publicly visible

1. Replace live placeholder repository URLs; design the schema `$id` namespace separately.
2. Replace invalid CODEOWNERS entries with `@egarcia74` until a real maintainer team exists.
3. Enable private vulnerability reporting or publish a monitored security email.
4. Protect `main` and require the Lint and Validate checks.
5. Enable Discussions or remove all guidance that depends on it.
6. Restore standard Apache-2.0 detection using canonical `LICENSE` plus `NOTICE`.
7. Add an explicit pre-alpha notice to README and GitHub metadata.
8. Enforce package ownership for both Revision endpoints.
9. Replace substring fixture assertions with exact structured diagnostic-code sets.
10. Align the symlink policy and implementation.

### Near-term — v0.2

1. Approve and implement the D-016 Edition ADR as one coherent change.
2. Introduce version- and Edition-aware reference semantics.
3. Anchor Evidence to exact Source versions, artifact digests, and structured selectors.
4. Define package dependency identity and validation.
5. Pin GitHub Actions to full commit SHAs.
6. Add parser limits, path-count limits, file-size limits, and graph-depth limits.
7. Package the validator as a versioned CLI with stable diagnostic JSON output.
8. Decide DCO versus CLA and code versus data/content licensing.

### Medium-term — v0.5

1. Generate a read-only SQLite or DuckDB query projection per Edition.
2. Implement deterministic publication generation from an Edition.
3. Complete assessment-link ownership, contrary-evidence completeness, and confidence-ceiling rules.
4. Route contestable Event and Relationship assertions through Claim and Assessment semantics.
5. Add multi-investigation fixtures, cross-package dependencies, long revision chains, and adversarial input tests.
6. Establish maintainership, release authority, recusal, appeals, corrections, and takedown processes.
7. Add SBOM generation, dependency update automation, and signed release provenance.

### Long-term — v1.0

1. Release an Edition-aware MCP server with deterministic retrieval and provenance traversal.
2. Add semantic search scoped to explicit Edition IDs.
3. Publish JSON-LD/RDF projections after the ontology stabilises.
4. Support signed Editions, verification tooling, and key-rotation policy.
5. Demonstrate migration and archival guarantees across multiple schema generations.
6. Complete an external legal, security, accessibility, and governance review.
7. Prove the model across several unrelated investigations before declaring stability.

## Alternative Architecture

A stronger long-term architecture would preserve the repository's best idea—reviewable structured source files—while separating authoring, release, query, and publication concerns.

```text
YAML authoring files
        |
        v
structural + semantic validation
        |
        v
canonical JSON entity versions
        |
        v
content-addressed immutable Edition
        |
        +--> generated Markdown/static publication
        +--> SQLite or DuckDB query projection
        +--> MCP server and semantic index
        +--> optional JSON-LD/RDF projection
```

Key properties:

- Human contributors review YAML diffs.
- Hashes are computed over canonical JSON, not YAML serialisation.
- An Edition binds exact entity versions and dependencies.
- Every generated artefact records its Edition ID and generator version.
- SQLite or DuckDB is disposable and rebuildable, not canonical.
- MCP queries default to an explicit Edition and return exact version IDs.
- Semantic embeddings are derived, versioned, and traceable to Edition content.
- Markdown remains a publication format rather than a competing source of truth.

This architecture is more durable than choosing YAML, SQLite, RDF, or Git alone as the universal canonical representation. Each representation serves one responsibility.

## Final Verdict

### 1. Would I approve this repository for public release?

**Yes, only as an explicitly labelled pre-alpha architecture and tooling preview.** The repository is already public, and the code does not need to be withdrawn. I would not approve a tagged evidence-bearing release, a stability claim, or foundation adoption.

### 2. What prevents full approval?

The absence of immutable Editions and exact reference binding is decisive. Evidence provenance, governance, rights, privacy, and release authority are also incomplete. The new cross-package Revision defect shows that package ownership is not yet a first-class invariant.

### 3. What would I change before inviting public contributions?

Fix CODEOWNERS, security reporting, branch protection, Discussions guidance, placeholder URLs, and licence recognition. Then enforce Revision package ownership and exact structured fixture diagnostics. These are bounded changes and should not wait for the Edition redesign.

### 4. Could this realistically become a decade-long open-source project?

**Yes.** The repository now has a credible pre-alpha foundation: explicit schemas, immutable version intent, executable semantic checks, isolated fixtures, CI, decision records, and honest acknowledgement of unresolved architecture. Longevity depends on completing Edition identity before real data hardens the mutable-head assumptions and on building genuine maintainer governance before contributor scale arrives.

### 5. What would I revisit immediately if this were my repository?

I would address, in order:

1. Public repository safety and contributor-routing defects.
2. Revision package ownership and structured diagnostics.
3. The D-016 Edition and exact-reference architecture.
4. Evidence-to-source byte-level provenance.
5. Governance, rights, privacy, and release authority.
6. Only then, MCP implementation and semantic search.

The repository is progressing in the right direction. It is not yet an evidence platform; it is a promising, increasingly coherent pre-alpha foundation for one.
