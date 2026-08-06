---
review_title: "Independent Architecture Review: Body of Evidence — Eleventh Pass"
reviewed_at: "2026-08-06T16:35:46+10:00"
reviewed_commit: "c2aec89a30231acfc42c801d4b830e620d31d70e"
comparison_commit: "258e25789f1f10b134527ec328120d82d8036d54"
coderabbit_head: "c2aec89a30231acfc42c801d4b830e620d31d70e"
review_type: "independent-principal-architect-follow-up"
review_status: "final"
verdict: "conditional-go-public-pre-alpha-no-go-evidence-release"
---

# Independent Architecture Review: Body of Evidence — Eleventh Pass

## Verdict

**Public pre-alpha remains approved; evidence publication remains not
approved.**

The response to the tenth-pass review is materially successful. Internal
symlink rejection is centralized across all five validators, the historical
reference tests now exercise both current and historical source versions
across all registered fields, package discovery is shared across a complete
CLI run, and subprocess-aware coverage is reaching SonarQube Cloud.

The response nevertheless overstates `PackageDiscovery` as an immutable
validation snapshot and as a structural fix for the filesystem
time-of-check/time-of-use gap. It is a frozen wrapper around mutable lists of
paths, and callers can supply discovery data that does not correspond to the
declared investigation paths. An adversarial direct call used an empty
discovery with the known-invalid duplicate-version fixture and obtained a
successful validation result with no diagnostics.

Estimated overall readiness is **7.2/10**, up from 7.0. The implementation is
stronger, but the validation context must become internally consistent before
it is exposed through MCP or treated as a reusable public API.

## Review basis

This review examined merged response commit
`c2aec89a30231acfc42c801d4b830e620d31d70e`, comparing the combined PR #14 and
PR #15 changes with `258e25789f1f10b134527ec328120d82d8036d54`.

The review covered:

- All five standalone validators against internal symlink fixtures
- Current-source and historical-source behavior across 32 reference fields
- The stronger same-stable-ID historical-reference adversarial package
- Shared package discovery across a full validation run
- Direct-call behavior with synthetic and inconsistent discovery state
- Mutability and TOCTOU properties of `PackageDiscovery`
- Unit tests, self-test, compilation, diff hygiene, and subprocess coverage
- SonarQube Cloud quality-gate results for PR #15
- Live `main` branch-protection settings
- Authenticated CodeRabbit CLI review over the complete change range

## Executive summary

### Verified improvements

- All five standalone validators reject ordinary internal symlinks.
- Current sources enforce manifest currency across all 32 reference locations.
- Historical sources receive the intended manifest-currency exemption across
  all 32 locations.
- Historical references still receive existence, type, and package checks.
- The stronger same-stable-ID historical probe continues to pass.
- A normal full validation run calls `discover_package` once per package.
- Coverage includes CLI subprocess execution rather than reporting
  `validate.py` as unexecuted.
- Seventy-two tests pass.
- The one-valid/fourteen-invalid self-test passes.
- Local coverage is 77% overall and 64% for `validate.py`.
- SonarQube Cloud reports 98.9% new-code coverage and a passing quality gate.
- Python compilation and diff hygiene pass.

### Remaining or newly demonstrated weaknesses

1. Validator callers can provide discovery state unrelated to the requested
   package roots and obtain a vacuous successful result.
2. `PackageDiscovery` is shallowly frozen, not immutable.
3. Discovery captures paths, not the bytes subsequently validated, so the
   documented TOCTOU gap remains.
4. The single-walk regression test counts factory calls, not actual walks.
5. SonarQube, CodeRabbit, and Codacy remain non-required signals on `main`.
6. Repository documentation incorrectly says no Sonar coverage-gate condition
   exists; the live gate applies an 80% new-coverage condition.
7. GitHub CodeRabbit was again rate-limited, leaving the manual local fallback
   as the only completed automated review.

## Remediation assessment

