# Vision

## The Problem

Complex investigations are hard to trust.

Not because the investigators are dishonest — but because the structure of most published investigations makes independent verification nearly impossible. Conclusions get separated from their sources. Sources get paraphrased until their original meaning shifts. Revisions happen silently. Context collapses. The chain of reasoning becomes opaque.

This is especially damaging for investigations that matter: government document releases, public health controversies, parliamentary inquiries, corporate misconduct, historical record reconstruction. The higher the stakes, the more important it is that the reasoning be inspectable.

The current default — a PDF report, a news article, a website — is not inspectable. It is a presentation. It cannot be forked, challenged, extended, or reproduced in the way software can.

## What We're Building

Body of Evidence treats investigations the way good engineering teams treat code: as a version-controlled, testable, reviewable artefact where every change is documented and every assertion can be traced.

**The core idea:** if structured evidence is your canonical source of truth, everything else becomes a view over that data. A readable web page. A machine-queryable API. An AI-navigable knowledge graph. All generated. All consistent. All traceable back to primary sources.

This means:

- A reader can follow any claim back to its source document
- A challenger can file a formal challenge against a specific claim
- A reviewer can assess the confidence level of any finding
- A researcher can reproduce the entire evidence chain
- An AI agent can query the evidence model and answer questions about it
- A developer can add a new investigation without redesigning anything

## What We Are Not Building

We are not building:

- A news website
- A political platform
- A place for opinion
- A fact-checking service (in the journalistic sense)
- A platform that reaches conclusions for you

We are building infrastructure that makes conclusions challengeable and traceable. What you conclude from the evidence is your business. Our job is to make the evidence available in a form that makes your reasoning auditable.

## Who This Is For

**Investigators** who want their work to be taken seriously and be reproducible.

**Citizens** who want to understand complex issues from primary sources rather than intermediaries.

**Researchers** who need a structured evidence base for secondary analysis.

**Journalists** who want to publish investigations in a form that can be independently verified.

**AI systems** that need structured, reliable evidence to reason about complex issues.

**Future historians** who will need to understand what was known, when, and on what basis.

## The Long Game

Version 0.1 establishes the platform. Future versions will add:

- Published investigations across multiple domains
- A web interface for human browsing
- An MCP server for AI-assisted evidence querying
- Peer review tooling
- Cross-investigation linking
- Citation and reference tracking
- A public API

The platform is designed so that none of this requires redesigning the data model. The schema is the foundation. Everything else is built on it.

## Guiding Principles

1. **Evidence and interpretation are separate.** The platform records both, but never conflates them.
2. **Traceability is non-negotiable.** Every claim has a source. Every source has provenance.
3. **History is immutable.** Conclusions that change are superseded, not silently overwritten.
4. **Confidence is explicit.** Every assessment states its confidence level and the reasoning behind it.
5. **Reproducibility is a design constraint.** Any investigator with the same sources should be able to reach the same structured evidence model.
6. **Transparency over advocacy.** The platform presents evidence. It does not argue.
7. **Simplicity scales.** The data model should be simple enough that a new investigation can be added by a single person with no platform-specific expertise.
