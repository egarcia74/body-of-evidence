# Changelog

All notable changes to Body of Evidence are documented here.

This project adheres to [Semantic Versioning](VERSIONING.md). Dates are ISO 8601.

---

## [Unreleased]

### Added — D-028 human sign-off for AI-drafted architecture decisions (2026-08-07)

- **A human must accept any ADR that changes what a release is, what "verified" means, what a reference resolves to, what identity is, or what the platform claims to guarantee.** `AI_GUIDELINES.md` exempted "schema and tooling" from its AI limits; that exemption was written when platform work meant validation scripts, and D-016 sat inside it while deciding what a release *is*. The right thing happened anyway for D-016 specifically — three options were put to the sponsor, each with a recommendation, and the sponsor chose between them — but nothing required it. The rule attaches to the *consequence* rather than to the tooling/content boundary, which thins as the platform grows. (D-028 itself was accepted differently and the two must not be read as the same: a single proposal was put with no alternatives offered, so its record says the sponsor accepted a proposal rather than chose among options)
- An ADR under the rule must record **who decided, which option they chose, when, and the scope of that acceptance** — so a reader years later can tell a human decision from an AI recommendation. An AI may not accept its own draft, nor record agreement it did not receive. D-028 states this for itself: the sponsor accepted a single proposal with no alternatives offered, which is recorded as acceptance of a proposal rather than a choice between options, because "the sponsor chose" would overstate it
- The New Investigation proposal template gains **prerequisite checks** — made by Claude Code without sponsor sign-off, on the basis that it creates no new commitment; D-028 records the attribution and the change remains open to maintainer reversal. It enforces at proposal time what `CONTRIBUTING.md` and `ETHICS.md` already prohibit: living-person subjects, personal data beyond public-interest scope, confidential or anonymity-requested material, and documents lacking redistribution rights — each failing CLOSED on "unsure" — plus source obtainability (a METHODOLOGY confidence ceiling, not a block) and the harm-versus-public-interest weighing ETHICS requires. `ROADMAP.md` has always required the H-10 privacy policy before any living-person investigation, but nothing asked the question until after work had started
- **The template is now a GitHub issue form** (`.github/ISSUE_TEMPLATE/new_investigation.yml`, replacing `new_investigation.md`), because a markdown template enforces nothing — a submitter can delete a question, and a rule with no mechanism is the failure class this repository keeps rediscovering. The four blocking checks are `required` fields that cannot be submitted blank. Scope stated honestly: **a required field forces an ANSWER, it cannot verify one.** A contributor can still answer falsely and a maintainer still reviews every proposal; this raises the floor from "skippable" to "must be answered" and must not be described as making the gate self-enforcing
- Deliberately NOT called a privacy gate: the privacy, redaction and retention policy (H-10) does not exist, so retention and redaction decisions cannot be recorded. The checks block living-person subjects rather than enabling them

### Fixed — post-merge review of D-028 (2026-08-07)

Four findings from the CodeRabbit pass that should have run before PR #19 merged (see the merge-discipline note in D-028):

