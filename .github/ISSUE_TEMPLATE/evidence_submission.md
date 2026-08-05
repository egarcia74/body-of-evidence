---
name: Evidence Submission
about: Submit new evidence for an existing investigation
title: "[EVIDENCE] <investigation-slug>: <brief description>"
labels: evidence
assignees: ""
---

<!--
CONFIDENTIALITY: Do NOT submit confidential material, information from
confidential sources, or anything you are not permitted to publish. This
is a public repository with permanent history. A private evidence vault
does not exist yet; until it does, confidential material is prohibited.
-->

## Investigation

Slug:
Investigation ID: `boe:investigation:...`

## The Source

- **Title:**
- **Type:** (primary_document / testimony / data / audio_video / photograph / correspondence / publication / news_report / analysis)
- **Date:**
- **URL:**
- **Archive URL:** (web.archive.org or archive.ph link)
- **Provenance — Origin:** (where this document comes from)
- **Provenance — Obtained via:** (how you obtained it)
- **Quality Tier:** (A / B / C / D / E)
- **SHA-256 of the retrieved file:** (required for tier A/B — run `shasum -a 256 <file>`)
- **Byte length / media type:**
- **Rights status:** (can this document legally be redistributed? The repository licence does not cover third-party documents)

## The Evidence (the extraction — carries NO polarity)

**Location in source:** (page, paragraph, timestamp, section)

**Quotation (verbatim, preferred over paraphrase):**
>

**Description (what this extraction is, not what it proves):**

**Interpretation (optional, kept separate):**

## The Link(s) (how this evidence bears on each claim — polarity lives here)

Evidence connects to claims through ClaimEvidenceLink entities. The same
evidence can support one claim and contradict another, so fill one block
per claim.

### Link 1

- **Claim ID (or proposed new claim statement):** `boe:claim:...`
- **Polarity:** (supports / contradicts / contextualises / corroborates / impeaches)
- **Strength:** (direct / strong_circumstantial / circumstantial / weak)
- **Reasoning:** (why this evidence bears on this claim in the stated way)

### Link 2 (if applicable)

- **Claim ID:**
- **Polarity:**
- **Strength:**
- **Reasoning:**

## Declarations

- [ ] This submission contains no confidential material and nothing I lack the right to publish
- [ ] I extracted the quotation from the original source myself (not from an AI summary — see AI_GUIDELINES.md)
- [ ] Any AI assistance in preparing this submission is disclosed below

AI assistance disclosure (or "none"):

Conflict of interest (or "none"):

## Notes

<!-- Anything else the reviewer should know -->
