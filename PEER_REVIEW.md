# Peer Review

## Purpose

Peer review is the mechanism by which the platform ensures that published investigations are methodologically sound, factually grounded, and free from obvious conflicts of interest. It is not editorial censorship — reviewers check methodology and evidence, not conclusions.

---

## When Review Is Required

| Lifecycle Transition | Review Required |
|---|---|
| `draft` → `review` | Lead investigator submits; no external review yet |
| `review` → `published` | At least one independent reviewer must approve |
| `published` → `revised` | Lead investigator may make revisions; published content requires review before `revised` becomes `published` |
| Any challenge (`Review` entity with type `challenge`) | Lead investigator must respond; maintainer determines outcome |

---

## Who Can Review

Any contributor who has had at least one contribution merged may review an investigation. The lead investigator of an investigation may not be the sole reviewer of that investigation.

Reviewers with conflicts of interest (see [ETHICS.md](ETHICS.md)) must recuse themselves.

---

## What Reviewers Check

Reviewers are not asked to agree with the findings. They are asked to verify:

### Methodological Compliance

- [ ] All claims are falsifiable and atomic
- [ ] All evidence traces to a named source
- [ ] All sources have documented provenance
- [ ] Confidence levels are assigned with written rationale
- [ ] Contradictory evidence is documented, not omitted
- [ ] Claims and interpretations are clearly separated

### Entity Integrity

- [ ] All IDs follow the `boe:<type>:<ulid>` format
- [ ] No duplicate IDs
- [ ] All referenced IDs resolve
- [ ] No orphaned evidence (evidence not linked to a claim)

### Conflict of Interest

- [ ] Lead investigator has disclosed any conflicts
- [ ] No undisclosed relationship between the investigator and investigation subjects is apparent

### Completeness

- [ ] The investigation scope is clearly stated
- [ ] The investigation does not claim to address questions outside its scope
- [ ] Major gaps in the evidence base are noted in the findings

---

## The Review Record

Reviews are recorded as `Review` entities in the investigation's data. A review entity captures:

- Reviewer identity (can be pseudonymous)
- Review type (`endorsement`, `correction`, `challenge`, `methodology_review`)
- Review date
- Review outcome
- Detailed notes
- Whether the reviewer has any relevant conflicts to disclose

This means the review history of an investigation is part of its permanent record.

---

## Formal Challenges

A formal challenge is a `Review` entity with type `challenge`. Challenges must:

- Identify the specific claim, finding, or assessment being challenged
- Provide counter-evidence or methodological objection with specificity
- Not be based solely on disagreement with a conclusion

The challenge process:

1. Challenger files a **Claim Challenge** issue (or submits a PR with the `Review` entity)
2. Lead investigator has 30 days to respond
3. If the challenge is resolved between challenger and lead investigator, the outcome is documented
4. If unresolved, a maintainer makes a binding determination
5. The outcome is documented in the `Review` entity
6. If the challenge is upheld, a `Revision` entity is created

---

## Limitations of Peer Review

Peer review on this platform:

- Does NOT guarantee that findings are legally correct
- Does NOT substitute for expert review in specialised domains (legal, medical, scientific)
- Does NOT verify that all relevant evidence has been found — only that what has been found is correctly handled
- Is NOT equivalent to editorial review by a professional publication

These limitations are stated here and should be referenced in investigation findings where relevant.
