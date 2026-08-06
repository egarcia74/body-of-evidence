---
review_title: "Independent Architecture Review: Body of Evidence — Tenth Pass"
reviewed_at: "2026-08-06T10:51:43+10:00"
reviewed_commit: "258e25789f1f10b134527ec328120d82d8036d54"
comparison_commit: "4e759f1d97b7a3c63c8a11e6de0c149c89300963"
coderabbit_head: "57204b8cb555f27a46e441608848711e2506e09e"
review_type: "independent-principal-architect-follow-up"
review_status: "final"
verdict: "conditional-go-public-pre-alpha-no-go-evidence-release"
---

# Independent Architecture Review: Body of Evidence — Tenth Pass

## Verdict

**Public pre-alpha remains approved; evidence publication remains not approved.**

The response to the eighth-pass review closes the reported H-21, H-22, and
M-22 defects for their intended behavior. The subsequent PR-review follow-ups
also generalize unreadable-subtree and package-root-symlink rejection across
all five standalone validators. Those are material improvements, and their
exact runtime behavior was independently reproduced.

The response nevertheless overstates two guarantees. Internal package
symlinks are still rejected only by reference validation, so four standalone
checks certify packages that violate the repository-wide symlink prohibition.
The claimed 32-field historical-reference test does not exercise a historical
referencing entity at all: its synthetic source entity is current.

The prior ninth-pass CI findings also remain open. PR #13 was merged while
Codacy and SonarCloud were red, and the GitHub CodeRabbit check reported success
despite being rate-limited without performing a review.

Estimated overall readiness remains **7.0/10**. The validation implementation
improved, but the remaining generalization gaps and ignored red checks prevent
a further score increase.

## Review basis

This review examined merged response commit
`258e25789f1f10b134527ec328120d82d8036d54`, comparing it with
`4e759f1d97b7a3c63c8a11e6de0c149c89300963`.

The local review branch was at `57204b8`. Its Git tree hash was exactly equal
to the merged commit's tree hash (`ec8d26f6cbc0e43b379e4d658a6416bf02a4bc19`),
so runtime verification and CodeRabbit examined the content that was merged.

The review covered:

- Historical and current reference-currency behavior
- All 32 registered flat and nested reference locations
- Dangling and live package-root symlinks
- Internal file, directory, and unmanifested symlinks
- Unreadable subtrees under every standalone validator
- Package discovery reuse and traversal atomicity
- Local tests, self-test, compilation, and diff hygiene
- Final GitHub check status for PR #13
- Authenticated CodeRabbit CLI review over the complete change range

## Executive summary

### Verified improvements

- Historical source versions are exempt only from `REF_NOT_CURRENT`.
- Historical references still receive existence, type, and package checks.
- The stronger same-stable-ID historical probe passes.
- Dangling package-root symlinks reach validation and are rejected.
- All five standalone validators reject symlinked package roots.
- All five standalone validators reject unreadable descendant directories.
- Exact diagnostic tuple assertions cover the new fail-closed tests.
- The unreadable-root test determines permission behavior directly.
- Sixty-five tests pass.
- The one-valid/fourteen-invalid self-test passes.
- Python compilation and diff hygiene pass.

### Remaining or newly demonstrated weaknesses

1. Internal package symlinks are rejected only by reference validation.
2. The 32-field historical-exemption coverage claim is false.
3. Package discovery performs multiple independent filesystem walks.
4. SonarCloud has no test-coverage input and remains red.
5. Codacy remained red when PR #13 was merged.
6. GitHub CodeRabbit can report green without completing a review.
7. Repository documentation describes guarantees the code does not provide.

## Remediation assessment

| Finding | Result | Assessment |
| --- | --- | --- |
| H-21 historical-reference exemption | **Behavior verified; coverage claim overstated** | The generic implementation works, but the new registry test exercises a current source, not a historical one. |
| H-22 dangling package-root symlink | **Verified and generalized at root level** | All five standalone checks reject live and dangling package-root symlinks. |
| M-22 unreadable descendant traversal | **Verified across all validators** | Every standalone check emits `PACKAGE_SUBTREE_UNREADABLE`. Discovery is still repeated rather than shared as one result. |
| L-07 exact registry assertions | **Partially verified** | Exact assertions are present. Historical exemption is not parameterized across the registry as claimed. |
| L-08 permission skip condition | **Verified** | The test probes directory enumeration before deciding whether to skip. |

## Medium-severity findings

### M-27 — Internal package symlinks remain reference-validator-only

The response correctly propagates package-root-symlink and unreadable-subtree
diagnostics to every validator. It does not propagate the repository's
whole-package symlink prohibition.

An adversarial run used the committed
`fixtures/invalid/unmanifested-symlink` package and selected each check
individually. Results:

| Check | Result |
| --- | --- |
| `schema` | Passed |
| `ids` | Passed |
| `references` | Failed with `PACKAGE_SYMLINK` |
| `orphans` | Passed |
| `provenance` | Passed |

