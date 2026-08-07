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

## The Assessment Framework

Every `Assessment` entity records **three separate dimensions**. Conflating them was an error in methodology v0.1, corrected in v0.2:

1. **Conclusion** — which way the evidence points: `supported`, `contradicted`, `mixed`, `insufficient`, or `not_assessed`. "Mixed" means credible evidence exists on multiple sides. "Insufficient" means the available evidence cannot resolve the claim either way.
2. **Confidence** — how strong the evidence for that conclusion is, on the 1–5 ordinal scale below.
3. **Dispute status** — whether the assessment is under active formal challenge: `undisputed`, `disputed`, or `unresolved`.

These are independent. An assessment can be high-confidence and disputed (someone has filed a challenge against a well-evidenced conclusion), or low-confidence and undisputed (weak evidence nobody contests). A claim with strong evidence on both sides is `conclusion: mixed` — being contested is *not* a confidence level.

### Confidence Levels

| Level | Label | Description |
|---|---|---|
| **5** | `near_certain` | Multiple independent primary sources corroborate the conclusion. No credible alternative explanation consistent with the evidence. Would survive aggressive adversarial review. |
| **4** | `strong` | Strongly supported by evidence. Minor evidentiary gaps or single-source dependency that cannot be resolved with currently available materials. |
| **3** | `moderate` | Supported by available evidence, but alternative explanations remain viable. Reasonable investigators could disagree. |
| **2** | `weak` | Limited or indirect evidence for the conclusion. Meaningful uncertainty remains. |
| **1** | `speculative` | Minimal or highly indirect evidence. The conclusion is possible but not well-supported. Included for completeness, not as a finding. |

The numeric level and label must always pair as shown. The scale is **ordinal, not probabilistic** — a 4 is not "80% likely". Do not attach percentages to these levels unless the project develops and validates a calibration method.

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

A confidence level of 5 does not mean we are certain. It means the evidence, as we understand it, is overwhelming. New evidence can change any assessment. When it does, a new assessment version is created and the package manifest is updated — the old version is preserved untouched.

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

Every entity has a stable `id` and a per-version `version_id`. Which version is current is recorded **only** in the investigation's package manifest (`package.yaml`). When evidence changes, or an error is discovered:

1. Never modify a published entity version file in any way — not its content, and not its status field. A published version's bytes are frozen.
2. Create a new version file: same `id`, new `version_id`, updated content.
3. Create a `Revision` entity recording the old `version_id`, the new `version_id`, and the reason for the change.
4. Update the package manifest to list the new `version_id` as current.
5. The old version file remains in the repository, untouched. It is superseded *by omission from the manifest*, not by mutation.

This means the historical record of what was concluded, and when, is always intact — and "superseded" is a fact about the release, never an edit to the past.

*(D-016, accepted 2026-08-06: once immutable Editions exist, step 4 updates the mutable **working head** and publishing an Edition becomes the release act, so "the release" gains a concrete artifact rather than meaning "whatever the manifest currently says." An Edition snapshots the manifest's `release_version`, `schema_version` and `methodology_version` at publication: `package.yaml` stays authoritative for the working head, while the Edition's copies are authoritative for that released artifact. The design is accepted; the mechanism is NOT built, so the five steps above are correct as written today. See "The D-016 design" in DECISIONS.md.)* (Methodology v0.1 instructed contributors to update the old entity's status to `superseded`; that was itself a mutation of the historical record and was corrected in v0.2.)

---

## What This Methodology Does Not Do

- It does not determine legal guilt or innocence.
- It does not assign moral blame.
- It does not predict future events.
- It does not reach conclusions beyond what the evidence supports.
- It does not substitute for legal, medical, or scientific expertise.

Findings should always include a caveat noting these limits where relevant.
