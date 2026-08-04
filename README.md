# Body of Evidence

**An open-source, version-controlled evidence platform for publishing transparent, reproducible investigations built from primary sources.**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-orange.svg)](CHANGELOG.md)

---

## What This Is

Body of Evidence is infrastructure for investigations that need to be:

- **Inspectable** — every claim traces to a source
- **Auditable** — every revision is documented
- **Reproducible** — any investigator can reconstruct the evidence chain
- **Reviewable** — every assessment can be challenged
- **Extendable** — new investigations slot in without redesigning the platform

It is not a website. Not a political project. Not an opinion platform. It is a structured data model with tooling to turn that data into readable, verifiable investigations.

---

## How It Works

```
Structured Data (YAML/JSON) → Generated Markdown → GitHub Pages → Humans
Structured Data (YAML/JSON) → MCP Server → AI Agents
```

Structured data is the canonical source of truth. Everything else — markdown, web pages, AI interfaces — is generated from it. If there is ever a conflict between a rendered page and the underlying data, the data wins.

---

## What You Can Do With It

- Publish an investigation backed by primary sources
- Challenge a claim and document your challenge formally
- Trace any conclusion back through its evidence chain
- Fork an investigation and propose revisions
- Query the evidence model via MCP-compatible AI tools
- Verify that nothing has been silently changed

---

## Supported Investigation Types

The platform is domain-agnostic. Examples of what it can support:

- Government document releases (JFK Records, Pentagon Papers, Church Committee)
- Public health investigations (COVID origins, clinical trial data)
- Parliamentary and judicial inquiries (Royal Commissions, Inspector General reports)
- Scientific controversies
- Corporate investigations
- Independent journalism investigations
- Historical record reconstruction

The data model does not change when a new investigation type is added.

---

## Repository Structure

```
body-of-evidence/
├── investigations/          # Per-investigation evidence data
│   └── _template/           # Template for new investigations
├── schema/                  # JSON Schema definitions for all entities
├── examples/                # YAML examples of each entity type
├── scripts/                 # Validation, generation, utility scripts
├── docs/                    # Extended documentation, guides, history
│   ├── guides/              # How-to guides for contributors
│   ├── history/             # Founding documents and decision history
│   └── adr/                 # Architecture Decision Records
├── templates/               # Investigation and GitHub templates
├── src/mcp/                 # Future MCP server implementation
├── lib/                     # Shared library code
├── tests/                   # Validation and integration tests
└── .github/                 # GitHub Actions, issue/PR templates
```

---

## Getting Started

### As a Reader

Browse `investigations/` to explore published investigations. Each investigation contains a README summarising findings, with claims, evidence, and sources in structured YAML files.

### As a Contributor

1. Read [CONTRIBUTING.md](CONTRIBUTING.md)
2. Read [METHODOLOGY.md](METHODOLOGY.md) — especially the confidence framework
3. Read [TERMINOLOGY.md](TERMINOLOGY.md) — shared vocabulary matters
4. Read [ETHICS.md](ETHICS.md) — the principles behind editorial decisions
5. Open an issue using the appropriate template

### As a Developer

```bash
git clone https://github.com/your-org/body-of-evidence
cd body-of-evidence
pip install -r scripts/requirements.txt
python scripts/validate.py
```

---

## Core Principles

1. Evidence and interpretation are always kept separate
2. Every conclusion must be traceable to primary sources
3. Every revision is documented — historical conclusions are never silently rewritten
4. Every assessment explains its confidence level
5. Every source has documented provenance
6. Transparency over advocacy

See [VISION.md](VISION.md) for the full philosophy.

---

## Documentation Index

| Document | Purpose |
|---|---|
| [VISION.md](VISION.md) | Why this exists and where it's going |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Technical design and data model |
| [METHODOLOGY.md](METHODOLOGY.md) | How evidence is assessed and rated |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute |
| [GOVERNANCE.md](GOVERNANCE.md) | Decision-making and editorial process |
| [TERMINOLOGY.md](TERMINOLOGY.md) | Shared vocabulary |
| [ETHICS.md](ETHICS.md) | Editorial ethics and conflict of interest policy |
| [AI_GUIDELINES.md](AI_GUIDELINES.md) | How AI tools may and may not be used |
| [PEER_REVIEW.md](PEER_REVIEW.md) | The review process for claims and findings |
| [REPRODUCIBILITY.md](REPRODUCIBILITY.md) | Standards for reproducible investigations |
| [SECURITY.md](SECURITY.md) | Responsible disclosure policy |
| [DISCLAIMER.md](DISCLAIMER.md) | Legal and editorial disclaimer |
| [ROADMAP.md](ROADMAP.md) | What's planned |
| [DECISIONS.md](DECISIONS.md) | Key architectural and editorial decisions |
| [CHANGELOG.md](CHANGELOG.md) | Version history |

---

## Status

**Version 0.1 — Platform Bootstrap.** The data model, schema, and infrastructure are established. No investigations are published yet. The first investigations will be added in v0.2.

---

## License

Apache 2.0. See [LICENSE](LICENSE).

## Citation

See [CITATION.cff](CITATION.cff).
