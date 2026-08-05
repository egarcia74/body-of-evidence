---
review_title: "Independent Architecture Review: Body of Evidence — Seventh Pass"
reviewed_at: "2026-08-05T23:11:36+10:00"
reviewed_commit: "cc6294ede1aadf246b9e2243d3481628b9636613"
comparison_commit: "76b7c95624fc829fe376cfd0342fb4a9628e00a1"
review_type: "independent-principal-architect-follow-up"
review_status: "final"
verdict: "conditional-go-public-pre-alpha-no-go-evidence-release"
---

# Independent Architecture Review: Body of Evidence — Seventh Pass

## Verdict

**Public pre-alpha approved; evidence publication not approved.**

The exact sixth-pass probes are fixed. The broader statement that every
sixth-pass item is fully closed is still too strong.

Estimated overall readiness improves from **6.6/10 to 6.8/10**.

## Review basis

This review examined commit
`cc6294ede1aadf246b9e2243d3481628b9636613`, comparing it with the
[sixth-pass review](2026-08-05T180937+1000-independent-architecture-review-sixth-pass.md),
committed at `76b7c95`.

The remediation claims were treated as propositions to falsify. Review work
covered:

- Stable-ID resolution under duplicate IDs and reversed package order
- Every currently schema-declared reference field
- Manifest membership as the boundary of a released graph
- Working and dangling entity-file symlinks
- Directory and non-YAML symlink handling
- Invalid-root error handling
- Local tests, self-tests, linters, compilation, and commit hygiene
- GitHub Actions results on the reviewed commit

## Executive summary

This is the strongest remediation round so far:

- The original H-17 false positive is gone under both package orderings.
- All six previously omitted reference fields are now checked.
- Working and dangling entity-file symlinks are rejected.
- Common invalid `--root` inputs produce controlled errors.
- The reference registry and completeness scan are valuable structural
  improvements.
- Forty-four tests pass locally.
- Both GitHub workflows passed on `cc6294e`.

One high-severity semantic hole remains: references resolve against any
matching YAML file in the package, not against the manifest's declared current
membership. Consequently, `package.yaml` still is not actually authoritative
over the graph it claims to release.

## Remediation assessment

| Finding | Result | Assessment |
| --- | --- | --- |
| H-17 lossy stable-ID index | **Exact defect fixed; architecture incomplete** | Multimap resolution removes the false positive. Package ownership and import semantics remain undecided. |
| H-18 unchecked schema references | **Verified for current schemas** | All six omitted fields are checked, including `investigation.related_investigations`. |
| H-18 structural completeness | **Partially fixed** | Top-level fields are registry-driven; nested fields remain hardcoded despite appearing in a registry. |
| H-19 entity-file symlinks | **Verified** | Working and dangling YAML-file symlinks are rejected without crashes. |
| H-19 package-wide symlink policy | **Partially fixed** | Directory and non-YAML symlinks remain invisible. |
| M-18 invalid `--root` | **Verified for stated cases** | Missing, file, and symlink roots are handled. Other discovery errors can still traceback. |

## High-severity finding

### H-20 — References ignore manifest membership

