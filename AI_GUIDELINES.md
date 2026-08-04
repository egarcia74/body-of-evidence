# AI Guidelines

## Purpose

AI tools are powerful and can accelerate investigation work. They can also introduce fabrications, misattributions, and false confidence — which are especially dangerous in a platform whose value depends on accuracy.

This document states what AI tools may and may not be used for in Body of Evidence contributions.

---

## Permitted Uses

AI tools may be used for:

- **Drafting structure** — generating a first draft of an investigation scaffold, claim list, or document structure that a human then populates with real evidence
- **Writing assistance** — improving the clarity, grammar, and readability of human-authored content
- **Search assistance** — helping locate relevant documents, keywords, or entity relationships within already-identified sources
- **Schema and tooling** — generating or improving validation scripts, schema definitions, and platform code
- **Summarisation** — summarising a source document to help a human decide whether it is relevant (the human reads the source; the AI helps prioritise)
- **Cross-referencing** — suggesting potential relationships between entities that a human then verifies
- **MCP querying** — using AI agents to query the evidence model via MCP tools (a designed use case)

---

## Prohibited Uses

AI tools may NOT be used for:

- **Generating evidence claims** — AI-generated evidence content cannot be entered into the evidence model. Every evidence item must be extracted by a human from a verified source.
- **Assigning confidence levels** — Confidence assessments must be made by a human applying the [METHODOLOGY.md](METHODOLOGY.md) framework. AI-suggested confidence levels are not acceptable without human verification and written rationale.
- **Producing source citations** — AI tools frequently hallucinate citations. No source may be added to the evidence model based on an AI-generated reference without independent human verification that the source exists and says what the citation claims.
- **Summarising testimony or documents as evidence** — AI summaries of primary source documents may be used to help humans navigate them, but may not substitute for the human reading the original. Evidence must be extracted from the original.
- **Representing AI output as human assessment** — AI-generated text must be disclosed if it forms part of an assessment or finding. Passing AI-generated content off as human analysis is grounds for contribution reversal.

---

## Disclosure

When AI tools contributed materially to a contribution — for example, if an AI tool drafted a significant portion of an investigation scaffold or suggested a structural approach — that should be noted in the PR description. This is not a penalty; it is a record. The platform's eventual audit trail should include what tools were used.

---

## Why These Limits

The confidence framework in [METHODOLOGY.md](METHODOLOGY.md) requires that every assessment be backed by a human reviewer who has read the evidence and applied the framework. AI confidence assessments bypass this requirement. More fundamentally, AI tools can generate plausible-sounding but false evidence — and in an evidence platform, a single false evidence item can corrupt an entire investigation's conclusions.

The platform is designed to be used *by* AI agents (via MCP) as a reliable evidence base. For that to be valuable, the evidence must have been put there by humans.

---

## Future Policy

As AI capabilities and AI-in-the-loop verification processes mature, this policy will be revisited. Any changes will be made through the governance process in [GOVERNANCE.md](GOVERNANCE.md) and documented in [DECISIONS.md](DECISIONS.md).
