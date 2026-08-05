---
review_title: "Independent Architecture Review: Body of Evidence — Fifth Pass"
reviewed_at: "2026-08-05T17:36:09+10:00"
reviewed_commit: "ce215933d4425e4c2112a6f36ed9316f9fbb1e65"
comparison_commit: "054d2d9603dd8ec9f28c3663e4f00816a4bf27b5"
review_type: "independent-principal-architect-follow-up"
review_status: "final"
verdict: "conditional-go-public-pre-alpha-no-go-evidence-release"
---

# Independent Architecture Review: Body of Evidence — Fifth Pass

## Verdict

**The remediation is real, but three fixed claims are only partially true and the Apache licensing fix failed.**

The repository remains acceptable as a clearly labelled public pre-alpha. It is not ready for an evidence-bearing publication, a tagged stability release, foundation endorsement, or a claim of independently reproducible evidentiary integrity.

Estimated overall readiness improves from **6.2/10 to 6.4/10**. Package-scoped Revision endpoints, structured diagnostics, nested-path symlink detection, repository ownership, private security reporting, branch protection, Discussions, and public metadata are material improvements. However, package ownership has not been applied to ordinary entity references, the diagnostic tests discard multiplicity and field identity, symlinked package roots bypass containment, and GitHub still does not recognise the repository as Apache-2.0 licensed.

## Review basis

This review examined commit `ce215933d4425e4c2112a6f36ed9316f9fbb1e65`, comparing it with the [fourth-pass review](2026-08-05T164053+1000-independent-architecture-review-fourth-pass.md), committed at `054d2d9603dd8ec9f28c3663e4f00816a4bf27b5`.

The response to the fourth pass identified four remediation commits:

- `f6e9bed`: package-scoped Revisions and structured diagnostics
- `7f0f28d`: public-repository metadata and licensing changes
- `a66bdde`: correction of stale remote documentation
- `ce21593`: removal of a local filesystem path from contributor guidance

The remediation claims were treated as propositions to falsify. Review work covered:

- Cross-package Revision and general-reference behaviour
- Structured diagnostic identity, multiplicity, and test exactness
- Nested symlinks, legitimate nested paths, and symlinked package roots
- Full-suite execution and CI status
- CODEOWNERS validity
- Branch protection and required checks
- Discussions and private vulnerability reporting
- Repository description, topics, URLs, and licensing recognition
- The unchanged Edition, provenance, governance, AI, and MCP architecture

CodeRabbit's optional external review pass was unavailable because its CLI authentication had expired. The findings below come from direct code inspection, runtime tests, adversarial probes, GitHub settings inspection, and public API results.

## Executive Summary

### Material improvements

The following fixes are independently verified:

- A Revision endpoint owned by another package is rejected with `REVISION_ENDPOINT_WRONG_PACKAGE`.
- The cross-package Revision fixture produces only the intended diagnostic.
- Package-order reversal does not bypass Revision ownership.
- All five validators now return structured `Diagnostic` objects.
- Legitimate non-symlinked nested entity paths pass containment checks.
- Symlinks in nested path components are rejected, including a symlink several directories above an entity file.
- CODEOWNERS contains a valid owner and GitHub reports no parsing errors.
- Private vulnerability reporting is enabled.
- Discussions is enabled.
- `main` has the four claimed required status checks.
- Force pushes and branch deletion are disabled.
- Repository description and five topics are populated.
- Ordinary repository-link placeholders have been corrected.
- Both GitHub workflows passed at the reviewed commit.

These are substantive improvements, not documentation-only responses.

### Remaining or newly demonstrated weaknesses

The fifth pass found:

1. Stable-ID references other than Revision endpoints can still resolve across package boundaries without a declared dependency.
2. A symlinked investigation package root bypasses the no-symlink and containment policy.
3. Diagnostic-set assertions collapse duplicate diagnostics and field locations.
4. GitHub still reports the licence as `NOASSERTION` because `LICENSE` is materially different from the official Apache-2.0 text.
5. The production CLI path has not been exercised against multiple real investigations because none exist.
6. CODEOWNERS claims that schema changes require two reviewers even though one owner exists and PR review is not required.
7. CITATION metadata still describes the now-live repository URLs as placeholders.
8. Dependency graph and Dependabot alerting remain disabled.

### Unchanged release blockers

The known critical architecture remains unchanged:

