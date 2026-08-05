---
review_title: "Independent Architecture Review: Body of Evidence — Sixth Pass"
reviewed_at: "2026-08-05T18:09:37+10:00"
reviewed_commit: "d6209f1d81c91808b4080b6da0914167b84ac36f"
comparison_commit: "c1769406fe67bc0f6f00c92a61f01b7f5e9885f4"
review_type: "independent-principal-architect-follow-up"
review_status: "final"
verdict: "conditional-go-public-pre-alpha-no-go-evidence-release"
---

# Independent Architecture Review: Body of Evidence — Sixth Pass

## Verdict

**Public pre-alpha approved; evidence publication not approved.**

The response to the fifth pass is substantive. Apache licensing, diagnostic
identity, CLI integration coverage, Dependabot alerts, and package-root
symlink rejection are independently verified.

However, two broad claims remain overstated:

- “Every reference is package-scoped” is false. Several schema-defined
  references are not validated at all, and the stable-ID index cannot
  represent the same ID in multiple packages correctly.
- “Symlinks are rejected everywhere” is false. An unmanifested entity-file
  symlink can read content outside its package and pass every validator.

Estimated overall readiness improves from **6.4/10 to 6.6/10**. These defects
block an evidence-bearing investigation but do not prevent publication as a
clearly labelled pre-alpha.

## Review basis

This review examined commit
`d6209f1d81c91808b4080b6da0914167b84ac36f`, comparing it with the
[fifth-pass review](2026-08-05T173609+1000-independent-architecture-review-fifth-pass.md),
committed at `c176940`.

The remediation claims were treated as propositions to falsify. Review work
covered:

- Stable-ID ownership and package-order behaviour
- All schema-declared reference-bearing fields
- Package-root, manifest-path, unmanifested-file, and broken symlinks
- Structured diagnostic multiplicity and location
- The actual CLI package-discovery path and invalid-root behaviour
- Local tests, self-tests, linters, compilation, and commit hygiene
- GitHub Actions results, Apache licence recognition, and Dependabot settings
- The unchanged Edition, provenance, graph, governance, AI, and MCP architecture

CodeRabbit's optional external review pass was unavailable because its CLI was
not authenticated. Findings below come from direct code inspection, runtime
tests, adversarial probes, GitHub settings inspection, and public API results.

## Executive summary

### Verified improvements

- GitHub now recognises the repository as Apache-2.0 licensed.
- Both GitHub workflows passed on the reviewed commit.
- Dependency graph and Dependabot vulnerability alerts are enabled.
- Structured diagnostics preserve multiplicity, file identity, and field or
  entry location.
- Invalid-fixture tests compare exact, duplicate-preserving diagnostic lists.
- The real CLI discovery path has subprocess-level multi-package tests.
- A symlinked package root is rejected before entity discovery.
- General reference checks that are actually registered now compare target and
  referencing packages.
- CODEOWNERS and CITATION comments accurately describe current repository state.

### Remaining or newly demonstrated weaknesses

1. The stable-ID index is a last-writer-wins map and cannot represent package
   ownership correctly when an ID appears in more than one package.
2. Five schema-defined reference locations are absent from the reference
   validator entirely.
3. Unmanifested entity-file symlinks can escape package containment and pass all
   checks.
4. A broken unmanifested symlink crashes validation with an uncaught
   `FileNotFoundError`.
5. A nonexistent `--root` path also produces a traceback rather than a stable
   CLI diagnostic.

### Unchanged release blockers

- C-02: no immutable, content-addressed Edition
- C-03: references are not exact-version or Edition bindings
- H-04: Evidence does not bind exact Source versions, artifact bytes, and selectors
- H-03/H-07: assessment and assertion-graph semantics remain incomplete
- H-08/H-09/H-10: governance, rights, privacy, and release authority remain
  non-operational

## Remediation claim assessment

| Claim | Result | Assessment |
| --- | --- | --- |
| H-02c ordinary references package-scoped | **Partially fixed** | Covered fields are scoped, but the ID index is lossy and several reference fields are omitted entirely. |
| H-15 symlinked package roots rejected | **Verified narrowly** | Root symlinks are rejected. Unmanifested entity symlinks remain accepted. |
| H-16 Apache-2.0 recognition | **Verified** | GitHub now reports `Apache-2.0`. |
| M-07b diagnostic multiplicity/location | **Verified** | Exact duplicate-preserving `(validator, code, path, location)` assertions are implemented. |
| M-15 CLI multi-package testing | **Verified** | Three subprocess integration tests exercise actual discovery. |
| M-16 CODEOWNERS comment | **Verified** | It no longer claims an unenforced two-reviewer gate. |
| L-05 CITATION comment | **Verified** | Live repository URLs are accurately described. |
| L-06 diagnostic type hints | **Verified** | Validators now declare `List[Diagnostic]`. |
| M-17 Dependabot alerts | **Verified** | Dependency graph and Dependabot alerts are enabled; automated update PRs remain deliberately disabled. |