The four passing validators silently omit the symlinked entity through
`find_entity_files`. That is the same vacuous-success failure class addressed
for package-root symlinks and unreadable subtrees.

Required correction:

- Create one central filesystem preflight for roots, descendants, symlinks,
  and traversal errors.
- Run it independently of the selected domain check.
- Add an all-check parameterized test using an internal unmanifested symlink.
- Ensure file, directory, non-YAML, live, and dangling symlinks all fail every
  standalone invocation consistently.

### M-28 — The claimed historical registry coverage does not exist

`test_every_registered_field_enforces_currency_when_historical` places the
referencing entity's own stable ID and version in `current_maps`:

```python
current_maps = {pkg: {self_id: self_version}}
```

Consequently, `referencing_is_current` is true. The test correctly proves
that all 32 fields produce `REF_NOT_CURRENT` when a **current source** points
to a non-current target. It does not prove the H-21 exemption for a historical
source across any of those parameterized locations.

The response states that this test constructs a current/non-current pair per
registry entry and proves the historical exemption across all 32 locations.
That statement is factually incorrect.

Required correction:

- Rename the existing test to describe a current referencing entity.
- Preserve it as positive coverage for H-20 currency enforcement.
- Add a second parameterized test where the source ID/version is absent from
  the current map.
- Assert that no `REF_NOT_CURRENT` is produced for every flat and nested field.
- Continue asserting existence, type, and package diagnostics independently.

### M-24 — Package discovery still performs multiple independent walks

`_walk_package` is a shared implementation, not a shared traversal result.
Each consumer invokes it independently:

- `find_traversal_errors` walks the package.
- `find_entity_files` walks it again.
- Reference validation calls `find_all_symlinks`, producing another walk.

This creates unnecessary I/O and a time-of-check/time-of-use window where the
tree can change between security preflight and entity consumption. It also
contradicts documentation claiming the consumers share one traversal.

Required correction:

- Introduce a `PackageDiscovery` result containing files, symlinks, and errors.
- Build it once per package.
- Pass the immutable snapshot to every validator selected for that CLI run.
- Avoid recomputing discovery inside helper functions.

### M-25 — External quality enforcement remains operationally red

Final PR #13 checks show:

- Codacy Static Code Analysis: failed.
- SonarCloud Code Analysis: failed.
- Repository Markdown, YAML, validation, and whitespace checks: passed.
- SonarQube workflow execution: passed, but its external quality gate failed.

The Sonar workflow does not generate a coverage report, and
`sonar-project.properties` does not point SonarCloud at one. The resulting
0% new-code coverage is expected configuration behavior, not evidence that
tests are absent.

Required correction:

- Generate XML coverage with `pytest-cov` during the Sonar workflow.
- Configure `sonar.python.coverage.reportPaths`.
- Fix or explicitly disposition every Codacy issue.
- Decide whether external checks are gates or advisory signals.
- Do not leave advisory checks permanently red; that trains maintainers to
  ignore failures and makes real regressions indistinguishable from baseline
  noise.

### M-26 — GitHub CodeRabbit success is not proof of review

The GitHub CodeRabbit status for PR #13 is green, but the attached status says
`Review rate limited`. No GitHub-app review was performed for that run.

The authenticated local CodeRabbit review supplies useful independent evidence
for this PR, but it does not make the GitHub status semantically correct.

Required correction:

- Distinguish `review completed` from `check execution completed`.
- Require an actual review result or recorded local fallback before treating
  CodeRabbit as satisfied.
- Document the fallback in the PR when the GitHub app is rate-limited.

## Low-severity documentation debt

### L-11 — Documentation overstates traversal and diagnostic integration

`CLAUDE.md` says `symlinked_root_diagnostics` is called by all five validators.
Reference validation instead retains an inline root-symlink loop because it
also needs the filtered real-path list.

The same paragraph says `find_entity_files` and `find_all_symlinks` share one
`_walk_package` traversal. They share the function but invoke separate walks.

Correct the documentation to describe the current behavior, then replace the
repeated walks structurally under M-24.

## CodeRabbit disposition

CodeRabbit CLI 0.7.2 was authenticated and run in agent mode over
`4e759f1..57204b8`. The reviewed tree is identical to merged `258e257`.

CodeRabbit completed successfully with two minor findings:

| CodeRabbit finding | Disposition |
| --- | --- |
| `CLAUDE.md` incorrectly says `symlinked_root_diagnostics` is called by all five validators | **Accepted; included in L-11** |
| Historical registry test name and documentation contradict its current-source fixture | **Accepted, but the suggested rename is insufficient; included in M-28 with an additional required historical test** |

No CodeRabbit finding was rejected.

CodeRabbit did not identify M-27, the repeated-walk aspect of M-24, or the
governance implications of M-25/M-26. Automated review remains a second opinion,
not a substitute for adversarial runtime probes and architectural review.

