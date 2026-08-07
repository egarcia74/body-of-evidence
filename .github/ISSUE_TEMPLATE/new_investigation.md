---
name: New Investigation Proposal
about: Propose a new investigation to be added to the platform
title: "[INVESTIGATION] <proposed slug>"
labels: new-investigation
assignees: ""
---

## Proposed Investigation

**Title:**
**Proposed slug:** (kebab-case, e.g., `church-committee`)

## Scope

**What questions will this investigation address?**

**Time period covered:**

**What is explicitly out of scope?**

## Why this investigation belongs here

<!-- What makes this investigation suitable for Body of Evidence? What is the public interest? -->

## Prerequisite Checks

<!--
This is NOT a complete privacy assessment. The privacy, redaction and
retention policy (H-10) does not exist yet — see ROADMAP.md — so retention
and redaction decisions cannot be recorded here. What this section does is
enforce, at proposal time, the prohibitions that are ALREADY normative in
CONTRIBUTING.md and ETHICS.md, so they are checked before work starts
rather than discovered after.
-->

**1. Does this investigation involve living people?** (yes / no)

<!--
YES => BLOCKED. Not a warning. The privacy, redaction and retention policy
(H-10) does not exist, and public Git history cannot be reliably purged.
-->

**2. Does any source contain personal data about private individuals
beyond what the investigation's public-interest scope strictly requires?**
(yes / no / unsure)

<!--
YES or UNSURE => BLOCKED. CONTRIBUTING.md ("Confidential Material Is
Prohibited") and ETHICS.md ("Harm Awareness") already prohibit this.
Answering "no living people" does NOT exempt an investigation from these
rules: deceased individuals have surviving relatives, and public records
routinely contain third-party personal data.
-->

**3. Is any material confidential, from a confidential source, or subject
to a request for anonymity?** (yes / no / unsure)

<!--
YES or UNSURE => BLOCKED. ETHICS.md: confidential material is prohibited
in this repository entirely until a private vault exists. Where a source
requested anonymity, the correct action today is to not use that source's
material at all.
-->

**4. Can every third-party document be legally redistributed?**
(yes / no / unsure)

<!--
NO or UNSURE => BLOCKED for the affected documents. CONTRIBUTING.md
prohibits submitting documents you are not legally permitted to publish.
The repository licence covers this project's own content, not third-party
documents. Cite a source separately rather than redistributing it.
-->

**5. Are all primary sources publicly obtainable by a third party?**
(yes / no)

<!--
Not a block. If NO, METHODOLOGY.md caps any finding resting on those
sources at confidence level 3 (moderate). List which sources are affected
so the ceiling is applied deliberately rather than discovered at review.
-->

**6. Public interest served by publication, weighed against potential
harm** (ETHICS.md "Harm Awareness" — required even when 1-4 are all clear):

---

## Lead Investigator

**GitHub username:**
**Conflict of interest:** (any relationship with the investigation subject)

## Primary Sources

Identify at least 3 primary sources that are publicly obtainable and will form the evidence base.

1. **Title:** | **URL/Location:** | **Type:**
2. **Title:** | **URL/Location:** | **Type:**
3. **Title:** | **URL/Location:** | **Type:**

## Initial Claims

What are 2–3 initial claims you intend to investigate? These will be refined during the investigation.

1.
2.
3.

## Resources Required

- [ ] I can lead this investigation myself
- [ ] I need co-investigators (describe what help is needed)
- [ ] I need a reviewer with domain expertise (describe the domain)

## Additional Context

<!-- Anything else the maintainers should know before approving this proposal -->
