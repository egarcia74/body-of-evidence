# Terminology

Precise shared vocabulary prevents ambiguity. Use these definitions consistently across all contributions.

---

## Core Terms

**Assessment**
A structured evaluation of whether a `Claim` is supported by available evidence, including a confidence level and rationale. Assessments are made by investigators. They are not the same as the evidence itself.

**Claim**
A single, atomic, falsifiable assertion made within an investigation. Claims are the testable units of an investigation. Each claim is either supported, contested, refuted, or unresolved by the available evidence.

**Confidence Level**
A 1–5 scale rating the strength of evidence behind an assessment. See [METHODOLOGY.md](METHODOLOGY.md) for the full framework. Confidence is not certainty. Confidence of 5 means the evidence is overwhelming; it does not mean the claim is proven in a legal sense.

**Evidence**
A specific piece of content from a source that is directly relevant to a claim. Evidence is always tied to a specific source. It is a quotation, a data point, an observed fact from a source — not the source document itself.

**Finding**
A high-level conclusion synthesised from multiple claims and evidence items. Findings represent the investigation's conclusions. They are more interpretive than claims and must reference the claims they synthesise.

**Investigation**
A bounded inquiry with a defined scope, stated methodology, and lifecycle state. An investigation is the container for all related claims, evidence, sources, and findings.

**Person**
An individual who is relevant to an investigation, either as a subject, a source, a witness, or a participant. Recording a person in the data model is not a claim about their conduct — it records their relevance to the investigation.

**Primary Source**
A document or artefact that directly records an event, decision, or statement: original government documents, sworn testimony, official records, authenticated correspondence, raw data. The gold standard for evidence.

**Provenance**
The documented chain of custody for a source: where it came from, how it was obtained, when, and how its authenticity was established. Without provenance, a source cannot support high-confidence assessments.

**Revision**
A documented change to any entity that was previously in `published` state. Revisions preserve the history of the investigation. They are how the platform avoids silent rewrites.

**Review**
A formal peer review of an investigation, finding, or claim. Reviews can result in endorsement, suggested corrections, or formal challenges. They are recorded as entities in the data model.

**Secondary Source**
A document that reports on, analyses, or synthesises primary sources. News articles, academic papers, and expert commentary are secondary sources. They can support claims but must be clearly distinguished from primary sources.

**Source**
A primary or secondary document, recording, or artefact from which evidence is extracted. Sources have provenance, type, and quality tier. Evidence always traces back to a source.

---

## Status Terms

**draft** — Not yet ready for review. Work in progress.

**review** — Submitted for peer review. No further edits pending review outcome.

**published** — Reviewed and approved. Publicly visible.

**revised** — A published item with pending updates. The published version remains visible.

**superseded** — Replaced by a newer version. Preserved for historical record.

**archived** — Closed, no further updates expected. Remains publicly visible.

---

## Investigation Terms

**Lead Investigator** — The person responsible for the coherence and accuracy of an investigation. Named in `investigation.yaml`.

**Scope** — The defined boundaries of an investigation: what questions it is answering, what time period it covers, and what it explicitly excludes.

**Thread** — An informal term for a logical sub-sequence of events or claims within a larger investigation. Not a formal entity type.

---

## Technical Terms

**ULID** — Universally Unique Lexicographically Sortable Identifier. Used as the unique identifier component in all `boe:` IDs. Unlike UUIDs, ULIDs sort by creation time.

**boe ID** — The canonical identifier format: `boe:<type>:<ulid>`. Example: `boe:claim:01HV8QKJZ9XTMK3P2R7N5W6D4F`. IDs are permanent and immutable once assigned.

**MCP** — Model Context Protocol. A standard for exposing structured data and tools to AI agents. The evidence model is designed to be queryable via MCP.

**JSON Schema** — The schema language used to define and validate entity structure. All schemas live in `schema/`.

---

## Terms to Avoid

**"Fact"** — Use "claim" (unassessed) or "finding" (assessed). "Fact" implies certainty the platform does not claim.

**"Proof"** — Use "evidence" or "confirmed finding." Proof is a legal and mathematical standard, not an evidential one.

**"The truth"** — The platform asserts what the evidence supports, not what is true in an absolute sense.

**"Conspiracy"** — Legally and colloquially loaded. Use "coordinated action," "undisclosed agreement," or describe the specific conduct.

**"Whistleblower"** — Use the person's role and the nature of the disclosure. Whether someone is legally a whistleblower is a separate determination.
