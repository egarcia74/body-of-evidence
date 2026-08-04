# Changelog

All notable changes to Body of Evidence are documented here.

This project adheres to [Semantic Versioning](VERSIONING.md). Dates are ISO 8601.

---

## [Unreleased]

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

[Unreleased]: https://github.com/your-org/body-of-evidence/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/your-org/body-of-evidence/releases/tag/v0.1.0
