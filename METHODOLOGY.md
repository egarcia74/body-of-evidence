# Methodology

## Purpose

This document defines the standards by which evidence is collected, assessed, and rated in Body of Evidence investigations. Every contributor and reviewer must understand this methodology before submitting or reviewing evidence.

The goal is not to reach a predetermined conclusion. The goal is to establish what the evidence supports, at what confidence level, and why.

---

## Core Methodological Principles

### 1. Primary Sources First

Evidence is always grounded in primary sources: original documents, official records, sworn testimony, verified data, direct observation. Secondary sources (analysis, reporting, commentary) are recorded separately and never treated as equivalent to primary sources.

### 2. Evidence and Interpretation Are Separate

The platform separates what a source *says* (evidence) from what we *conclude* from it (assessment). A source document may be unambiguous; the interpretation of that document in context may still be uncertain. These are recorded as distinct entities.

### 3. Falsifiability

Every `Claim` entity must be falsifiable. Claims like "X was generally considered problematic" are not valid — they cannot be tested against evidence. Claims like "Document X states that Y occurred on date Z" are falsifiable.

### 4. Completeness Obligation

Investigators must not selectively present only supporting evidence. If contrary evidence exists, it must be documented. An investigation that ignores contradictory evidence is not valid under this methodology.

### 5. Provenance Chain

Every source must have a documented provenance chain: where did this document come from? When was it obtained? How was its authenticity verified? A source without provenance is recorded but cannot support a high-confidence assessment.

---

## The Confidence Framework

Every `Assessment` entity carries a confidence level from 1 to 5.

### Confidence Levels

| Level | Label | Description |
|---|---|---|
| **5** | `confirmed` | Established beyond reasonable doubt. Multiple independent primary sources corroborate the claim. No credible alternative explanation consistent with the evidence. The claim would survive aggressive adversarial review. |
| **4** | `probable` | Strongly supported by evidence. Minor evidentiary gaps or single-source dependency that cannot be resolved with currently available materials. Preponderance of evidence supports the claim. |
| **3** | `plausible` | Supported by available evidence, but alternative explanations remain viable. The claim is more likely true than not, but reasonable investigators could disagree. |
| **2** | `contested` | Evidence exists on multiple sides of the claim. No clear preponderance. The claim cannot be resolved with available evidence. Both the claim and its negation are defensible. |
| **1** | `speculative` | Limited or indirect evidence. The claim is possible but not well-supported. Significant uncertainty. Included for completeness, not as a finding. |

### Confidence Factors

Confidence is determined by weighing these factors:

| Factor | What to ask |
|---|---|
| **Evidence strength** | Is each piece of evidence direct or circumstantial? First-hand or reported? |
| **Source quality** | Is the source primary? Official? Independently verified? Has it been authenticated? |
| **Corroboration** | How many independent sources support the claim? Do they agree in detail? |
| **Completeness** | Is there obviously missing evidence? Have we looked for it? |
| **Alternative explanations** | What other explanations fit the available evidence? How credible are they? |
| **Context integrity** | Is the evidence being interpreted in context, or cherry-picked? |
| **Contradictory evidence** | What evidence argues against the claim, and how strong is it? |

### Confidence Is Not Certainty

A confidence level of 5 does not mean we are certain. It means the evidence, as we understand it, is overwhelming. New evidence can change any assessment. When it does, a `Revision` entity documents the change.

### Confidence Must Be Reasoned

An `Assessment` entity must include a `rationale` field explaining why this confidence level was assigned, not just what level was assigned. "Strong sources" is not a rationale. "Three independently obtained primary documents from different agencies, corroborating the same sequence of events, with no credible contradictory evidence identified" is a rationale.

---

## Source Classification

### Source Types

| Type | Description |
|---|---|
| `primary_document` | Original document (government record, court filing, internal memo) |
| `testimony` | Sworn testimony, deposition, formal statement |
| `data` | Raw dataset, statistical record |
| `audio_video` | Recording (authenticated) |
| `photograph` | Image (authenticated, with chain of custody) |
| `correspondence` | Letters, emails, messages |
| `publication` | Peer-reviewed paper, official report |
| `news_report` | Secondary — journalism based on primary sources |
| `analysis` | Secondary — expert analysis or commentary |
| `other` | Anything not fitting the above |

### Source Quality Tiers

| Tier | Label | Criteria |
|---|---|---|
| A | `verified_primary` | Primary source with authenticated provenance |
| B | `probable_primary` | Primary source with strong but not fully verified provenance |
| C | `credible_secondary` | Secondary source with identified primary sources |
| D | `unverified` | Authenticity not established |
| E | `disputed` | Authenticity or accuracy actively contested |

---

## Claim Structure

A valid claim:

- Is a single, atomic, falsifiable assertion
- References the specific evidence it is based on
- Does not bundle multiple assertions (split bundled claims into separate entities)
- Distinguishes between what the evidence says and what it implies

**Valid claim:** "FBI memorandum dated 1963-11-22 (source: boe:source:...) states that the Director was notified of the assassination within 90 minutes."

**Invalid claim:** "The FBI knew about the assassination and covered it up." (Bundles assertion with interpretation; not falsifiable in this form.)

---

## Revision and Correction Policy

When evidence changes, or an error is discovered:

1. Do not edit the existing `Assessment` or `Finding` in place (unless it is in `draft` state).
2. Create a new `Assessment` or `Finding` with updated content.
3. Create a `Revision` entity referencing both old and new entities.
4. The old entity is preserved. Its status is updated to `superseded`.
5. Document the reason for the revision in the `Revision.reason` field.

This means the historical record of what was concluded, and when, is always intact.

---

## What This Methodology Does Not Do

- It does not determine legal guilt or innocence.
- It does not assign moral blame.
- It does not predict future events.
- It does not reach conclusions beyond what the evidence supports.
- It does not substitute for legal, medical, or scientific expertise.

Findings should always include a caveat noting these limits where relevant.
