---
review_title: "Independent Architecture Review: Body of Evidence — Eighth Pass"
reviewed_at: "2026-08-06T00:06:46+10:00"
reviewed_commit: "b712c6cc74ce397c6b4406ff95ff2a5211168f7e"
comparison_commit: "975fea114540eb8a550857638e071a6abb86a158"
coderabbit_head: "fdde1e2235ba7a3fd11e86a569ee9bb11e87a610"
review_type: "independent-principal-architect-follow-up"
review_status: "final"
verdict: "conditional-go-public-pre-alpha-no-go-evidence-release"
---

# Independent Architecture Review: Body of Evidence — Eighth Pass

## Verdict

**Public pre-alpha approved; evidence publication not approved.**

The response to the seventh-pass review materially improves manifest-current
resolution, reference-registry execution, symlink coverage, and CLI error
handling. The four stated defects are fixed for their demonstrated cases.

Two broader integrity defects remain. Current-manifest resolution is applied
to historical source versions that are intentionally outside the manifest,
making legitimate history invalid. Package discovery also filters dangling
package-root symlinks before the symlink validator can reject them.

Estimated overall readiness improves from **6.8/10 to 6.9/10**. The initial
direct-review estimate was 7.0; the independently verified CodeRabbit finding
H-22 reduces the final score by 0.1.

## Review basis

This review examined response commit
`b712c6cc74ce397c6b4406ff95ff2a5211168f7e`, comparing it with the
[seventh-pass review](2026-08-05T231136+1000-independent-architecture-review-seventh-pass.md),
committed at `975fea1`.

The direct review covered:

- Manifest-current resolution across all registered reference locations
- Current and historical entity-version semantics
- Executability and completeness of flat and nested reference registries
- File, directory, non-YAML, live, and dangling symlinks
- Traversal and permission failures at root and descendant levels
- Local tests, self-tests, compilation, lint, and diff hygiene
- GitHub Actions results on the reviewed response commit

After direct review, CodeRabbit CLI 0.7.1 was run in agent mode over the
committed range `975fea1..fdde1e2`. That range contains the reviewed
`b712c6c` remediation and a subsequent requirements-only pytest dependency
bump. Every CodeRabbit finding was independently verified and dispositioned;
its output was treated as a second opinion, not as authoritative evidence.

## Executive summary

### Verified improvements

- Manifest parsing now precedes ordinary reference validation.
- All 32 registered flat and nested reference locations enforce manifest
  currency for current graph targets.
- ClaimEvidenceLink, Assessment, and Revision references all produce
  `REF_NOT_CURRENT` when the target exists locally but is absent from the
  package manifest.
- `NESTED_REFERENCE_FIELDS` is consumed generically at runtime.
- Accessible symlinked directories and non-YAML symlinks are rejected.
- An unreadable `--root` produces a controlled diagnostic and exit code 1,
  without a traceback.
- Forty-nine tests and the one-valid/fourteen-invalid self-test pass.
- All GitHub validation and lint checks passed on the reviewed response.

### Remaining or newly demonstrated weaknesses

1. Manifest-current target rules are imposed on deliberately unmanifested
   historical source versions.
2. Dangling package-root symlinks disappear during CLI discovery before the
   symlink validator sees them.
3. An unreadable descendant directory is silently skipped by `os.walk`, so
   the validator can certify a package it did not completely inspect.
4. Two regression tests are weaker or less portable than their documented
   guarantees.

## Remediation assessment

| Finding | Result | Assessment |
| --- | --- | --- |
| H-20 manifest-current resolution | **Fixed for current graph entities; historical semantics incorrect** | Every registered reference location enforces currency, but the rule is also imposed on historical source versions. |
| M-19 executable nested registry | **Verified** | Nested runtime traversal is registry-driven and behavior-tested. |
| M-20 directory/non-YAML symlinks | **Verified for readable trees** | Accessible directory and non-YAML symlinks are rejected; unreadable subtrees remain invisible. |
| M-21 unreadable root | **Verified** | Root enumeration failure becomes a controlled error with exit code 1. |

## High-severity findings

### H-21 — Current-manifest rules invalidate legitimate history

The H-20 fix correctly requires references in the released graph to target
entities present in the current manifest. It applies that rule to every entity
file, including deliberately unmanifested historical versions.