The multimap prefers any same-package file declaring the referenced stable ID
([`validate_references.py`](../../scripts/validate_references.py#L151)).

It does not establish that the referenced entity has a current version selected
by that package's manifest. Reference validation happens against the complete
file index before manifest-derived current state is applied
([`validate_references.py`](../../scripts/validate_references.py#L556)).

An adversarial probe:

1. Copied the known-valid package.
2. Removed only the current Claim entry from `package.yaml`.
3. Left its version files unmanifested.
4. Retained the ClaimEvidenceLink, Assessment, and Revision that reference it.
5. Ran the complete CLI.

Result:

```text
[schema] OK
[ids] OK
[references] OK
[orphans] OK
[provenance] OK
PASSED
```

The released graph therefore contains links and assessments referencing a
Claim that the release manifest does not contain.

This undermines the manifest's documented role as release authority. File
presence is being treated as package membership, even though unmanifested
files deliberately represent historical or superseded versions.

Required correction:

- Parse manifests before ordinary reference validation.
- Build a per-package current-entity map.
- Require stable references to resolve through that current map, not merely
  through any file in the directory.
- Validate historical version files separately from the released graph.
- D-016 should replace this interim model with exact Edition membership and
  version-pinned resolution.

This is closely related to C-03, but it is independently fixable before the
full Edition design.

## Medium-severity findings

### M-19 — Nested reference registry is not executable

`NESTED_REFERENCE_FIELDS` is declared as though it drives validation
([`validate_references.py`](../../scripts/validate_references.py#L106)).

It is actually consumed only by tests. Runtime validation contains a hardcoded
loop for `review.specific_concerns`
([`validate_references.py`](../../scripts/validate_references.py#L209)).

A future nested reference can be added to a schema and the registry, make the
completeness test pass, and still never be executed.

Required correction:

- Give registry entries executable path metadata, expected type, and
  cardinality.
- Traverse all registered paths generically at runtime.
- Add a behavioural test that makes every registry entry dangle and proves
  that each entry produces the expected diagnostic.

### M-20 — Symlinked directories are silently accepted

A package containing `unmanifested-link -> /outside/package/entities` passed
all five validators, and entity discovery returned an empty result for that
entry. The current validator does not follow the link, but it certifies a
package containing prohibited, consumer-dependent indirection. A future
generator or MCP implementation may traverse it. Non-YAML symlinks are also
outside the present scan.

Required correction: inspect directory entries without following them and
reject every symlink in an investigation package, regardless of target type or
file extension.

### M-21 — Unreadable roots still traceback

The CLI checks whether a root exists, is a directory, and is not itself a
symlink. Enumeration failures remain uncaught. An unreadable directory
produced a `PermissionError` at
[`validate.py`](../../scripts/validate.py#L167).

Required correction: catch `OSError` around root enumeration and package
traversal, then return a stable diagnostic and non-zero exit without a
traceback.

## Architecture scorecard

| Category | Sixth pass | Seventh pass |
| --- | ---: | ---: |
| Repository architecture | 6.8 | 6.9 |
| Data model | 7.0 | 7.0 |
| Validation | 7.3 | 7.5 |
| Testing | 7.5 | 8.0 |
| Documentation | 6.4 | 6.6 |
| Governance | 3.1 | 3.1 |
| Maintainability | 6.8 | 7.1 |
| Extensibility | 6.5 | 6.7 |
| AI readiness | 6.0 | 6.2 |
| MCP readiness | 5.0 | 5.2 |
| Security | 5.8 | 6.0 |
| Open-source readiness | 6.3 | 6.5 |
| **Overall** | **6.6** | **6.8** |

## ADR assessment

| Decision | Recommendation | Reason |
| --- | --- | --- |
| D-020 multimap identity index | **Keep as an interim mechanism** | Resolve only against manifest membership, and decide global ownership and import semantics as part of D-016. |
| D-020 declarative reference registry | **Keep and strengthen** | Make nested entries executable and behaviour-tested, rather than merely discoverable by completeness tests. |
| D-020 symlink policy | **Keep and generalise** | Enforce the documented policy over every filesystem entry, not only YAML files reached by current discovery. |
| D-020 invalid-root handling | **Keep and generalise** | Convert all discovery-time `OSError` failures into stable CLI diagnostics. |
| D-016 Editions and pinned references | **Prioritise immediately** | It remains the coherent solution for release membership, identity, and reproducibility. |

## Updated technical debt register

### Critical

- **C-02:** No immutable, content-addressed Edition.
- **C-03:** References are not exact-version or Edition bindings.

### High

- **H-20:** Ordinary references ignore manifest membership.
- **H-03:** Confidence and assessment semantics remain insufficiently formal.
- **H-04:** Evidence does not bind exact Source versions, artifact bytes, and
  selectors.
- **H-07:** Assertion-graph semantics remain incomplete.
- **H-08–H-10:** Governance, rights, privacy, and release authority remain
  non-operational.

### Medium

- **M-19:** Nested registry entries are not runtime-executable.
- **M-20:** Directory and non-YAML symlinks are not rejected.
- **M-21:** Discovery-time permission and I/O errors can traceback.
- GitHub Actions are not pinned by immutable commit SHA.
- Release artifact and publication hashes are not yet defined.
- Machine-readable JSON diagnostics remain absent.
- YAML parser resource limits remain absent.
- Calendar-date semantics remain under-specified.

## Recommendations

### Immediate — before an evidence-bearing release

1. Make manifest membership authoritative for all ordinary references.
2. Convert the nested reference registry into executable traversal metadata.
3. Reject every symlink anywhere inside an investigation package.
4. Catch discovery and traversal `OSError` failures at the CLI boundary.
5. Complete D-016 before adding the first real investigation dataset.

### Near-term — v0.2

1. Implement immutable Editions with exact membership and hashes.
2. Pin references to exact entity versions or Edition-resolved bindings.
3. Bind Evidence to exact Source versions, artifacts, and selectors.
4. Provide structured JSON diagnostics for CI, MCP, and agent consumers.
5. Establish operational maintainers, review authority, privacy contacts, and
   rights-handling policy.

### Medium-term — v0.5

1. Build a generated SQLite or DuckDB read model from canonical Editions.
2. Define import and cross-investigation ownership semantics.
3. Formalise assertion, disagreement, confidence, and temporal semantics.
4. Add corpus-scale, malicious-input, and reproducibility tests.

### Long-term — v1.0

1. Publish deterministic Edition artifacts and generated human-readable
   publications.
2. Expose MCP tools over the generated indexed read model.
3. Add compatibility guarantees and migrations across schema generations.
4. Operate a documented, auditable release and governance process.

## Verification evidence

The following checks were run against the reviewed commit:

- `pytest`: 44 tests passed.
- Repository self-test: one valid and twelve invalid packages behaved as
  expected.
- Python compilation completed successfully.
- Markdown and YAML lint completed without errors.
- Diff hygiene check passed.
- The exact H-17, H-18, H-19, and M-18 probes from the sixth pass now pass.
- The manifest-membership probe incorrectly passed validation.
- The directory-symlink probe incorrectly passed validation.
- The unreadable-root probe produced a traceback.
- Local `HEAD` and `origin/main` both resolved to `cc6294e` at review time.
- GitHub's
  [Validate workflow](https://github.com/egarcia74/body-of-evidence/actions/runs/30989571426)
  and
  [Lint workflow](https://github.com/egarcia74/body-of-evidence/actions/runs/30989571421)
  both succeeded on the reviewed commit.

## Final verdict

This round is a meaningful improvement. The exact demonstrated defects were
fixed, and the registry-plus-completeness-test direction is materially better
than repeated handwritten enumeration.

The general forms of the claimed guarantees are not yet fully enforced. H-20
is the most important outstanding defect because it breaks the manifest's role
as release authority and allows a published graph to depend on entities that
the release does not contain.

**Approve continued public development as pre-alpha. Do not approve the first
evidence-bearing investigation, a stability promise, or downstream MCP
consumption until H-20 and the D-016 Edition model are resolved.**
