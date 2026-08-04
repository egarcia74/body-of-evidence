# Roadmap

## Version 0.1 — Platform Bootstrap (current)

Establish the foundation. No investigations published yet.

- [x] Repository scaffold and directory structure
- [x] Core documentation (VISION, ARCHITECTURE, METHODOLOGY, GOVERNANCE, etc.)
- [x] JSON Schema for all 13 entity types
- [x] YAML examples for each entity
- [x] Validation script stubs
- [x] GitHub Actions CI stubs (schema validation, linting)
- [x] Issue and PR templates
- [x] Investigation `_template/` directory
- [x] MCP architecture documented (not implemented)
- [x] Apache 2.0 license and CITATION.cff

---

## Version 0.2 — First Investigations

Validate the data model against real investigations. Expect schema iteration.

- [ ] Publish 2–3 investigations using the v0.1 schema
- [ ] Refine schema based on real data (preserve backwards compatibility)
- [ ] Complete validation scripts (schema, IDs, references, orphans, provenance)
- [ ] Full CI pipeline (validation on every PR)
- [ ] Dead link checker
- [ ] Investigation README generation from structured data
- [ ] Contributor documentation guides
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