Pass 3 iterates all discovered entities
([`validate_references.py`](../../scripts/validate_references.py#L626)), while
`check_ref` requires every target to be current
([`validate_references.py`](../../scripts/validate_references.py#L192)). The
validator never asks whether the referencing source version is itself current.

An adversarial probe added, outside the repository:

- A superseded, unmanifested ClaimEvidenceLink version.
- A retired, unmanifested Evidence entity referenced by that historical link.
- Valid current versions remaining in the manifest.

The historical link was rejected with `REF_NOT_CURRENT`.

That conflicts with the immutable-history model. A historical link must remain
able to describe what it referenced at that historical point. Otherwise valid
history becomes impossible whenever the referenced entity is later removed
entirely.

Required correction:

- Determine whether the referencing entity is current by comparing its
  `version_id` with `current_map[id]`.
- Enforce current-target resolution only for references originating in current
  entity versions.
- Validate historical files for existence, type, and package ownership without
  imposing today's manifest membership.
- Under D-016, replace that interim rule with validation against the historical
  immutable Edition that contained the source version.
- Separate current released-graph validation from repository-history integrity
  validation explicitly in code and documentation.

This is High severity because the present behavior pressures maintainers to
delete, edit, or falsely retain historical entities, directly opposing the
project's provenance and immutability principles.

### H-22 — Dangling package-root symlinks bypass validation

Default CLI discovery includes entries only when `p.is_dir()` is true
([`validate.py`](../../scripts/validate.py#L170)). A live symlink to a directory
passes that filter and is later rejected by the reference validator. A dangling
symlink returns false from `is_dir()` and is silently excluded before any
symlink policy runs.

An independently reproduced probe placed one valid package and one dangling
package-root symlink under `--root`. Reference validation reported one package,
returned success, and never mentioned the symlink.

The result is environment-dependent. A symlink can be dangling in CI, then
resolve to sensitive or unrelated content on another consumer's machine.
Passing CI therefore does not prove the published tree is safe to consume.

Required correction:

```python
if not p.name.startswith("_") and (p.is_symlink() or p.is_dir())
```

Add a CLI regression test containing a valid sibling package and a dangling
package-root symlink. The suite must fail specifically with the package-root
symlink diagnostic.

CodeRabbit identified this defect; direct reproduction confirmed it.

## Medium-severity finding

### M-22 — Unreadable subdirectories bypass whole-package traversal

`find_all_symlinks` calls `os.walk` without an `onerror` handler
([`boe_files.py`](../../scripts/boe_files.py#L123)). Python therefore silently
ignores descendant enumeration failures.

A probe placed a symlink inside an unreadable package subdirectory. Results:

- `find_all_symlinks` returned an empty list.
- Reference validation passed.
- The package was certified despite containing an uninspected subtree and a
  prohibited symlink.

Required correction:

- Treat every traversal failure as a structured validation diagnostic.
- Supply an `onerror` callback to `os.walk`, or use traversal that returns
  errors explicitly.
- Apply the same fail-closed rule to entity discovery.
- Never certify a package unless every filesystem entry was inspectable.

This finding was discovered independently and also reported as a major issue
by CodeRabbit.

## Low-severity test debt

### L-07 — Registry behavior uses membership assertions

The registry-executability test checks that the expected diagnostic tuple is
present, rather than comparing the exact, duplicate-preserving result
([`test_validation.py`](../../tests/test_validation.py#L536)). Extra or
duplicated diagnostics could therefore pass unnoticed.

Compare sorted actual and expected diagnostic tuples for every flat and nested
entry. Extend the same parameterization to prove `REF_NOT_CURRENT` across all
32 registered locations, not only `REF_NOT_FOUND`.

### L-08 — Unreadable-root test has an unreliable skip condition

The test skips only when the CLI returns zero
([`test_validation.py`](../../tests/test_validation.py#L748)). In a privileged
environment, enumeration may succeed but later validation can still return a
different non-zero error, causing the test to fail for the wrong reason.

After removing permissions, first attempt `list(unreadable.iterdir())`. Skip
when enumeration succeeds; invoke the CLI only when the local operation raises
`PermissionError`. Preserve permission restoration in `finally`.

## CodeRabbit disposition

CodeRabbit completed successfully with four findings across 17 reviewed files.

| CodeRabbit severity | Finding | Disposition |
| --- | --- | --- |
| Major | `os.walk` silently skips unreadable descendants | **Accepted; independently duplicates M-22** |
| Major | Dangling package-root symlinks are filtered before validation | **Accepted as new H-22; independently reproduced** |
| Minor | Registry behavioral assertions are not exact or duplicate-preserving | **Accepted as L-07** |
| Minor | Unreadable-root test is not portable to privileged environments | **Accepted as L-08** |

CodeRabbit did not identify H-21. This is useful evidence for the adopted
policy: automated review broadens coverage but cannot replace independent
architectural reasoning and adversarial runtime probes.

## Architecture scorecard

| Category | Seventh pass | Eighth pass |
| --- | ---: | ---: |
| Repository architecture | 6.9 | 7.0 |
| Data model | 7.0 | 7.0 |
| Validation | 7.5 | 7.7 |
| Testing | 8.0 | 8.2 |
| Documentation | 6.6 | 6.8 |
| Governance | 3.1 | 3.1 |
| Maintainability | 7.1 | 7.4 |
| Extensibility | 6.7 | 6.9 |
| AI readiness | 6.2 | 6.4 |
| MCP readiness | 5.2 | 5.4 |
| Security | 6.0 | 6.0 |
| Open-source readiness | 6.5 | 6.7 |
| **Overall** | **6.8** | **6.9** |

## ADR assessment

| Decision | Recommendation | Reason |
| --- | --- | --- |
| D-021 manifest-current resolution | **Modify** | Keep current-target enforcement for the released graph, but do not impose today's manifest on historical source versions. |
| D-021 executable nested registry | **Keep and strengthen tests** | Runtime behavior is correct; assertions should be exact and currency behavior parameterized over the whole registry. |
| D-021 whole-package symlink rejection | **Modify** | Include dangling package-root symlinks and fail closed on every traversal error. |
| D-021 CLI enumeration handling | **Keep and generalize** | Root errors are controlled; the same policy must apply recursively below the root. |
| D-016 Editions and pinned references | **Prioritize immediately** | Edition-scoped resolution is the coherent solution for both current releases and historical graphs. |

## Updated technical debt register

### Critical

- **C-02:** No immutable, content-addressed Edition.
- **C-03:** References are not exact-version or Edition bindings.

### High

- **H-21:** Current manifest currency is incorrectly imposed on historical
  source versions.
- **H-22:** Dangling package-root symlinks bypass discovery and validation.
- **H-03:** Confidence and assessment semantics remain insufficiently formal.
- **H-04:** Evidence does not bind exact Source versions, artifact bytes, and
  selectors.
- **H-07:** Assertion-graph semantics remain incomplete.
- **H-08–H-10:** Governance, rights, privacy, and release authority remain
  non-operational.

### Medium

- **M-22:** Unreadable descendants are silently skipped during filesystem
  traversal.
- GitHub Actions are not pinned by immutable commit SHA.
- Release artifact and publication hashes are not yet defined.
- Machine-readable JSON diagnostics remain absent.
- YAML parser resource limits remain absent.
- Calendar-date semantics remain under-specified.

### Low

- **L-07:** Registry behavioral tests do not assert exact diagnostics.
- **L-08:** The unreadable-root test has an unreliable privileged-environment
  skip condition.

## Recommendations

### Immediate — before an evidence-bearing release

1. Split current released-graph validation from historical-file validation.
2. Reject live and dangling package-root symlinks before directory filtering.
3. Fail closed on every recursive traversal error.
4. Add the exact H-21, H-22, and M-22 probes as regression tests.
5. Complete D-016 before adding the first real investigation dataset.

### Near-term — v0.2

1. Implement immutable Editions with exact membership and hashes.
2. Resolve historical references against their originating Edition.
3. Pin references to exact versions or Edition-resolved bindings.
4. Bind Evidence to exact Source versions, artifacts, and selectors.
5. Provide structured JSON diagnostics for CI, MCP, and agent consumers.
6. Establish operational maintainers, review authority, privacy contacts, and
   rights-handling policy.

### Medium-term — v0.5

1. Build a generated SQLite or DuckDB read model from canonical Editions.
2. Define import and cross-investigation ownership semantics.
3. Formalize assertion, disagreement, confidence, and temporal semantics.
4. Add corpus-scale, malicious-input, and reproducibility tests.

### Long-term — v1.0

1. Publish deterministic Edition artifacts and generated human-readable
   publications.
2. Expose MCP tools over the generated indexed read model.
3. Add compatibility guarantees and migrations across schema generations.
4. Operate a documented, auditable release and governance process.

## Verification evidence

The following checks and probes support this review:

- `pytest`: 49 tests passed.
- Repository self-test: one valid and fourteen invalid packages behaved as
  expected.
- Python compilation completed successfully.
- Markdown and YAML lint completed without errors.
- Diff hygiene passed.
- All 32 registered reference locations produced `REF_NOT_CURRENT` under the
  manifest-currency probe.
- ClaimEvidenceLink, Assessment, and Revision exact probes produced
  `REF_NOT_CURRENT`.
- Accessible directory and non-YAML symlinks were rejected.
- An unreadable root returned a controlled exit code 1 without a traceback.
- A historical unmanifested link referencing retired unmanifested evidence was
  incorrectly rejected with `REF_NOT_CURRENT`.
- A symlink hidden inside an unreadable descendant was not detected, and the
  package incorrectly passed reference validation.
- A dangling package-root symlink beside a valid package was not detected, and
  reference validation incorrectly passed.
- CodeRabbit completed with four findings; all four were independently
  accepted after reproduction or direct inspection.
- GitHub's
  [Validation suite](https://github.com/egarcia74/body-of-evidence/actions/runs/31011123461)
  and
  [lint workflow](https://github.com/egarcia74/body-of-evidence/actions/runs/31011123310)
  succeeded on the reviewed remediation commit.

## Final verdict

This response is materially stronger than the preceding rounds. Manifest
ordering, current-target enforcement, nested-registry execution, accessible
symlink coverage, and root-error handling are real improvements.

The remaining defects are architectural and integrity-related rather than
cosmetic. H-21 conflates current release semantics with historical audit-trail
semantics. H-22 and M-22 mean validation can certify filesystem content it did
not actually inspect or even acknowledge.

**Approve continued public development as pre-alpha. Do not approve the first
evidence-bearing investigation, a stability promise, or downstream MCP
consumption until H-21, H-22, M-22, and the D-016 Edition model are resolved.**
