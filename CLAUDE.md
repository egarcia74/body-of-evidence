# CLAUDE.md — Body of Evidence

Project memory for Claude Code sessions. Keep this current when architecture or conventions change.

## What this is

Open-source, version-controlled evidence platform for transparent, reproducible investigations built from primary sources. **Pre-alpha (schema v0.2). No investigations published yet.** Structured YAML is the canonical source of truth; markdown/pages/MCP are generated views.

## Current state (2026-08-05)

- Commit `f758968`: v0.1 founding scaffold
- Commit `1bfdae7`: schema v0.2 — response to first independent review (3.5/10, no-go)
- Seven independent reviews in `docs/reviews/` (3.5 → 4.8 → 5.8 → 6.2 → 6.4 → 6.6 → 6.8/10). Each pass treats the previous round's remediation claims as propositions to falsify, not evidence of completion — and EVERY pass so far has found at least one claim that was narrower than stated, including the fix for the previous pass's narrowness. Seventh pass, on D-020's fixes: `REFERENCE_FIELDS` checked existence/type/package but never checked whether the referenced id was the package manifest's CURRENT version — a Claim could be dropped from `package.yaml` while every Link/Assessment/Revision still referencing it validated clean (H-20, the highest-severity finding of any round so far); `NESTED_REFERENCE_FIELDS` existed only to satisfy a completeness test — nothing at runtime actually consumed it, so it was descriptive, not executable (M-19); and the symlink scan only looked at `*.yaml`/`*.yml` files, missing symlinked SUBDIRECTORIES and non-YAML symlinks entirely (M-20). All FIXED per D-021. **Pattern to internalise (now confirmed across FOUR consecutive rounds — D-018 through D-021):** "I fixed the specific case the reviewer demonstrated" is not the same as "I fixed the general claim." Before reporting any fix as done: (a) what OTHER inputs exercise the same code path, not just the review's probe; (b) if you built a "registry" or "completeness test," does anything at RUNTIME actually consume it, or does it only satisfy the test itself (M-19's exact shape); (c) does the check happen at the right POINT in the pipeline — H-20 existed because reference validation ran before manifest state was known, not because any individual check was wrong.
- All ADRs in `DECISIONS.md` (D-001..D-021). D-016 is the accepted DIRECTION for immutable edition manifests — design ADR still required; do not implement piecemeal.
- Lint baseline is deliberately scoped and GREEN (`.markdownlint.jsonc`, `.yamllint` — rationale in the files). Keep it green; if you tighten rules, fix the whole repo in the same commit.
- **Next major task:** the D-016 editions ADR (immutable edition manifests + RFC 8785 canonical JSON + version-pinned references, designed as one unit — resolves C-02/C-03). After that: evidence→artifact selectors (H-04), assessment graph semantics (H-03), Event/Relationship assertion bypass (H-07).

## Core invariants (do not violate)