- C-02: no immutable, content-addressed Edition
- C-03: references are not exact-version or Edition bindings
- H-04: Evidence does not bind exact Source versions, artifact bytes, and selectors
- H-03/H-07: assessment and assertion-graph semantics remain incomplete
- H-08/H-09/H-10: governance, rights, privacy, and release authority remain non-operational

These are acknowledged open items and are not reclassified as fifth-pass discoveries.

## Architecture Scorecard

| Category | Fourth pass | Fifth pass | Assessment |
| --- | ---: | ---: | --- |
| Repository architecture | 6.5 | **6.7** | Public configuration is stronger; package boundaries remain incompletely enforced. |
| Data model | 6.9 | **7.0** | Revision ownership improved; Edition and exact-reference identity remain absent. |
| Validation | 7.1 | **7.2** | Revision checks are stronger, but ordinary references and package-root symlinks bypass intended boundaries. |
| Testing and automation | 6.8 | **7.0** | Twenty-five tests and green CI; diagnostic assertions still lose multiplicity and location. |
| Documentation | 5.8 | **6.0** | Public links and metadata improved; licensing and review-policy comments remain inaccurate. |
| Governance | 2.7 | **3.0** | Operational repository controls exist, but human authority and two-reviewer claims do not. |
| Maintainability | 6.3 | **6.7** | Structured diagnostics are a good foundation; stable location fields and CLI contracts are absent. |
| Extensibility | 6.4 | **6.5** | Explicit package ownership is emerging; dependency semantics remain undefined. |
| AI readiness | 5.4 | **5.8** | Structured diagnostics help in-process consumers; printed CLI output remains unstructured. |
| MCP readiness | 4.5 | **4.8** | Better diagnostic and ownership primitives; deterministic Edition scope remains unavailable. |
| Security and integrity | 5.1 | **5.4** | Branch and reporting controls improved; root-symlink and dependency-supply-chain gaps remain. |
| Open-source readiness | 5.5 | **5.8** | Public pre-alpha is credible; invalid licence identification is a serious foundation blocker. |
| **Overall** | **6.2** | **6.4** | Useful remediation, with several overstated closure claims and unchanged release architecture. |

## Remediation Claim Assessment

| Claimed item | Result | Assessment |
| --- | --- | --- |
| H-02b Revision endpoints package-scoped | **Verified** | Correct under both package orders and absolute package paths. |
| Structured diagnostics | **Verified** | All validators return `Diagnostic` objects. |
| Exact fixture diagnostic sets | **Partially fixed** | Exact code sets are asserted, but multiplicity and field identity are discarded. |
| Nested symlink rejection | **Verified** | Deep parent symlinks are caught. |
| Symlink policy fully enforced | **Not fixed** | A symlinked package root is accepted and traversed. |
| CODEOWNERS invalid owner | **Verified** | GitHub reports zero CODEOWNERS errors. |
| Private security reporting | **Verified** | The setting is enabled and SECURITY points to it. |
| `main` protected | **Verified** | Four required checks; force pushes and deletion disabled. |
| Discussions | **Verified** | Enabled in repository settings and navigation. |
| Ordinary `your-org` repository URLs | **Verified** | Remaining occurrences are only the deliberately deferred schema IDs. |
| Apache-2.0 recognition | **Not fixed** | GitHub public API still reports `NOASSERTION`. |
| Repository description and topics | **Verified** | Description plus five topics are present. |

## High-Severity Findings

### General entity references are not package-scoped

