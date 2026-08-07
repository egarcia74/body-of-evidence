# Roadmap

## Version 0.1 — Platform Bootstrap (done, then substantially revised)

The founding scaffold, followed by three independent architecture reviews
(preserved in `docs/reviews/`) and two remediation rounds (DECISIONS.md
D-009..D-016). Current state: schema bundle 0.2.0, 16 entity schemas,
non-vacuous self-proving validation (1 valid + 9 invalid fixture packages),
23 tests in CI, green lint baseline. No investigations published.

---

## Version 0.2 — Editions, then First Investigations

Order matters twice over. The D-016 Edition design had to land BEFORE real
investigation data accumulated around the mutable manifest model — done.
And the first pilot investigation now lands BETWEEN phase 1 and phase 2,
not after phase 4: building all four phases before any real content exists
would let the design go four phases deep before reality tests it. One small
pilot on the phase-1 Edition model is the cheapest available falsification
of the design, and the same total work either way.

- [x] D-016 Edition ADR: immutable content-addressed edition manifests,
      RFC 8785 canonical JSON releases, Edition-scoped reference
      resolution — designed as one unit (C-02/C-03 from the reviews).
      DESIGN ONLY; implementation is the four phases below.
- [ ] D-016 phase 1: `edition.schema.json`, editions compile + verify, AND
      validated-byte publication (publish from retained bytes or a
      content-addressed snapshot — never a re-read), with the regression
      test that mutates a file between validation and publication. Without
      this the implementation can re-read and silently reintroduce the
      TOCTOU defect D-027 left to this ADR
- [ ] **First pilot investigation on the phase-1 Edition model** —
      resequenced ahead of phases 2-4 (2026-08-07). One small, real
      investigation compiled to an Edition, to falsify the design against
      actual content before three more phases are built on it. What it is
      looking for: whether Edition-scoped resolution is workable in
      practice, whether the working-head/Edition split is comprehensible
      to an author, and whether compile/verify are usable
- [ ] Schema bundle preservation (`schema/v{N}/`) and preserved
      methodology versions — named in D-016 as a prerequisite before an
      Edition can be called fully self-verifying, and scheduled HERE
      (2026-08-07) rather than left ownerless: an Edition can already name
      its `schema_version` without being able to resolve it to bytes, and
      this gets materially more expensive once real investigations exist.
      Must land before phase 4, since a signature over a digest whose
      schema cannot be resolved verifies less than it appears to
- [ ] D-016 phase 2: Edition-scoped reference resolution; removes
      D-023/H-21's interim `referencing_is_current` rule (and is where
      `validate_manifest`'s deferred complexity is discharged)
- [ ] D-016 phase 3: `imports` replaces the unenforced `dependencies`
      field; cross-package references resolve through pinned Editions
- [ ] D-016 phase 4: signature envelope (detached `.sig` over the
      Edition content digest) — envelope designed in D-016, implementation
      deferred; moved here from Unprioritised/Future
- [ ] Evidence→Source-version, artifact-digest, and selector anchoring (H-04)
- [ ] Assessment graph semantics: link ownership, contrary-evidence
      completeness, confidence ceilings (H-03)
- [ ] Operational governance: real CODEOWNERS, security contact, quorum,
      appeals, release authority (H-08 — requires humans)
- [ ] Inbound rights decision (DCO/CLA) and data/content licensing (H-09)
- [ ] Privacy, redaction, and retention policy before any investigation
      involving living people (H-10)
- [ ] Publish the remaining heterogeneous pilot investigations (2-3 total,
      including the first one above) on the edition model
- [ ] Dead link checker; calendar-valid dates; YAML resource limits
- [ ] At least 2 peer reviews completed to test the review process

---

## Version 0.3 — MCP Server (Alpha)

Make the evidence model queryable by AI agents.

- [ ] MCP server implementation in `src/mcp/`
- [ ] Tools: `search_claims`, `search_sources`, `search_people`, `search_events`
- [ ] Tools: `retrieve_evidence`, `compare_claims`, `get_timeline`
- [ ] Tools: `confidence_lookup`, `get_relationship_graph`
- [ ] MCP tool documentation
- [ ] Integration tests for MCP tools
- [ ] Public alpha announcement

---

## Version 0.4 — Web Interface

Human-readable browsing without needing to read YAML.

- [ ] Generated static site (GitHub Pages)
- [ ] Investigation index page
- [ ] Per-investigation browsable view
- [ ] Claim → evidence → source drill-down
- [ ] Confidence level visual indicators
- [ ] Timeline visualisation
- [ ] Search (static, client-side)

---

## Version 0.5 — Cross-Investigation Linking

Connect entities across investigations.

- [ ] Cross-investigation `Person` deduplication
- [ ] Cross-investigation `Organisation` deduplication
- [ ] `Relationship` entities spanning investigations
- [ ] "Also appears in" investigation cross-references
- [ ] Global entity index

---

## Version 1.0 — Stable Platform

Production-ready. Schema is stable. API is versioned.

- [ ] Stable v1 schema (no breaking changes without major version bump)
- [ ] Versioned public API
- [ ] Full test coverage for validation scripts
- [ ] Complete contributor onboarding documentation
- [ ] At least 5 published investigations
- [ ] At least 2 investigations with completed peer reviews
- [ ] Public citation format documented

---

## Unprioritised / Future

Ideas that may be incorporated in future versions, not yet scheduled:

- Cryptographic signing key management and trust model (the signature
  envelope itself is designed in D-016 and scheduled in 0.2 above)
- IPFS/content-addressed source archiving
- DOI registration for investigations
- Integration with Wikimedia sources
- Multi-language support
- Formal academic citation export (BibTeX, RIS)
- Challenge resolution dashboard
- Contributor reputation system

Items move from this section to a versioned milestone when there is both demand and a willing implementer.