1. **Published entity version files are never modified.** Not content, not status. New version = new file, same `id`, new `version_id`.
2. **Supersession lives in `package.yaml`** (the manifest), never in the superseded file. There is no `superseded` status. Manifests are mandatory, path-contained, and list exactly one current version per id.
3. **Polarity lives on `ClaimEvidenceLink`**, never on Evidence. Evidence has no claim references.
4. **References are single-direction** (link→claim, link→evidence, assessment→claim). Backlinks are derived, never stored.
5. **Conclusion ≠ confidence ≠ dispute status.** Three separate Assessment fields. "Contested" is not a confidence level.
6. **Confidence labels:** 1=speculative, 2=weak, 3=moderate, 4=strong, 5=near_certain. Ordinal, not probabilistic.
7. **Tier A/B sources need a SHA-256 artifact digest.** URLs locate; digests identify.
8. **IDs:** `boe:<type>:<ulid>` stable across versions; `version_id` bare ULID per version. Crockford Base32 — no I, L, O, U; first char 0–7. **Repeated stable ids across files are VALID** (that is the versioning model); version_ids are globally unique. Do not "fix" duplicate ids without checking version_ids first.
9. **Every reference must resolve to the manifest's CURRENT version of the target id** — not merely to "a file with this id exists" (D-021/H-20, the highest-severity finding to date). Manifests are parsed BEFORE ordinary reference validation, specifically so `current_maps` exists when references are checked; get this pipeline ORDER wrong again and H-20 comes back. Every field in `validate_references.py`'s `REFERENCE_FIELDS`/`NESTED_REFERENCE_FIELDS` registry is checked (D-020/H-18, D-021/M-19; this IS the complete list, enforced by a schema-scanning completeness test AND a behavioural test that dangles every entry and asserts it's actually executed — do not add a registry entry that only satisfies the completeness test), not just Revision endpoints (D-018/H-02b). A stable id CAN legitimately appear in more than one file — `id_index` is a multimap; a reference prefers a same-package match and only flags `REF_WRONG_PACKAGE` when none exists (D-020/H-17; a naive single-owner index produces false positives). There is deliberately no way yet to declare "package A depends on package B". A symlink is rejected everywhere — a package ROOT (D-019/H-15), a manifest-listed entity path (D-018/M-11), an ordinary unmanifested entity file (D-020/H-19), AND any directory or non-YAML file (D-021/M-20; `boe_files.find_all_symlinks` uses `os.walk(followlinks=False)`, not pathlib globbing, specifically so detection doesn't depend on a particular pathlib version's traversal behaviour) — before any file is ever read.
10. **Validation must never be vacuous.** `validate.py` fails on empty runs; fixtures prove both directions with exact, duplicate-preserving diagnostic assertions (structured `Diagnostic(code, validator, path, message, location)`, compared as a sorted list not a set — D-019/M-07b closed the gap where a set silently dropped duplicate diagnostics).

## AI contribution limits

`AI_GUIDELINES.md` governs what Claude Code (and any AI tool) may do in this repo. Read it before touching investigation content. Summary: AI may draft structure, write tooling/schema code, and assist search/summarisation — but may **not** generate evidence claims, assign confidence levels, produce source citations, or have AI-drafted assessment text pass as human analysis without disclosure. This applies to investigation *content* work, not to schema/validator engineering.

## Commands

```bash
pip install -r scripts/requirements.txt   # pinned deps (needs jsonschema>=4.18 + referencing)
python3 scripts/validate.py --self-test   # valid fixtures must pass, invalid must fail
python3 scripts/validate.py               # validate investigations (fails if none exist; --allow-empty to override)
python3 -m pytest tests/ -q               # 49 tests: fixtures, exact diagnostic assertions, CLI-level integration, schema-completeness scan, registry-executability scan
python3 scripts/validate.py --root <dir>  # validate an arbitrary package directory instead of <repo>/investigations (D-019/M-15; --root and its enumeration are error-handled — D-020/M-18, D-021/M-21)
python3 -c "from ulid import ULID; print(ULID())"  # generate a new version_id/id ULID
```

CI (`.github/workflows/validate-schema.yml`) runs pytest + self-test + investigations with `--allow-empty` (remove that flag when the first real investigation lands).

## Layout notes

- `schema/` — 16 JSON Schemas (draft 2020-12). `common.schema.json` holds shared defs. `package.schema.json` is the manifest.
- `fixtures/valid/harbour-tender-inquiry/` — complete fictional package; must pass every check. Contains a superseded claim version (same id, different version_id, absent from manifest) + connecting Revision — this PROVES the versioning workflow; do not "clean it up". `fixtures/invalid/*` — fourteen packages, one violated invariant each (incl. FIVE real tracked symlinks: manifest-symlink-escape's entity-path symlink, investigation-root-symlink's package-ROOT symlink, unmanifested-symlink's not-listed-in-package.yaml entity symlink, broken-unmanifested-symlink's DANGLING one, and symlinked-subdirectory's symlinked DIRECTORY — all five are SUPPOSED to be there; the dangling one is excluded from `.yamllint`'s scan on purpose, see that file). Fixtures derive from the invariants, never from current validator behaviour (the original duplicate-id fixture enshrined a wrong invariant; see D-015). `fixtures/cross_package/{pkg-a,pkg-b}` — two packages sharing a stable id on purpose, validated TOGETHER by dedicated tests (not the self-test loop, which only ever validates one package directory at a time) to prove package-scoped revision ownership (D-018/H-02b), package-scoped ordinary references (D-019/H-02c), AND that a same-package match is preferred over a stale cross-package one (D-020/H-17).
- `scripts/boe_files.py` — shared file discovery AND the `Diagnostic(code, validator, path, message, location)` type every validator returns (D-018/D-019). All validators use it (scans .yaml AND .yml, rejects duplicate YAML keys, refuses to descend into a symlinked package root OR read/traverse ANY individual symlink anywhere in a package — file, directory, or non-YAML — via `find_all_symlinks`'s `os.walk(followlinks=False)` — D-020/H-19, D-021/M-20). Any new validator must too.
- `scripts/validate_references.py`'s `REFERENCE_FIELDS`/`NESTED_REFERENCE_FIELDS` (D-020/H-18, made executable not just descriptive in D-021/M-19) — the single source of truth for which schema fields get reference-checked AND resolved against manifest currency (D-021/H-20), kept honest by `tests/test_validation.py::TestReferenceRegistryCompleteness`, which scans every schema for boe-ID-pattern fields and fails if the registry and the schemas disagree in either direction, PLUS a behavioural test that dangles every registry entry and asserts each one is actually checked. Adding a reference field to a schema without a matching registry entry WILL fail a test — that is the point.
- `investigations/_template/` — copy to start an investigation. Includes `package.yaml` and `links/`.

## Known open items (deliberately deferred — see DECISIONS.md end section)

Governance placeholders (CITATION.cff authors, schema `$id` domain — need real human decisions from Eddie; CODEOWNERS and security contact are fixed, see below), D-016 editions design (top of the queue), deterministic JSON release format, signed releases, SQLite/MCP query index (v0.3), structured evidence selectors + evidence→artifact pinning, SourceWork/Artifact/Fragment split, explicit cross-package dependency declarations (accidental/malicious cross-package Revision claims are now blocked per D-018, but there is still no way to intentionally DECLARE one package depends on another), controlled relationship predicates, YAML resource limits, calendar-valid dates, Actions SHA-pinning + hash-locked deps, DCO/CLA, confidential-source vault (confidential material is prohibited in the repo until one exists — now normative in CONTRIBUTING/ETHICS/templates). **Fourth-pass review also flagged now-live public-repo operational defects.** FIXED same day: CODEOWNERS now names `@egarcia74` (not `@your-org/maintainers`), GitHub private vulnerability reporting is enabled and SECURITY.md points at it, `main` is protected (Lint/Validate checks required, force-push and deletion blocked, no PR requirement yet — solo maintainer), Discussions is enabled, ordinary `your-org` repo-link placeholders are replaced with `egarcia74/body-of-evidence` in CODEOWNERS/CHANGELOG/CITATION/CONTRIBUTING/README, and Dependabot vulnerability alerts are enabled. **Fifth-pass review found the LICENSE fix had NOT actually worked** — GitHub still reported `NOASSERTION` because the text itself (not just the appended block I'd removed) was a paraphrase of Apache-2.0. Now fixed with the byte-for-byte official text (D-019/H-16) — verify via `gh api repos/egarcia74/body-of-evidence --jq .license` before ever reporting a license-detection claim as fixed again. Still open: the schema `$id` namespace (deliberately NOT substituted — needs a decision on a stable identity that survives repository transfer, not just the current GitHub owner) and CITATION.cff authors.

## Conventions

- Conventional commits (`feat:`, `fix:`, `schema:`, `docs:`; `!` for breaking).
- British/American English consistent per file (docs currently use organisation with -s).
- Fixture/example data must be fictional or safely historical; politically neutral where possible.
- When schemas change: update examples, fixtures, tests, TERMINOLOGY.md, and ARCHITECTURE.md together — the test suite catches example/schema drift.
- Remote: `origin` → `github.com/egarcia74/body-of-evidence` (public). Never push without being asked, even though the repo is already public.
