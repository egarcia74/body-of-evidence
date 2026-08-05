# CLAUDE.md — Body of Evidence

Project memory for Claude Code sessions. Keep this current when architecture or conventions change.

## What this is

Open-source, version-controlled evidence platform for transparent, reproducible investigations built from primary sources. **Pre-alpha (schema v0.2). No investigations published yet.** Structured YAML is the canonical source of truth; markdown/pages/MCP are generated views.

## Current state (2026-08-05)

- Commit `f758968`: v0.1 founding scaffold
- Commit `1bfdae7`: schema v0.2 — response to first independent review (3.5/10, no-go)
- Four independent reviews in `docs/reviews/` (3.5 → 4.8 → 5.8 → 6.2/10). Fourth pass confirmed the third-pass probes now fail correctly, but found D-017's "exact intended error" fixture claim was unenforced and a cross-package Revision hole (H-02b); both FIXED per D-018 (structured diagnostics + exact-set fixture assertions + package-scoped revisions + full-path symlink enforcement).
- All ADRs in `DECISIONS.md` (D-001..D-018). D-016 is the accepted DIRECTION for immutable edition manifests — design ADR still required; do not implement piecemeal.
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
9. **Revisions connect versions of ONE entity, OWNED BY ONE PACKAGE.** Endpoint existence is not enough — validators check endpoint identity, type, and package ownership (not just that both endpoints exist, but that they belong to the entity being revised and to the package containing the Revision), and that superseded versions are not current in the manifest.
10. **Validation must never be vacuous.** `validate.py` fails on empty runs; fixtures prove both directions with exact diagnostic-code-set assertions (structured `Diagnostic(code, validator, path, message)`, not free-form strings — D-018).

## AI contribution limits

`AI_GUIDELINES.md` governs what Claude Code (and any AI tool) may do in this repo. Read it before touching investigation content. Summary: AI may draft structure, write tooling/schema code, and assist search/summarisation — but may **not** generate evidence claims, assign confidence levels, produce source citations, or have AI-drafted assessment text pass as human analysis without disclosure. This applies to investigation *content* work, not to schema/validator engineering.

## Commands

```bash
pip install -r scripts/requirements.txt   # pinned deps (needs jsonschema>=4.18 + referencing)
python3 scripts/validate.py --self-test   # valid fixtures must pass, invalid must fail
python3 scripts/validate.py               # validate investigations (fails if none exist; --allow-empty to override)
python3 -m pytest tests/ -q               # 25 tests, fixture-driven, exact diagnostic-code-set assertions
python3 -c "from ulid import ULID; print(ULID())"  # generate a new version_id/id ULID
```

CI (`.github/workflows/validate-schema.yml`) runs pytest + self-test + investigations with `--allow-empty` (remove that flag when the first real investigation lands).

## Layout notes

- `schema/` — 16 JSON Schemas (draft 2020-12). `common.schema.json` holds shared defs. `package.schema.json` is the manifest.
- `fixtures/valid/harbour-tender-inquiry/` — complete fictional package; must pass every check. Contains a superseded claim version (same id, different version_id, absent from manifest) + connecting Revision — this PROVES the versioning workflow; do not "clean it up". `fixtures/invalid/*` — nine packages, one violated invariant each (incl. a real tracked symlink in manifest-symlink-escape — it is SUPPOSED to be there). Fixtures derive from the invariants, never from current validator behaviour (the original duplicate-id fixture enshrined a wrong invariant; see D-015). `fixtures/cross_package/{pkg-a,pkg-b}` — two packages sharing a stable id on purpose, validated TOGETHER by a dedicated test (not the self-test loop) to prove package-scoped revision ownership (D-018/H-02b).
- `scripts/boe_files.py` — shared file discovery AND the `Diagnostic(code, validator, path, message)` type every validator returns (D-018). All validators use it (scans .yaml AND .yml, rejects duplicate YAML keys). Any new validator must too.
- `investigations/_template/` — copy to start an investigation. Includes `package.yaml` and `links/`.

## Known open items (deliberately deferred — see DECISIONS.md end section)

Governance placeholders (CITATION.cff authors, schema `$id` domain — need real human decisions from Eddie; CODEOWNERS and security contact are fixed, see below), D-016 editions design (top of the queue), deterministic JSON release format, signed releases, SQLite/MCP query index (v0.3), structured evidence selectors + evidence→artifact pinning, SourceWork/Artifact/Fragment split, explicit cross-package dependency declarations (accidental/malicious cross-package Revision claims are now blocked per D-018, but there is still no way to intentionally DECLARE one package depends on another), controlled relationship predicates, YAML resource limits, calendar-valid dates, Actions SHA-pinning + hash-locked deps, DCO/CLA, confidential-source vault (confidential material is prohibited in the repo until one exists — now normative in CONTRIBUTING/ETHICS/templates). **Fourth-pass review also flagged now-live public-repo operational defects.** FIXED same day: CODEOWNERS now names `@egarcia74` (not `@your-org/maintainers`), GitHub private vulnerability reporting is enabled and SECURITY.md points at it, `main` is protected (Lint/Validate checks required, force-push and deletion blocked, no PR requirement yet — solo maintainer), Discussions is enabled, and ordinary `your-org` repo-link placeholders are replaced with `egarcia74/body-of-evidence` in CODEOWNERS/CHANGELOG/CITATION/CONTRIBUTING/README. Still open: the schema `$id` namespace (deliberately NOT substituted — needs a decision on a stable identity that survives repository transfer, not just the current GitHub owner) and LICENSE/NOTICE split so GitHub detects Apache-2.0.

## Conventions

- Conventional commits (`feat:`, `fix:`, `schema:`, `docs:`; `!` for breaking).
- British/American English consistent per file (docs currently use organisation with -s).
- Fixture/example data must be fictional or safely historical; politically neutral where possible.
- When schemas change: update examples, fixtures, tests, TERMINOLOGY.md, and ARCHITECTURE.md together — the test suite catches example/schema drift.
- Remote: `origin` → `github.com/egarcia74/body-of-evidence` (public). Never push without being asked, even though the repo is already public.