## Architecture scorecard

| Category | Ninth pass | Tenth pass |
| --- | ---: | ---: |
| Repository architecture | 7.0 | 7.0 |
| Data model | 7.0 | 7.0 |
| Validation | 7.8 | 8.0 |
| Testing | 8.3 | 8.4 |
| Documentation | 6.8 | 6.7 |
| Governance | 3.3 | 3.1 |
| Maintainability | 7.4 | 7.4 |
| Extensibility | 6.9 | 6.9 |
| AI readiness | 6.4 | 6.4 |
| MCP readiness | 5.4 | 5.4 |
| Security | 6.2 | 6.4 |
| Open-source readiness | 6.7 | 6.7 |
| **Overall** | **7.0** | **7.0** |

## ADR assessment

| Decision | Recommendation | Reason |
| --- | --- | --- |
| D-023 H-21 interim historical exemption | **Keep as interim** | Behavior is generic and the stronger probe passes; D-016 remains the correct final model. |
| D-023 package-root symlink rejection | **Keep and centralize** | Root behavior is correct across all validators, but internal symlinks are inconsistent. |
| D-023 fail-closed traversal | **Keep and refactor** | All validators report errors, but one discovery snapshot should replace repeated walks. |
| D-023 registry tests | **Modify** | Preserve current-source currency coverage and add actual historical-source exemption coverage. |
| D-022 CodeRabbit governance | **Modify** | A rate-limited no-review result must not satisfy the intended review control. |
| D-022 SonarCloud informational-first | **Time-box** | Advisory baselining is reasonable briefly; persistent red status is not a sustainable operating model. |
| D-016 Editions and pinned references | **Prioritize immediately** | It remains the coherent solution for immutable release and historical graph resolution. |

## Updated technical debt register

### Critical

- **C-02:** No immutable, content-addressed Edition model.
- **C-03:** References are not bound to exact versions or Editions.

### High

- **H-03:** Graph semantics remain insufficiently constrained.
- **H-04:** Evidence provenance is not anchored to precise artifact fragments.
- **H-07:** Relationship predicates remain uncontrolled.
- **H-08–H-10:** Governance, contributor rights, and privacy controls remain
  incomplete for evidence-bearing publication.

### Medium

- **M-24:** Filesystem discovery is repeated rather than snapshotted.
- **M-25:** SonarCloud and Codacy remain red and non-gating.
- **M-26:** Rate-limited CodeRabbit runs can appear green.
- **M-27:** Internal package symlinks pass four standalone validators.
- **M-28:** Historical exemption is not parameterized across the registry.
- Hash-locked dependency installation is absent.
- The CLI lacks a stable machine-readable diagnostic contract.
- YAML resource limits are absent.
- Calendar dates receive format rather than full semantic validation.

### Low

- **L-11:** Traversal and root-diagnostic documentation is inaccurate.
- Schema `$id` values still lack an adopted stable public namespace.
- `CITATION.cff` still requires final human author metadata.

## Recommendations

### Immediate

1. Move every filesystem-integrity rule into one central preflight.
2. Reject internal package symlinks under every standalone `--check` mode.
3. Add the missing 32-field historical-source exemption test.
4. Correct the test name, docstrings, `CLAUDE.md`, and D-023 claims.
5. Generate SonarCloud coverage and resolve or disposition Codacy findings.
6. Make CodeRabbit completion distinguishable from rate limiting.

### Near-term

1. Replace repeated walks with one immutable `PackageDiscovery` result.
2. Complete D-016 as one coherent Editions and exact-reference design.
3. Promote a clean SonarCloud baseline to an enforced quality gate.
4. Define stable machine-readable validation output.

### Medium-term

1. Introduce artifact/fragment-level evidence selectors.
2. Add controlled relationship predicates and graph constraints.
3. Produce deterministic canonical JSON release artifacts.
4. Add a derived SQLite or DuckDB query index for MCP and AI consumers.

### Long-term

1. Sign immutable Edition manifests and release artifacts.
2. Establish durable contributor-rights and privacy processes.
3. Formalize long-term schema compatibility and migration guarantees.

## Final verdict

1. **Would I approve the remediation direction?** Yes.
2. **Would I approve the claim that every immediate issue is fully closed?**
   No. Internal symlink handling and historical registry coverage remain
   narrower than claimed.
3. **Would I approve merging with the observed red external checks?** No.
   PR #13 was already merged, but that should not become precedent.
4. **Could this become a decade-long open-source project?** Yes, if D-016,
   provenance anchoring, governance, and reproducible release artifacts are
   completed before evidence publication.
5. **What would I revisit immediately?** Central filesystem discovery,
   historical-reference test semantics, CI gate meaning, and the Editions
   design.

The repository is moving in the right direction, but its recurring failure
mode remains unchanged: fixes are often correct for the explicitly exercised
case while documentation claims a broader invariant. The next improvement
should make those invariants structural rather than adding another layer of
per-validator patches.