The H-02b fix is valid but narrow. The version index now carries package ownership for Revision endpoints. The stable-ID index used by every other reference remains repository-global: [validate_references.py](../../scripts/validate_references.py#L434).

A direct two-package probe created:

- Package A with its own Investigation and Claim
- Package B with a different Investigation
- Package A's Claim referencing Package B's Investigation ID

The complete reference validator returned success.

The same class of cross-package resolution can affect:

- Claim to Investigation
- Evidence to Source
- Assessment to Claim or ClaimEvidenceLink
- Finding to Investigation or Claim
- Timeline to Investigation or Event
- Review to subject, Revision, or Evidence
- Relationship endpoints
- Event references
- Organisation and Source relationships

This violates the self-contained investigation-package proposal. It also creates accidental dependency semantics before the project has designed explicit dependencies.

Required correction:

1. Change the stable-ID index to retain `{path, type, package}` and all relevant versions.
2. Pass the referencing entity's package into reference checking.
3. Require the target to be owned by the same package by default.
4. Later permit cross-package references only through an explicit immutable dependency declaration.
5. Add a multi-package fixture covering ordinary references, not only Revisions.

### Symlinked package roots bypass containment

Nested component detection in [`_resolved_containment_error`](../../scripts/validate_references.py#L146) works correctly. The function begins walking at the package root but tests only components appended below it. It never checks `inv_path.is_symlink()`.

The production discovery path in [`validate.py`](../../scripts/validate.py) uses `p.is_dir()`. A symlink to a directory satisfies this predicate. A direct probe demonstrated:

```text
investigations/alias -> outside-package
alias.is_dir(): true
entity discovery: traversed alias/claims/claim.yaml
containment result: no error
```

Resolved containment does not help because the package root is resolved to the symlink target and the entity is then correctly considered a child of that resolved root.

Required correction:

- Reject an investigation root if `inv_path.is_symlink()` before file discovery.
- Apply the rule centrally in the master runner or shared package-discovery helper.
- Add a tracked or runtime-created package-root symlink fixture.
- Retain the existing component walk and resolved-containment defence.

### Apache-2.0 licensing remains invalidly represented

GitHub's repository and licence APIs both report `NOASSERTION` for the reviewed commit.

The current [LICENSE](../../LICENSE) ends at line 157. It is not merely missing the standard Appendix. A comparison with Apache's official `LICENSE-2.0.txt` found substantive textual differences in sections 4, 7, 8, and 9, followed by the omitted Appendix.

Removing the former attribution block did not make the underlying text canonical. As a result:

- GitHub does not identify the repository as Apache-2.0.
- `CITATION.cff` asserts `Apache-2.0` while the repository file is materially different.
- Automated compliance systems may treat the repository as custom or unidentified licensing.
- A major open-source foundation should not approve the repository in this state.

Required correction:

1. Replace `LICENSE` byte-for-byte with Apache's official `LICENSE-2.0.txt`.
2. Keep project attribution and informational material in `NOTICE`.
3. Verify GitHub's licence API returns `Apache-2.0`.
4. Confirm any package metadata and `CITATION.cff` use the same SPDX identity.

## Medium-Severity Findings

### Diagnostic assertions discard multiplicity and field identity

The structured `Diagnostic` object is the right direction. The fixture test, however, projects diagnostics into a Python set of `(validator, code)`: [test_validation.py](../../tests/test_validation.py#L185).

That projection discards:

- How many instances of a diagnostic occurred
- Which field or JSON pointer failed
- Which manifest entry failed
- Which exact referenced value was invalid

The existing `broken-reference` fixture emits two `REF_NOT_FOUND` diagnostics, one for `claim_id` and another for `evidence_id`. The test observes one set member. Fixing either dangling reference while leaving the other broken would still pass.

A separate direct probe demonstrated:

| Probe | Actual diagnostic count | Asserted set |
| --- | ---: | --- |
| One Revision endpoint belongs to the wrong entity | 1 | `{(references, REVISION_ENTITY_MISMATCH)}` |
| Both Revision endpoints belong to the wrong entity | 2 | `{(references, REVISION_ENTITY_MISMATCH)}` |

The response's claim of exact diagnostic-set equality is literally true but semantically insufficient.

Required correction:

- Add a structured instance location such as `field` or RFC 6901 JSON Pointer to `Diagnostic`.
- Compare an ordered list or `Counter` of `(validator, code, repository-relative path, location)`.
- Preserve multiplicity.
- Keep messages outside the stable test identity.

### Production multi-package execution remains unproven

There are zero real packages under `investigations/`. The requested production-directory scenario therefore cannot be verified against real data.

The dedicated cross-package Revision test correctly calls the core validator with two sibling roots. It does not exercise the CLI discovery route. Add a CLI-level integration test that constructs multiple sibling packages under a temporary investigations root, or add an explicit `--root` option that can be tested without mutating the repository.

### Repository policy comments overstate reality

[CODEOWNERS](../../.github/CODEOWNERS#L9) says schema changes require two reviewers. It declares only one owner, and branch protection deliberately does not require a pull request or approving review.

The owner configuration is valid, but the comment describes a control that does not exist. Change it to the present rule or implement the claimed two-reviewer process when additional maintainers exist.

### Dependency security features remain disabled

The dependency graph, Dependabot alerts, and Dependabot updates are disabled. This is not a release blocker by itself, but it weakens supply-chain visibility while GitHub Actions remain tag-pinned rather than commit-SHA-pinned.

Enable the dependency graph now. Enable Dependabot alerting and update automation when dependency-change review policy is defined.

## Low-Severity Findings

- [CITATION.cff](../../CITATION.cff#L1) says repository URLs are placeholders until a public remote exists, although the live URLs are now present.
- Type annotations in several validators still declare `List[str]` although they return `List[Diagnostic]`.
- YAML lint remains green with deliberately accepted line-length and workflow-key warnings.
- GitHub release immutability is disabled. This is reasonable before releases exist but should be enabled when Edition-based releases begin.

## Public GitHub Configuration Review

The following settings were independently inspected in the authenticated repository settings UI:

### Confirmed controls

- Repository visibility: public
- Discussions: enabled
- Private vulnerability reporting: enabled
- Secret scanning and push protection: enabled
- Branch protection rule: applies to `main`
- Required checks:
  - `Lint YAML files`
  - `Lint Markdown`
  - `Whitespace hygiene`
  - `Validation suite`
- Force pushes: disabled
- Branch deletion: disabled
- Required pull request: disabled
- Administrator enforcement: disabled

The PR and administrator choices match the response's stated solo-maintainer policy. They should be revisited when another maintainer joins.

### CI status at the reviewed commit

Both workflows passed at `ce21593`:

- [Validate workflow](https://github.com/egarcia74/body-of-evidence/actions/runs/30984661290)
- [Lint workflow](https://github.com/egarcia74/body-of-evidence/actions/runs/30984661206)

The individual required jobs all completed successfully.

### Metadata

Confirmed present:

- Public pre-alpha description
- Topics: `evidence`, `investigative-journalism`, `json-schema`, `open-source-intelligence`, `transparency`
- Valid CODEOWNERS syntax with zero GitHub errors
- Enabled Security and Discussions navigation

Not confirmed as fixed:

- Apache-2.0 licence recognition; the public API reports `NOASSERTION`

## Runtime Verification

Fresh local verification produced:

- `pytest`: **25 passed**
- Validator self-test: **one valid and nine invalid fixture packages behaved as expected**
- Markdown lint: passed
- YAML lint: passed with accepted warnings
- Python compilation: passed
- Commit-range whitespace check: passed
- Local `HEAD`: `ce215933d4425e4c2112a6f36ed9316f9fbb1e65`
- `origin/main`: `ce215933d4425e4c2112a6f36ed9316f9fbb1e65`
- Worktree before this review file was created: clean

## Architecture Decision Review

| Decision | Verdict | Fifth-pass assessment |
| --- | --- | --- |
| YAML as human authoring representation | **Keep with modification** | Continue authoring in YAML; canonicalise releases to JSON. |
| JSON Schema validation | **Keep** | Appropriate structural layer. |
| Structured Python diagnostics | **Keep and strengthen** | Add stable location, severity, details, and JSON serialization. |
| Immutable entity versions | **Keep** | Continues to be a strong foundation. |
| Explicit Revision entities | **Keep** | Package ownership is now enforced correctly. |
| Self-contained investigation packages | **Keep and enforce** | Apply package ownership to every reference and root path. |
| ULID identifiers | **Keep** | Suitable under enforced global uniqueness. |
| D-014 invalid fixtures | **Modify** | Preserve diagnostic multiplicity and field identity. |
| D-016 immutable Editions | **Keep and prioritise** | Still the central release architecture. |
| D-018 package ownership | **Modify** | Revision enforcement is correct; general references and root discovery remain. |
| Apache-2.0 | **Keep, replace file** | Use the complete official text without modifications. |
| Deferred MCP implementation | **Keep** | Correct until Edition-aware queries exist. |

## Technical Debt Register

### Critical

| ID | Debt | Consequence |
| --- | --- | --- |
| C-02 | No immutable content-addressed Edition | Publications cannot be reconstructed as self-verifying domain releases. |
| C-03 | References are not version- or Edition-pinned | Historical relationships can be reinterpreted when manifests advance. |

### High

| ID | Debt | Consequence |
| --- | --- | --- |
| H-02c | General references are not package-scoped | Undeclared cross-investigation edges validate. |
| H-15 | Symlinked package roots are accepted | Validation can traverse content outside the canonical package path. |
| H-16 | LICENSE is not canonical Apache-2.0 | GitHub and compliance tooling report `NOASSERTION`. |
| H-03 | Assessment graph semantics remain incomplete | Confidence may not reflect all supporting, contrary, or disputed evidence. |
| H-04 | Evidence lacks exact artifact anchoring | Reviewers cannot prove they examined the same source bytes. |
| H-07 | Contestable assertions can bypass Claim/Assessment | Statements may evade evidentiary review. |
| H-08..H-10 | Governance, rights, and privacy are non-operational | Human decisions and legal controls lack authority. |

### Medium

| ID | Debt | Consequence |
| --- | --- | --- |
| M-07b | Diagnostic tests collapse multiplicity and location | Fixtures may pass after partial or wrong fixes. |
| M-15 | No CLI-level multi-package integration test | Production discovery differs from tested fixture invocation. |
| M-16 | CODEOWNERS claims an absent two-reviewer rule | Contributor policy communicates false assurance. |
| M-03 | GitHub Actions are not SHA-pinned | Workflow supply-chain integrity remains mutable. |
| M-13 | No hostile-input resource limits | Pathological YAML or graphs may exhaust CI or future MCP services. |
| M-14 | No stable diagnostic JSON CLI contract | External tools cannot rely on validator output. |
| M-17 | Dependency graph and alerts are disabled | Dependency vulnerabilities are less visible. |

### Low

| ID | Debt | Consequence |
| --- | --- | --- |
| L-05 | CITATION URL placeholder comment is stale | Public metadata contradicts itself. |
| L-06 | Diagnostic type annotations are stale | Static analysis and maintainability suffer. |
| L-01 | Accepted YAML warnings remain | A green lint baseline is not warning-free. |

## Recommendations

### Immediate — before the next remediation claim

1. Replace `LICENSE` with the complete official Apache-2.0 text and verify GitHub detection.
2. Reject symlinked investigation roots before file discovery.
3. Package-scope every cross-entity reference, not only Revision endpoints.
4. Add diagnostic location fields and assert a multiplicity-preserving signature.
5. Correct the CODEOWNERS and CITATION comments.
6. Add a CLI-level multi-package integration test.
7. Enable the dependency graph.

### Near-term — v0.2

1. Design and implement D-016 as a coherent Edition and exact-reference architecture.
2. Add exact Source-version, artifact-digest, and selector anchoring.
3. Define explicit immutable package dependencies.
4. Pin GitHub Actions to complete commit SHAs.
5. Add resource limits and hostile-input tests.
6. Package a versioned validator CLI with JSON diagnostic output.
7. Decide DCO versus CLA and investigation-content licensing.

### Medium-term — v0.5

1. Generate deterministic publications from an Edition.
2. Generate a read-only SQLite or DuckDB query projection per Edition.
3. Complete assessment, contrary-evidence, and confidence-ceiling semantics.
4. Route contestable Event and Relationship assertions through Claim and Assessment semantics.
5. Establish maintainer succession, release authority, recusal, appeals, and takedown processes.

### Long-term — v1.0

1. Release an Edition-aware MCP server.
2. Scope semantic search and all retrieval to explicit Edition IDs.
3. Add signed Editions and verification tooling.
4. Add JSON-LD or RDF projections after ontology stabilisation.
5. Demonstrate migrations across several schema generations and unrelated investigations.
6. Complete external legal, security, governance, and accessibility reviews.

## Final Verdict

### 1. Would I approve this repository for public release?

**Yes, only as the explicitly labelled pre-alpha already presented.** No withdrawal is warranted.

### 2. What prevents evidence-release approval?

Immutable Editions and exact reference binding remain decisive. The newly demonstrated general cross-package reference hole, root-symlink bypass, and unidentified licence must also be corrected.

### 3. What should change before the next review?

Replace the licence, enforce package boundaries for every reference and package root, and make diagnostic assertions multiplicity- and location-aware. These are bounded corrections and should precede the larger D-016 redesign.

### 4. Could this become a decade-long open-source project?

**Yes.** The repository has strong documentation discipline, an increasingly explicit data model, executable semantic validation, real negative fixtures, and honest pre-alpha signalling. It will remain credible only if review findings are closed according to their actual invariants rather than narrower implementation interpretations.

### 5. What would I revisit immediately if this were my repository?

1. The invalid Apache licence file.
2. Package ownership across the entire graph.
3. Package-root path integrity.
4. Diagnostic identity and test exactness.
5. D-016 Edition and exact-reference architecture.
6. Evidence-to-source byte-level provenance.
7. Governance, rights, privacy, and release authority.

The trajectory remains positive. The repository is a credible pre-alpha foundation, but it is not yet an evidence platform whose integrity guarantees can be independently reproduced.
