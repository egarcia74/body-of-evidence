# Style Guide

## Purpose

Consistent style makes the evidence model easier to read, easier to validate, and harder to misinterpret. This guide covers how to write claims, evidence, source citations, and assessments.

---

## Writing Claims

Claims are the atomic unit of an investigation. Write them precisely.

### Rules

1. **One assertion per claim.** If you find yourself writing "and" in a claim, split it.
2. **Falsifiable.** The claim must be testable against evidence.
3. **Past tense for historical assertions.** "Document X stated" not "Document X states."
4. **No editorialising.** "The memo requested destruction of records" not "The memo criminally ordered a cover-up."
5. **Reference the evidence, not the conclusion.** "Source A documents that X occurred on date Y" not "X clearly happened."

### Examples

**Good:**
> "FBI memorandum dated 1963-11-22 records that the Director was notified of the assassination at 1:45 PM Central Time."

**Bad:**
> "The FBI was clearly aware of the assassination immediately and failed to act." *(bundles assertion with interpretation; not falsifiable as written)*

**Bad:**
> "The director knew and the memo proves it." *(vague; "it" is ambiguous)*

---

## Writing Evidence

Evidence is a specific extraction from a source. It is not a summary of the source.

### Rules

1. **Quote directly where possible.** Use exact quotation in the `quote` field.
2. **Specify location.** Include page number, paragraph, timestamp, or section reference.
3. **Separate what the source says from what it implies.** The `description` field captures the raw extraction; the `interpretation` field (optional) captures what you take it to mean.
4. **Do not paraphrase if you can quote.** Paraphrase compresses meaning. Quotation preserves it.

### Fields

```yaml
quote: >
  "The Director was informed at 1:45 PM Central Time on November 22, 1963."
location: "Page 3, paragraph 2"
description: >
  The memorandum records the exact time of notification to the Director.
```

---

## Writing Source Citations

Sources must have enough information that another investigator can find the same document.

### Required Fields

- `title` — The official title of the document, if it has one
- `type` — From the defined type list (see [METHODOLOGY.md](METHODOLOGY.md))
- `date` — ISO 8601 format (`YYYY-MM-DD` or `YYYY-MM` or `YYYY`)
- `provenance.origin` — Where this document comes from
- `provenance.obtained_via` — How it was obtained
- `url` or `location` — How to find it

### Optional but Strongly Encouraged

- `archive_url` — A persistent archived copy
- `authentication_notes` — How authenticity was verified

---

## Writing Assessments

Assessments are the most interpretive part of the evidence model. They require the most discipline.

### The Rationale Field

Every assessment must include a rationale. The rationale must:

1. State what evidence was weighed
2. Explain why that evidence supports the chosen confidence level
3. Note what contradictory evidence was considered
4. State what new evidence would change the confidence level

### Confidence Level Selection

When uncertain between two levels, choose the lower. Overconfident assessments are more damaging than conservative ones.

Do not round up because the evidence "feels" strong. Evidence strength is determined by applying the factors in [METHODOLOGY.md](METHODOLOGY.md).

---

## YAML Formatting

- Use 2-space indentation
- Use double-quoted strings for all text fields with special characters
- Use `|` (literal block) for multi-line prose fields
- Use `>` (folded block) for long single-paragraph fields
- ISO 8601 dates: `YYYY-MM-DD`
- All IDs on a single line: `id: "boe:claim:01HV8QKJZ9XTMK3P2R7N5W6D4F"`

---

## Naming Conventions

- Investigation slugs: `kebab-case`, descriptive, e.g., `church-committee`, `covid-origins`
- File names: match the entity type and a short description, e.g., `claim-director-notification.yaml`
- Do not use personal names as slugs for sensitive investigations

---

## Language

- British or American English consistently within a single investigation (do not mix)
- Prefer active voice
- Prefer short sentences
- Do not use loaded language (see [TERMINOLOGY.md](TERMINOLOGY.md) — Terms to Avoid)
- When precise legal or technical language is needed, use it, but define it on first use