| Finding | Result | Assessment |
| --- | --- | --- |
| M-27 centralized internal-symlink rejection | **Verified** | Every standalone validator emits its own exact `PACKAGE_SYMLINK` diagnostic. |
| M-28 historical registry coverage | **Verified** | Separate current-source and historical-source tests genuinely cover all 32 registered reference locations. |
| M-24 one discovery per complete run | **Runtime behavior verified; architectural claim overstated** | The CLI shares one discovery result, but that result is mutable and does not snapshot content. |
| L-11 documentation correction | **Verified for traversal structure** | The layout notes now describe centralized discovery and preflight. The immutability language in D-025 remains incorrect. |
| M-25 coverage input | **Verified** | Coverage XML is generated in the Sonar job and includes subprocess execution. |
| M-26 CodeRabbit rate-limit handling | **Mitigated, not closed** | A local fallback ran, but completion remains a manual convention and is not an auditable required check. |

## High-severity findings

### H-23 — Validator APIs accept inconsistent discovery state

Every `run_*_validation` function accepts both `investigation_paths` and an
optional caller-provided `discoveries`. No boundary verifies that the
discoveries contain exactly the requested roots or that their entity files
belong to those roots.

An adversarial probe constructed an empty `PackageDiscovery` for the committed
`fixtures/invalid/duplicate-version-id` package and passed it to
`run_id_validation`. The result was:

```text
passed=True, errors=[]
```

The production CLI constructs matching inputs, so this is not currently a CLI
bypass. It is nevertheless a real correctness hole in the reusable Python API
and an unsafe foundation for future MCP integration. A stale cache, incomplete
caller, or mismatched context can certify an invalid package without any
diagnostic.

Required correction:

- Replace the dual-input API with one `ValidationContext` that owns its roots
  and discoveries.
- Construct that context through one controlled factory.
- If backward compatibility requires both arguments temporarily, reject any
  missing, extra, duplicate, reordered, or mismatched root before validation.
- Add a behavioral test proving a known-invalid package cannot be hidden by an
  empty, partial, stale, or foreign discovery object.
- Make the validated context—not lists supplied independently by callers—the
  eventual MCP boundary.

## Medium-severity findings

### M-29 — The immutable snapshot and TOCTOU claims are false

`PackageDiscovery` is declared `@dataclass(frozen=True)`, but
`entity_files`, `internal_symlinks`, and `traversal_errors` are ordinary mutable
lists. The review successfully called `clear()` on `entity_files` after
construction. `frozen=True` prevents field reassignment; it does not freeze
objects stored in those fields.

More importantly, discovery stores only paths. `entities_from` subsequently
reopens each path, and manifests are also opened after discovery. A file can
therefore change type, target, or content after preflight but before or between
validator reads. One enumeration is a useful I/O optimization, but it is not
an immutable validation snapshot and does not close content-level TOCTOU.

Required correction:

- Convert all collection fields and the outer discoveries collection to
  tuples immediately.
- Describe the current object accurately as an enumeration snapshot until
  content is captured.
- For a strong integrity boundary, load each document's bytes once into an
  immutable `DiscoveredDocument` and make every validator consume the same
  bytes or parsed immutable representation.
- Capture the manifest through the same mechanism.
- Optionally retain stat metadata or a digest so post-validation publication
  can confirm it is publishing the validated bytes.

### M-30 — Quality signals are measured but not enforced

The live `main` protection rule requires only four checks:

- Lint YAML files
- Lint Markdown
- Whitespace hygiene
- Validation suite

It has `strict: false`, requires zero approving reviews, and does not require
SonarQube, CodeRabbit, or Codacy. PR #15's GitHub CodeRabbit check was green
while its status said the review was rate-limited; the local review was the
only completed CodeRabbit analysis.

SonarQube Cloud is now healthy, but the repository says no coverage
quality-gate condition exists. The live PR #15 gate includes an 80% new-code
coverage condition and passed at 98.9%. The statements in `CHANGELOG.md` and
D-024 are therefore factually incorrect, even though no local
`--cov-fail-under` was added.

Required correction:

- Correct D-024 and the changelog to distinguish repository configuration,
  the live Sonar quality gate, and branch-protection enforcement.