GitHub's [license API](https://api.github.com/repos/egarcia74/body-of-evidence/license)
reports `Apache-2.0`. Both
[Validate](https://github.com/egarcia74/body-of-evidence/actions/runs/30986938271)
and [Lint](https://github.com/egarcia74/body-of-evidence/actions/runs/30986938297)
succeeded on the reviewed commit.

## High-severity findings

### H-17 — Stable-ID ownership remains lossy

The reference index is still:

```python
id_index[data["id"]] = {"path": path, "package": package}
```

Each stable ID can retain only one owner:
[validate_references.py](../../scripts/validate_references.py#L503).

This contradicts the fixture, which deliberately places the same stable claim
ID in two packages. One entry silently overwrites the other.

The existing fixture produces:

```text
REF_WRONG_PACKAGE claim-cross-ref.yaml investigation_id
REF_WRONG_PACKAGE revision-cross-package.yaml entity_id
REVISION_ENDPOINT_WRONG_PACKAGE revision-cross-package.yaml old_version_id
```

The `revision.entity_id` error is a false positive: that stable ID is present
locally in package A, but the index resolves only package B's later entry.

More fundamentally, the architecture has not decided whether:

- A globally unique stable entity may be owned by only one package; or
- The same entity may be mirrored or imported by multiple packages.

The current implementation accidentally permits both while correctly modelling
neither.

**Required correction:** enforce one owning package per stable ID, or represent
ownership as a multimap with explicit import and dependency semantics. Never
use last-writer-wins identity resolution.

### H-18 — Schema-defined references bypass validation

The manual type switch in
[validate_references.py](../../scripts/validate_references.py#L114) does not
cover all reference-bearing schema fields.

Confirmed omissions:

- `event.investigation_ids`
- `person.investigation_ids`
- `organisation.investigation_ids`
- `relationship.investigation_ids`
- `review.specific_concerns[].referenced_entity_id`

Direct probes containing dangling values in these fields produced zero
reference diagnostics.

This means the claim that every reference is package-scoped is materially
false: these references can be dangling, wrong-type, or cross-package without
detection.

`review.subject_type` is also not checked against `subject_id`, allowing a
Review to misdeclare what kind of entity it reviewed.

**Required correction:** create a declarative reference registry containing
entity type, field path, cardinality, and expected target type. Add a test that
compares that registry against all reference-shaped schema properties so schema
evolution cannot silently bypass validation.

### H-19 — Unmanifested entity symlinks escape the package

`find_entity_files()` rejects a symlinked package root but accepts symlinked
YAML files discovered beneath a real root:
[boe_files.py](../../scripts/boe_files.py#L45).

The manifest containment check protects only files listed in `package.yaml`.
Historical versions are intentionally unlisted, so this is a real
canonical-data path.

A fresh probe created:

```text
package/claims/unlisted-external.yaml -> ../../external-claim.yaml
```

The complete CLI returned:

```text
[schema] OK
[ids] OK
[references] OK
[orphans] OK
[provenance] OK
PASSED
```

Therefore validation can consume mutable content outside the investigation
package while certifying the package as valid.

A broken unmanifested symlink instead crashes with an uncaught
`FileNotFoundError`, because `load_yaml()` catches YAML errors but not
file-system errors: [boe_files.py](../../scripts/boe_files.py#L98).

**Required correction:** reject every symlinked entity file during shared
discovery, including unmanifested historical versions, and convert file-system
failures into structured diagnostics.

## Medium-severity finding

### M-18 — `--root` has an unhandled invalid-path failure

Passing a nonexistent `--root` causes a Python traceback at
[validate.py](../../scripts/validate.py#L149), rather than a stable CLI
diagnostic.

Validate that the root exists, is a directory, and is not itself an unsafe
symlink before calling `iterdir()`.

## Architecture scorecard

| Category | Fifth pass | Sixth pass |
| --- | ---: | ---: |
| Repository architecture | 6.7 | **6.8** |
| Data model | 7.0 | **7.0** |
| Validation | 7.2 | **7.3** |
| Testing and automation | 7.0 | **7.5** |
| Documentation | 6.0 | **6.4** |
| Governance | 3.0 | **3.1** |
| Maintainability | 6.7 | **6.8** |
| Extensibility | 6.5 | **6.5** |
| AI readiness | 5.8 | **6.0** |
| MCP readiness | 4.8 | **5.0** |
| Security and integrity | 5.4 | **5.8** |
| Open-source readiness | 5.8 | **6.3** |
| **Overall readiness** | **6.4** | **6.6** |

## Architecture decision review

| Decision | Verdict |
| --- | --- |
| D-019 general package-scoped references | **Modify** — direction is correct; coverage and identity resolution remain incomplete. |
| D-019 root-symlink rejection | **Modify** — retain root rejection but extend it to every discovered entity path. |
| D-019 canonical Apache licence | **Keep** — independently verified against GitHub's detector. |
| D-019 structured diagnostic locations | **Keep** — correctly implemented. |
| D-019 CLI `--root` | **Keep and harden** — integration coverage is valuable; add input validation and JSON output. |
| D-019 Dependabot alerting | **Keep** — enabled as claimed. |
| D-016 immutable Editions | **Prioritise immediately** — still the central release architecture. |

## Technical debt register

### Critical

- **C-02:** No immutable, content-addressed Edition.
- **C-03:** References are not bound to exact versions or Editions.

### High

- **H-17:** Lossy and semantically ambiguous stable-ID package ownership.
- **H-18:** Incomplete reference-field coverage.
- **H-19:** Unmanifested entity symlinks escape package containment.
- **H-03:** Assessment graph semantics remain incomplete.
- **H-04:** Evidence lacks exact source-version, artifact-digest, and selector anchoring.
- **H-07:** Contestable assertions can bypass Claim/Assessment.
- **H-08–H-10:** Governance, rights, privacy, and release authority remain
  non-operational.

### Medium

- **M-18:** Invalid CLI roots produce tracebacks.
- Actions remain tag-pinned rather than full-SHA-pinned.
- Dependencies are pinned by version but not hash-locked.
- No stable JSON diagnostic contract.
- YAML resource limits remain absent.
- Calendar-valid date checking remains absent.

## Recommendations

### Immediate — before any evidence publication

1. Replace last-writer-wins ID resolution with an explicit ownership model.
2. Cover every schema-declared reference through a declarative registry.
3. Reject symlinks across all package content, including historical files.
4. Convert discovery and file-system failures into structured diagnostics.
5. Complete D-016: immutable Editions, canonical JSON, exact version bindings,
   and dependency Editions.
6. Implement Evidence-to-artifact digest and selector anchoring.

### Near-term — v0.2

- Add machine-readable JSON diagnostics and stable exit behaviour.
- Add schema/reference-registry completeness tests.
- Test duplicate stable IDs under both package orderings and path names.
- Add invalid-root, broken-symlink, and unmanifested-symlink fixtures.
- Pin Actions to immutable commit SHAs and hash-lock Python dependencies.

### Medium-term — v0.5

- Complete assessment and assertion graph semantics.
- Introduce an Edition-derived SQLite query representation.
- Add deterministic build and rebuild tests.
- Establish rights, privacy, takedown, appeal, and contributor-attestation
  workflows.

### Long-term — v1.0

- Signed Edition manifests and release tags.
- Independent release approval and succession governance.
- Durable package catalog and dependency resolution.
- Edition-aware MCP queries with exact provenance citations.
- Reproducibility testing across independent environments.

## Runtime verification

Fresh local verification produced:

- `pytest`: **32 passed**
- Validator self-test: **one valid and ten invalid fixture packages behaved as expected**
- Markdown lint: passed
- YAML lint: passed with configured warnings only
- Python compilation: passed
- Commit-range whitespace check: passed
- Local `HEAD`: `d6209f1d81c91808b4080b6da0914167b84ac36f`
- `origin/main`: `d6209f1d81c91808b4080b6da0914167b84ac36f`
- Worktree before this review file was created: clean

Adversarial verification additionally demonstrated:

- An unmanifested entity-file symlink outside the package passes all five checks.
- A broken unmanifested symlink crashes with `FileNotFoundError`.
- Four missing `investigation_ids` registrations return no reference diagnostics.
- The supplied cross-package fixture emits a false-positive ownership diagnostic
  for a locally present `revision.entity_id`.

## Final verdict

1. **Would I approve the repository for public release?**
   Yes, as the explicitly labelled pre-alpha it already is. No, as a trustworthy
   evidence-publishing release.

2. **What prevents full approval?**
   Immutable Editions, version-pinned references, artifact-level evidence
   provenance, complete reference semantics, and operational governance. The
   new identity and symlink defects reinforce that decision.

3. **What would I change before evidence release?**
   Fix H-17 through H-19, then implement D-016 and H-04 before accepting the
   first real investigation.

4. **Could this become a decade-long project?**
   Yes. The trajectory is credible, and the remediation discipline is unusually
   strong. It will not survive ten years if identity, release state, and
   provenance remain implicit in mutable YAML and Git history.

5. **What would I revisit immediately if this were mine?**
   The hand-maintained reference switch, the ambiguous relationship between
   globally unique IDs and package ownership, the package file-discovery trust
   boundary, and the deferred Edition design.

No repository files other than this review were changed.
