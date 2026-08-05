# Roadmap

## Version 0.1 — Platform Bootstrap (done, then substantially revised)

The founding scaffold, followed by three independent architecture reviews
(preserved in `docs/reviews/`) and two remediation rounds (DECISIONS.md
D-009..D-016). Current state: schema bundle 0.2.0, 16 entity schemas,
non-vacuous self-proving validation (1 valid + 9 invalid fixture packages),
23 tests in CI, green lint baseline. No investigations published.

---

## Version 0.2 — Editions, then First Investigations

Order matters: the D-016 Edition design must land BEFORE real investigation
data accumulates around the mutable manifest model.

- [ ] D-016 Edition ADR: immutable content-addressed edition manifests,
      RFC 8785 canonical JSON releases, version-pinned references —
      designed as one unit (C-02/C-03 from the reviews)
- [ ] Evidence→Source-version, artifact-digest, and selector anchoring (H-04)
- [ ] Assessment graph semantics: link ownership, contrary-evidence
      completeness, confidence ceilings (H-03)
- [ ] Operational governance: real CODEOWNERS, security contact, quorum,
      appeals, release authority (H-08 — requires humans)
- [ ] Inbound rights decision (DCO/CLA) and data/content licensing (H-09)
- [ ] Privacy, redaction, and retention policy before any investigation
      involving living people (H-10)
- [ ] Publish 2–3 heterogeneous pilot investigations on the edition model
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

- Cryptographic signing of investigation states
- IPFS/content-addressed source archiving
- DOI registration for investigations
- Integration with Wikimedia sources
- Multi-language support
- Formal academic citation export (BibTeX, RIS)
- Challenge resolution dashboard
- Contributor reputation system

Items move from this section to a versioned milestone when there is both demand and a willing implementer.