- **Two of the new issue form's own required fields were vacuously required.** "Primary sources (at least 3)" and "Initial claims (2-3)" were single textareas — a textarea cannot enforce a count, so those minimums were labels rather than floors — and both were PREFILLED — sources with `1.` `2.` `3.` and claims with `1.` `2.`, each as a `value:` block — which makes a field non-empty before the submitter types anything, satisfying `required: true` with the numbering alone. The mechanism the whole markdown→issue-form conversion was about did not hold for them. Each source and each claim now has its own field — `source_1`-`source_3` and `claim_1`-`claim_2` required, `claim_3` and a free-form "further primary sources" textarea optional — which is the only shape in which the documented minimums are a floor rather than a label
- **The form collected no lead investigator**, though `CONTRIBUTING.md:32` requires "a named lead investigator" and `:101` lists its absence as grounds for rejection; the optional "I can lead this investigation myself" checkbox identifies nobody. The defect was an unasked question rather than a wrong answer, which no amount of `required: true` elsewhere would surface. Now a required `lead_investigator` field. Converting a template into an enforcing mechanism raises the cost of a MISSING field, because enforcement narrows what arrives — a submitter can no longer volunteer more than was asked — so the field list must be checked against every document stating a requirement, not just against the previous template
- "Which sources are not publicly obtainable?" was optional while the question it depends on was required — an issue form has no conditional requirement, so a "No" could arrive naming no sources, silently skipping METHODOLOGY.md's confidence ceiling. Now always required, with "N/A" documented as the answer when all sources are obtainable
- **D-016's phase list did not carry its own amendment.** PR #18's resequencing — phase 1 → pilot investigation → schema bundle preservation → phases 2-4 — reached `ROADMAP.md` and `CLAUDE.md` but never reached the ADR, which is the authoritative record. Now recorded in D-016's phasing section
- **D-028 attributed decisions to "me" and "mine"** in an ADR whose entire purpose is auditable attribution. A first-person pronoun names nobody, and in a document establishing that an AI may not accept its own draft it reads as an AI recording a decision. Attribution is now explicit (Claude Code, drafting; @egarcia74, acceptance; scope stated for each), with a drafting disclosure covering the ADR's prose and assessments

### Fixed — issue-template labels were declared but did not exist (2026-08-07)

- `new_investigation.yml` (`new-investigation`), `claim_challenge.md` (`challenge`) and `evidence_submission.md` (`evidence`) each declared a label that was absent from the repository. GitHub does not create missing labels for issue templates — it drops them silently, so every proposal, challenge and evidence submission would have arrived unlabelled and any triage filter keying on them would have matched nothing. All three labels created. Same shape as the defects the review passes keep finding in the validators: a declaration that reads as enforcement with no mechanism behind it, failing open

### Added — D-016 Edition design (2026-08-06)