- Enable strict/up-to-date required checks before merging.
- Promote stable external analysis to required checks, with an explicit
  policy for fork and Dependabot runs where secrets are unavailable.
- Record local CodeRabbit fallback output in the PR when the GitHub app is
  rate-limited.
- Adopt at least one independent approval once the contributor base permits;
  zero approvals is not foundation-grade governance.

## Low-severity testing debt

### L-12 — The single-walk test does not count filesystem walks

`test_run_all_checks_walks_each_package_exactly_once` patches
`discover_package` and counts factory invocations. It would still pass if a
validator directly called `_walk_package` or one of the retained legacy
helpers.

Patch `_walk_package` itself and assert one invocation per root through a full
`run_all_checks` execution. The existing factory-call test may remain as a
wiring test, but it does not independently prove the documented I/O invariant.

## CodeRabbit disposition

CodeRabbit CLI 0.7.2 was authenticated and run in agent mode over
`258e257..c2aec89`. It completed with one major finding.

| CodeRabbit finding | Disposition |
| --- | --- |
| Return immediately from reference validation whenever preflight reports any error | **Rejected as written** |

Preflight diagnostics already make the overall result fail. Discovered
symlinks are excluded from entity reads, symlinked manifests are refused, and
unreadable descendants are absent from the enumerated file set. The validators
intentionally continue over safely discovered content to aggregate additional
diagnostics; only reference validation returning early would be inconsistent.

An early return would reduce work after a known-invalid preflight, but it would
not solve the general content-level TOCTOU issue. That broader problem is
captured in M-29. If fail-fast preflight becomes policy, it should be applied
consistently to all five validators and tested as such.

CodeRabbit did not identify H-23, shallow mutability, the content-snapshot gap,
the weak walk-count test, or the live quality-gate/branch-protection mismatch.
Automated review remains a useful second opinion, not an architectural proof.

## Architecture scorecard

| Category | Tenth pass | Eleventh pass |
| --- | ---: | ---: |
| Repository architecture | 7.0 | 7.2 |
| Data model | 7.0 | 7.0 |
| Validation | 8.0 | 8.2 |
| Testing | 8.4 | 8.7 |
| Documentation | 6.7 | 6.8 |
| Governance | 3.1 | 3.2 |
| Maintainability | 7.4 | 7.6 |
| Extensibility | 6.9 | 7.0 |
| AI readiness | 6.4 | 6.5 |
| MCP readiness | 5.4 | 5.5 |
| Open-source readiness | 7.0 | 7.2 |
| **Overall** | **7.0** | **7.2** |

## Priority recommendations

### Immediate — before exposing validation through MCP or another API

1. Close H-23 with a single self-consistent `ValidationContext`.
2. Make discovery collections genuinely immutable.
3. Correct the Sonar coverage-gate documentation.
4. Strengthen the one-walk test to count actual filesystem traversals.
5. Record an auditable CodeRabbit fallback whenever GitHub is rate-limited.

### Before publishing evidence-bearing releases

1. Complete D-016: immutable Editions, exact-version/Edition-bound references,
   and deterministic canonical release serialization.
2. Bind evidence selectors to exact artifact bytes and locations.
3. Complete assessment-graph and relationship predicate semantics.
4. Finalize governance, rights/privacy review, and contributor attestation.
5. Sign releases and publish reproducible validation outputs for the exact
   released bytes.

## Final verdict

1. **Would I approve public release?** Yes, as an explicitly pre-alpha platform
   repository with no evidence-bearing publication.
2. **What prevents evidence-release approval?** D-016, exact provenance and
   artifact anchoring, unresolved graph semantics, governance gaps, and the
   absence of a release-grade immutable validation context.
3. **What should change next?** Fix H-23 and M-29 before the discovery API
   becomes an MCP integration surface; correct the quality-gate documentation.
4. **Could this become a decade-long open-source project?** Yes. The validation
   posture is unusually strong for pre-alpha, but the identity/edition model
   and governance remain the decisive long-term risks.
5. **What would I revisit immediately?** The split between caller-supplied
   paths and discoveries, the claim that path enumeration is an immutable
   snapshot, and the still-advisory external quality controls.
