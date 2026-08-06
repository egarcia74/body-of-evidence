# Reproducibility

## What Reproducibility Means Here

A Body of Evidence investigation is reproducible if an independent investigator, starting from the same primary sources, can construct the same evidence model and reach the same assessments.

This is a stronger standard than "the findings are correct." It means the reasoning is transparent enough that someone can check your work step by step.

---

## Requirements for Reproducibility

### 1. Source Availability

Every source must be either:

- Publicly accessible at a documented URL (with an archived copy link where possible)
- Available via an identifiable public records request, court filing, or other formal channel
- Documented with enough detail that another investigator can obtain the same document

Sources that are not obtainable by a third party cannot support findings above confidence level 3 (`moderate`).

### 2. Extraction Transparency

The specific passage, data point, or observation extracted from each source must be documented in the `Evidence` entity, not just "see source X." Someone should be able to open the source and find the specific thing you extracted.

### 3. Assessment Rationale

Every `Assessment` entity includes a written rationale field. This rationale must explain specifically:

- What evidence was considered
- Why that evidence supports the claimed confidence level
- What contradictory evidence was considered and why it did not change the assessment
- What would change the confidence level (what evidence, if found, would raise or lower it)

An assessment rationale that would not help an independent investigator reconstruct your reasoning is not sufficient.

### 4. Negative Space Documentation

Document what you looked for and did not find. An investigation that found no evidence of X is more useful if it records that investigators looked for X in sources A, B, and C and found nothing, than if it simply omits X.

### 5. Versioning

All structured data is version-controlled in Git. The Git history is part of the reproducibility record. Investigators can reconstruct the state of an investigation at any point in time.

*(D-016, accepted 2026-08-06: reconstruction currently requires reading Git history — "Git archaeology" — because the manifest that defines a release is mutable. Immutable Editions are designed to make ONE PACKAGE's release reconstructable from a single artifact, without walking history. A release that imports other packages needs each imported Edition and its validated bytes too, so "a single artifact" is a per-package claim, not a whole-dependency-graph one. The design is accepted; the mechanism is NOT built, so Git history remains the only mechanism today. See "The D-016 design" in DECISIONS.md.)*

---

## Reproducibility and Confidence

| Reproducibility Status | Effect on Confidence |
|---|---|
| Fully reproducible — sources publicly available, extraction documented, rationale complete | No penalty |
| Partially reproducible — some sources not publicly obtainable | Maximum confidence level: 3 (`moderate`) |
| Not reproducible — sources cannot be independently obtained or identified | Assessment is recorded but flagged; maximum confidence: 1 (`speculative`) |

---

## Archiving Sources

Where possible, investigators should archive external sources at a persistent URL (web.archive.org, archive.ph, or a project-maintained archive). External URLs break. Archived copies prevent evidence from disappearing.

Archive links are recorded in the `Source` entity's `archive_url` field.

---

## Computational Reproducibility

Where an investigation includes data analysis:

- The raw data must be included in the repository (or linked to a persistent source)
- The analysis scripts must be included in `scripts/` or the investigation's directory
- The scripts must produce the same output from the raw data without manual intervention

This is a future requirement. Investigations in v0.1 that include data analysis should at minimum document the methodology used.

---

## Why This Matters

The value of this platform is not just that it publishes findings — it is that those findings can be challenged and verified. An investigation that cannot be reproduced is, at best, a claim. An investigation that can be reproduced is evidence.