- **Design ADR only; nothing implemented.** Defines immutable, content-addressed Editions as the release artifact, with `package.yaml` demoted to a mutable working head that compiles into an Edition at release time (C-02)
- Edition identity is `boe:edition:<ULID>` — preserving TERMINOLOGY.md's rule that every `boe:` id carries a ULID — with integrity supplied by a SHA-256 `content_digest` over the RFC 8785 (JCS) canonical JSON body. Editions are JSON (YAML has no canonical form) at `investigations/<slug>/editions/<ulid>.json`
- The parent pointer carries the parent's digest, making the Edition chain a hash chain — which the design is explicit detects tampering only against an independently-obtained trust anchor (a signature, or a digest published elsewhere). Without an anchor, verification proves internal consistency only, so `README.md`'s "verify that nothing has been silently changed" stays unbacked until phase 4
- **Reference resolution becomes Edition-scoped, with no change to any of the 32 reference locations** (C-03). Resolution happens within one explicitly selected Edition (or the working head) — "the Edition containing the referencing version" does not name one, since a version persists across many. Immutability is what makes a stable-id reference exact inside that context. Explicit per-reference version pins were considered and rejected — they would cascade edits through every pinning file, manufacturing entity versions. This retires D-023/H-21's interim `referencing_is_current` rule
- Single-owner stable ids plus explicit `imports` pinned to `{slug, edition_id, content_digest}`, answering D-020's open question. The design specifies removing `dependencies` in phase 3 — it is declarable today but read by no validator — rather than leaving a no-op
- The design closes D-027's content-TOCTOU IOU by having publication emit the RETAINED validated bytes (`DiscoveredDocument.raw`) rather than re-reading and comparing — a re-read is itself a race. Scoped honestly: validated bytes are published bytes; nothing is claimed about the working tree afterwards
- Signing TARGET fixed (detached `.sig` over the content digest, so re-serialisation cannot invalidate it) and identified as the trust anchor the hash chain needs. Deliberately NOT a finished envelope: algorithm, encoding, key identifier and multi-signature handling are left to phase 4; resolves the standing contradiction between `DECISIONS.md` ("must be designed together with signing") and `ROADMAP.md` ("Unprioritised / Future")
- Documents the doc corrections the design requires (Git-tag releases vs Editions in `VERSIONING.md`; five unqualified "package.yaml is the single source of truth" statements; `REPRODUCIBILITY.md`'s Git-archaeology mechanism) and one prerequisite it does NOT satisfy: superseded schema bundles are not preserved, so an Edition can name its `schema_version` but not yet resolve it to bytes

### Changed — response to post-eleventh-pass feedback (2026-08-06, D-027)

- **Removed the proof-of-walk token.** D-026 claimed a `PackageDiscovery` "cannot be fabricated" because construction required a module-private token; a leading underscore is a naming convention, not access control, and importing `boe_files._WALK_TOKEN` produced a clean pass on a known-invalid package. `validate.validate_paths(paths, schema_dir)` is now the supported programmatic entry point — it takes paths plus ordinary configuration, but no caller-supplied validation state — and `ValidationContext`/`PackageDiscovery`/`DiscoveredDocument` are documented as internal (H-24)
- **`DiscoveredDocument` holds raw bytes + a SHA-256 digest, not a shared parsed dict.** D-026 gave all five validators one mutable mapping and called it "necessarily the same bytes"; mutating it turned a failing package into a passing one, making validators *less* isolated than re-reading had. `parse()` now returns a fresh object graph per call. The guarantee is restated precisely: one filesystem read per document per run, identical bytes for every validator (checkable via `digest`), and no cross-validator interference — explicitly NOT immutability, and NOT closing TOCTOU (H-24)
- **All five per-validator `__main__` runners now refuse to run.** The D-026 signature change left `python3 scripts/validate_{schema,ids,orphans,provenance}.py` crashing on startup, undetected because nothing ran them. They were redundant with `validate.py --check <name>`, and each duplicated discovery with a weaker `p.is_dir()` filter (the D-023/H-22 dangling-symlink blindness) and no empty-run guard. They print the supported command and exit non-zero rather than being deleted — simply deleting them made those commands exit 0 in silence, a quieter failure than the crash. Every supported CLI invocation, and every refusal, now has subprocess smoke coverage (M-31)
- `validate_paths` fails closed on an empty run (no paths, or an empty check selection) unless `allow_empty=True` — the supported API must not answer "passed" for validating nothing (invariant 10)
- `load_yaml` now reads bytes and delegates to `parse_yaml_bytes` rather than `open(path)`, whose default encoding is locale-dependent — the two could otherwise decode the same file differently
- Document content is read with `O_NOFOLLOW`, so a path swapped for a symlink after discovery enumerated it is refused rather than followed outside the package — hardening that narrows the read-side window, explicitly NOT a TOCTOU fix (which remains D-016's)
- New `fixtures/invalid/manifest-path-not-an-entity` (fifteenth invalid fixture) pins `MANIFEST_PATH_NOT_AN_ENTITY` in the self-test, not only in a tmp_path test
- `ValidationContext.for_paths` deduplicates repeated roots, so `validate_paths([pkg, pkg], ...)` returns a structured result instead of raising `ValueError` out of the supported API; the constructor's duplicate-root check remains for direct construction
- `validate_paths`' empty-run error is a structured `Diagnostic` (`EMPTY_RUN`), not a bare string — every other entry in `results` carries Diagnostics
- 124 tests (was 95)

### Changed — response to eleventh-pass review (2026-08-06, D-026)

- **Breaking (internal Python API):** every `run_*_validation` function now takes a single `context: ValidationContext` instead of `investigation_paths` plus an optional `discoveries` list. The two inputs were never reconciled, and an empty discovery paired with a known-invalid package root returned `passed=True, errors=[]` — a vacuous pass. `ValidationContext.roots` is DERIVED from its discoveries, so roots and discovery cannot disagree; `ValidationContext.for_paths()` is the single factory (H-23)
- A `PackageDiscovery` can no longer be fabricated: construction requires a private proof-of-walk token held only by `discover_package`, so no caller can assert that a package is empty (or contains something it does not) without having actually walked it. Contained beneath that: documents and symlinks must lie inside the discovery's own root, a symlinked-root discovery must be empty, and a context rejects duplicate roots (H-23)
- `PackageDiscovery`'s collection fields are now genuinely immutable tuples, type-checked at construction — `frozen=True` alone left them ordinary mutable lists, and the reviewer demonstrated it by calling `.clear()` on one (M-29)
- Document content is read and parsed ONCE per run, into the new `DiscoveredDocument`, and shared by every validator — including manifests and manifest-listed entity files, which were previously re-opened. Five validators re-reading the same paths could each observe different bytes; they now necessarily inspect identical content. This is documented as an enumeration-and-content snapshot, NOT as closing time-of-check/time-of-use against the filesystem, which needs content digests re-checked at publication (deferred to D-016) (M-29)
- `test_run_all_checks_walks_each_package_exactly_once` now patches `_walk_package` — the only function that touches the directory tree — instead of counting `discover_package` factory calls, so reaching past the factory to a retained `find_*` primitive would fail it; a second test asserts one walk per root across two packages (L-12)
- Corrected the D-024/`CHANGELOG` claim that no SonarQube Cloud quality-gate coverage condition existed: the live built-in "Sonar way" gate applies `new_coverage < 80%`. Repository configuration, the live gate, and branch-protection enforcement are now stated as three separate things (M-30)
- Corrected D-025's "one immutable result" and time-of-check/time-of-use claims in place, with the reason each was wrong (M-29)
- New `MANIFEST_PATH_NOT_AN_ENTITY` diagnostic: a manifest entry whose path exists but is not a discovered entity document (a directory, or `package.yaml` itself) is now reported instead of silently skipping the entry's id/version_id checks — a fail-open regression introduced by serving manifest-listed files from the shared context, caught by the local CodeRabbit pass before push
- 95 tests (was 72)

### Changed — response to tenth-pass review (2026-08-06, D-025)

- `boe_files.py` gained `PackageDiscovery`/`discover_packages`: each package root is now walked exactly ONCE per validation run — `validate.py`'s `run_all_checks` builds the discovery once and threads it through every `run_*_validation(..., discoveries=...)` call — producing entity files, internal symlinks, and traversal errors together, instead of `find_entity_files`/`find_all_symlinks`/`find_traversal_errors` each independently re-walking the same tree per validator (M-24; a same-day local CodeRabbit pass caught that the first version of this fix still walked each package once per validator rather than once per run — `test_run_all_checks_walks_each_package_exactly_once` now proves the full-run guarantee directly)
- `preflight_diagnostics` (replacing `symlinked_root_diagnostics`/`traversal_error_diagnostics`) now emits `PACKAGE_SYMLINK` for an ordinary internal symlink from all five validators, not just `references` — `schema`/`ids`/`orphans`/`provenance` previously passed vacuously on a package containing an unmanifested internal symlink (M-27)
- A new parameterized test (`test_every_single_check_fails_closed_on_internal_symlink`) and four extended `TestInvalidFixtures` expectations (`manifest-symlink-escape`, `unmanifested-symlink`, `broken-unmanifested-symlink`, `symlinked-subdirectory`) prove the M-27 fix across all five validators
- Renamed the historical-registry test to `test_every_registered_field_enforces_currency_when_source_is_current` (it never actually exercised a historical source, despite its old name/docstring claiming otherwise) and added `test_every_registered_field_exempts_historical_source_from_currency`, which does — a historical referencing entity pointing at an existing-but-non-current target must produce NO diagnostics, parameterized across all 32 registered reference locations (M-28)
- Corrected `CLAUDE.md`'s `scripts/boe_files.py` layout note, which claimed `find_entity_files`/`find_all_symlinks` shared one traversal (they shared a function, not a walk) and didn't mention the new centralized discovery/preflight mechanism (L-11)
- 72 tests (was 65)

### Added — pytest coverage tooling (2026-08-06, D-024)

- `pytest-cov==7.1.0` added to `scripts/requirements.txt`; both `validate-schema.yml` and `sonarcloud.yml` now run `pytest --cov=scripts --cov-report=xml --cov-report=term-missing`, producing `coverage.xml`
- `sonar-project.properties` now sets `sonar.python.coverage.reportPaths=coverage.xml`, so SonarQube Cloud's previously-unconditional `new_coverage: 0%` reflects real coverage data instead of the absence of any report
- Subprocess coverage measurement wired in (`.coveragerc` with `parallel = true`, `.github/coverage-subprocess/sitecustomize.py`, `COVERAGE_PROCESS_START`/`PYTHONPATH` set for the test step in both workflows) so the CLI-level tests that spawn `scripts/validate.py` as a real subprocess are actually measured — without it, `validate.py` reported 0% despite having dedicated CLI tests; verified locally to go from 0% to 63% (repo total 67% to 76%)
- No coverage threshold added *by this repository* (no `--cov-fail-under` in CI, no custom SonarQube Cloud quality gate) — this change produces and surfaces accurate coverage data; setting our own bar is a separate future decision once a baseline exists. **Corrected 2026-08-06 (eleventh-pass review M-30):** this bullet previously said no SonarQube Cloud quality-gate coverage condition existed at all, which was wrong — the project uses SonarQube Cloud's built-in "Sonar way" gate, which *does* apply `new_coverage < 80%` as a failing condition. That condition was failing (0%) before this change and passed at 98.9% on PR #15 afterwards. What is true is that we added no condition of our own, and that the Sonar gate is not a required check on `main` (D-022), so it does not block merges either way
- Scoped independently of the concurrent architecture-review remediation branch by deliberate choice — see D-024
- Two CodeRabbit nitpicks addressed post-merge (`068b414`): the documented local coverage command now sets `COVERAGE_PROCESS_START`/`PYTHONPATH` so it actually reproduces CI's subprocess coverage; both coverage-producing CI steps now verify `coverage.xml` was actually generated (`test -s`, not an XML parse — the file is CI's own output, not external input) before continuing

### Changed — response to eighth-pass review (2026-08-06, D-023)

- The manifest-currency rule (H-20/D-021) now applies only to references made BY a current entity version — a historical/superseded referencing file is exempt from `REF_NOT_CURRENT` (still checked for `REF_NOT_FOUND`/`REF_TYPE_MISMATCH`/`REF_WRONG_PACKAGE`), so valid history stops becoming invalid whenever the referenced entity is later retired entirely (H-21)
- `validate.py`'s default package discovery and `--investigation` path resolution now include symlinks even when dangling (`p.is_symlink() or p.is_dir()` instead of `p.is_dir()` alone), so a dangling package-root symlink reaches the symlink validator instead of silently vanishing before it ever runs (H-22)
- `boe_files` traversal (`find_entity_files`, `find_all_symlinks`) is now a single shared `os.walk(onerror=...)`-based walk; a new `find_traversal_errors` surfaces any subdirectory that could not be listed. `traversal_error_diagnostics` turns that into a failing `PACKAGE_SUBTREE_UNREADABLE` diagnostic in ALL FIVE validators (not just references, per a pre-merge automated-review follow-up), so a standalone `--check schema`/`ids`/`orphans`/`provenance` run also fails closed instead of silently certifying a package part of which was never inspected (M-22)
- The same gap existed for a symlinked package ROOT: only `references` reported `INVESTIGATION_ROOT_SYMLINK` explicitly; the other four validators saw zero files and passed vacuously. A new `symlinked_root_diagnostics` closes it for all five (M-22 follow-up, found by CodeRabbit on this PR)
- Registry behavioral tests now assert exact diagnostic lists instead of membership, and a new test parameterizes `REF_NOT_CURRENT` (not just `REF_NOT_FOUND`) across all registered reference locations (L-07)
- The unreadable-root CLI test's skip condition now checks `iterdir()` directly instead of the CLI's exit code, so it can no longer skip for the wrong reason in a privileged environment (L-08)
- SonarCloud's flagged unused-parameter and test/style findings addressed: removed genuinely-unused `label`/`id_index`/`version_index` parameters; split three composite test assertions; merged a nested `if`; the four `schema_dir` parameters required by `run_all_checks`'s uniform dispatch signature are marked accepted in SonarCloud rather than removed
- Fixed a Codacy-flagged unsorted import in `validate_references.py`
- 65 tests (was 49)

### Added — CI/PR quality gates (2026-08-06, D-022)

- `main` now requires pull requests (branch protection, `enforce_admins: true` — no owner bypass); direct pushes are no longer possible
- CodeRabbit GitHub App authorized on all repos; every PR now gets an automatic review in addition to the pre-existing local `/code-review` pre-push check
- SonarQube Cloud wired into CI (`.github/workflows/sonarcloud.yml`, `sonar-project.properties`); scans `scripts/` and `tests/`, excludes `fixtures/`/`examples/` (deliberately-invalid/generated content); quality gate result is reported but not yet a required check (no scan baseline exists yet)
- Dependabot version updates enabled (`.github/dependabot.yml`, weekly) for pip (`scripts/requirements.txt`) and GitHub Actions versions, on top of the pre-existing vulnerability alerts

### Changed — response to seventh-pass review (2026-08-05, D-021)

- References must now resolve against each package's manifest CURRENT-entity map, not merely against "a file with this id exists somewhere in the package" — manifests are parsed before ordinary reference validation runs; a reference to an unmanifested/superseded entity now fails with `REF_NOT_CURRENT`
- `NESTED_REFERENCE_FIELDS` is now executable (generic runtime traversal), not just descriptive metadata for a completeness test — the previously-hardcoded `review.specific_concerns` loop is gone; a new behavioural test dangles every registry entry, flat and nested, and asserts each one is actually checked
- Symlink rejection now covers every filesystem entry in a package (directories, non-YAML files), not only `*.yaml`/`*.yml` files — `boe_files.find_all_symlinks` replaces the narrower scan; diagnostic code renamed `ENTITY_FILE_SYMLINK` -> `PACKAGE_SYMLINK`
- `validate.py`'s investigation-path enumeration now catches `OSError` (e.g. an unreadable directory) and reports a diagnostic instead of a traceback
- 49 tests (was 44)

### Changed — response to sixth-pass review (2026-08-05, D-020)

- `id_index` is now a multimap (stable id -> list of owning files/packages), not a lossy single-owner map; a reference resolvable within the referencing entity's own package is preferred over a same-id entry in another package, fixing a false-positive `REF_WRONG_PACKAGE` the D-019 test fixture itself was producing
- Reference checking is now driven by a declarative `REFERENCE_FIELDS`/`NESTED_REFERENCE_FIELDS` registry instead of a hand-maintained dispatch; five previously-unchecked schema fields (`event`/`person`/`organisation`/`relationship.investigation_ids`, `review.specific_concerns[].referenced_entity_id`) are now validated, plus a sixth (`investigation.related_investigations`) found by the new completeness test that scans every schema for reference-shaped fields and asserts the registry matches exactly
- Symlinked entity files (and a symlinked `package.yaml` itself) are now rejected everywhere, not only symlinked package roots or manifest-listed paths — closes the gap where an unmanifested historical-version symlink could read content from outside the package, or crash validation if broken
- `load_yaml` now catches filesystem errors (e.g. a dangling symlink) as a diagnostic instead of an uncaught exception
- `validate.py --root` now validates the path exists, isn't a symlink, and is a directory before use, instead of crashing
- 44 tests (was 32)

### Changed — response to fifth-pass review (2026-08-05, D-019)

- Package-scoping now applies to EVERY cross-entity reference (claim→investigation, evidence→source, assessment→claim, etc.), not only Revision endpoints; a reference crossing a package boundary is rejected (`REF_WRONG_PACKAGE`) by default until an explicit dependency-declaration mechanism exists
- A symlinked investigation package ROOT (not just a symlinked entity path inside one) is now rejected before any file discovery, everywhere — `boe_files.find_entity_files`/`find_manifest` refuse to descend into one, `references` reports the precise cause
- `LICENSE` replaced with the byte-for-byte official Apache-2.0 text (the previous "fix" only removed an appended block; the surrounding text itself was a paraphrase, which is why GitHub kept reporting `NOASSERTION`)
- `Diagnostic` gained a `location` field; invalid-fixture tests now assert an exact, duplicate-preserving list of `(validator, code, path, location)`, not a deduplicating set — closes the gap where a fixture with two intended defects could pass after fixing only one
- `validate.py --root` added so the actual CLI multi-package discovery path can be tested against a throwaway directory; new subprocess-level integration tests cover a valid package, a cross-package reference, and a symlinked sibling package
- CODEOWNERS and CITATION.cff comments corrected to describe actual repository state
- Dependabot vulnerability alerts enabled
- 32 tests (was 25)

### Changed — response to fourth-pass review (2026-08-05, D-018)

- All validators now emit structured diagnostics (`code`, `validator`, `path`, `message`) instead of free-form strings; fixture tests assert the exact `(validator, code)` set per invalid fixture across all checks, not a substring in one named check (the tracked manifest-symlink-escape fixture's previously-unnoticed second diagnostic is now declared explicitly)
- Revision transition validation is now package-scoped: an endpoint version file owned by a different package than the Revision itself is rejected (new `REVISION_ENDPOINT_WRONG_PACKAGE` diagnostic), proven by a dedicated two-package fixture pair validated together
- Manifest path containment now rejects a symlink anywhere between the package root and the entity file, not just the final path component, matching the documented no-symlink policy
- 25 tests (was 23)

### Changed — response to third-pass review (2026-08-05, D-017)

- Revision transition validation: endpoints must belong to the revised entity and match its type; superseded versions cannot remain current (rich version index replaces the lossy one — the reviewer's unrelated-endpoints probe now fails as intended)
- Manifests must list exactly one Investigation entity matching investigation_id (the omission probe now fails as intended)
- Manifest containment is resolved, not lexical: symlinked entity paths rejected, resolved targets must stay under the package root
- Three new isolated invalid fixtures (revision-unrelated-endpoints, manifest-no-investigation, manifest-symlink-escape); fixture tests assert exact intended errors, not just failing-validator membership; 23 tests
- Green hygiene baseline: trailing whitespace stripped repo-wide, deliberate documented lint policies (.markdownlint.jsonc, .yamllint) verified green locally, CI uses repo configs plus a whitespace check
- Metadata drift reconciled: SECURITY support statement, CITATION.cff version/authors note, VERSIONING schema-preservation claim softened to planned, ROADMAP resequenced (D-016 editions before first investigations)

### Changed — response to second-pass review (2026-08-05, D-015)

- FIXED the release-blocking versioning contradiction: repeated stable ids across version files now validate (that IS the model); version_ids globally unique; (id, version_id) pairs unique; one current version per id enforced on the manifest
- Manifests now mandatory; path containment, existence, id/version match, entry uniqueness, slug and investigation_id consistency all enforced
- Revision old/new version_ids + revision_type required; endpoints must exist and differ
- Assessment dispute_status, link_ids, methodology_version required; confidence label/level pairing enforced by schema on Assessment and Finding
- Tier D/E source flags demoted from errors to advisories
- Replaced the false SHA-256 example (empty-string digest) with verifiable digests of documented synthetic bytes
- Valid fixture now contains a superseded entity version + connecting Revision, proving the versioning workflow validates; new invalid fixtures: duplicate-version-id, missing-manifest (old duplicate-id fixture removed — it enshrined the wrong invariant)
- Evidence submission and PR templates aligned with the v0.2 model (polarity on links, digests, version workflow); confidential-material prohibition made normative in CONTRIBUTING, ETHICS, and templates
- All schemas declare version 0.2.0 (one coherent bundle)
- Accepted direction for immutable edition manifests recorded as D-016 (design ADR required before implementation)

### Changed — response to independent architecture review (2026-08-05)

Schema version 0.2.0. Breaking changes; no migration needed (no investigation data existed). Full reasoning in DECISIONS.md D-009 through D-014; the review itself is preserved in docs/reviews/.

- Identity/version split: every entity now carries a stable `id` plus an immutable per-version `version_id`; supersession moved to package manifests; `superseded` and `revised` lifecycle statuses removed
- New `ClaimEvidenceLink` entity: claim-evidence connections and polarity moved off Evidence; dual backlink arrays removed from Claim and Evidence
- Assessment split into three dimensions: `conclusion`, `confidence_level` (relabelled: speculative/weak/moderate/strong/near_certain), `dispute_status`; `claim_status` removed from Claim
- Source entities gain `artifacts` with SHA-256 fixity and per-artifact rights metadata; tier A/B sources require digests
- New `package.yaml` manifest per investigation (schema/package.schema.json)
- Validator overhaul: fails on vacuous runs; `--self-test` proves valid fixtures pass and invalid fixtures fail; .yml bypass closed; duplicate YAML keys rejected; all schema errors reported; local $ref registry; real ULID validation (charset + timestamp constraint); reference type-checking; manifest consistency checks
- New fixtures/: one valid fictional package, five invalid packages (one invariant violated each)
- Tests rewritten around fixtures and run in CI; dependencies pinned
- README reclassified as pre-alpha; ARCHITECTURE.md now separates implemented from planned validation; licence scope narrowed to original work only
- Fixed: three v0.1 example IDs contained characters invalid in Crockford Base32 (caught by the new ULID validation); broken relative link in investigation template; ulid-py/python-ulid API mismatch in template comments

### Removed

- `scripts/init-repo.command` (bootstrap workaround; deleted git locks and rewrote git identity — unsafe as a distributed utility)

---

## [0.1.0] — 2026-08-04

### Added

- Complete repository scaffold for Body of Evidence platform
- Root documentation: README, VISION, ARCHITECTURE, METHODOLOGY, GOVERNANCE, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, VERSIONING, STYLE_GUIDE, TERMINOLOGY, DISCLAIMER, ETHICS, AI_GUIDELINES, PEER_REVIEW, REPRODUCIBILITY, DECISIONS
- JSON Schema definitions for all 13 entity types: Investigation, Claim, Evidence, Source, Person, Organisation, Event, Timeline, Assessment, Relationship, Revision, Review, Finding
- Shared common schema (`schema/common.schema.json`) defining reusable definitions
- YAML examples for each entity type in `examples/`
- Investigation `_template/` directory for bootstrapping new investigations
- Validation script stubs: `validate.py`, `validate_schema.py`, `validate_ids.py`, `validate_references.py`, `validate_orphans.py`, `validate_provenance.py`
- GitHub Actions workflow stubs: `validate-schema.yml`, `lint.yml`
- GitHub issue templates: bug report, evidence submission, claim challenge, new investigation proposal
- GitHub PR template
- CODEOWNERS file
- Apache 2.0 license
- CITATION.cff for academic citation
- `.gitignore`
- `docs/history/founding-prompt.md` — the founding specification

### Architecture Decisions

- YAML as canonical source of truth (D-001)
- ULID-based entity IDs with `boe:<type>:<ulid>` format (D-002)
- 5-level confidence scale (D-003)
- Immutable published entities with revision history (D-004)
- Apache 2.0 license (D-005)
- Self-contained investigation directory packages (D-006)
- MCP support as design constraint, not v0.1 deliverable (D-007)
- Python for validation scripts (D-008)

---

[Unreleased]: https://github.com/egarcia74/body-of-evidence/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/egarcia74/body-of-evidence/releases/tag/v0.1.0
