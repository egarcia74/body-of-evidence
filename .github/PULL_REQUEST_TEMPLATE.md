## Summary

<!-- What does this PR change and why? -->

## Type of Change

- [ ] New evidence (adding evidence to an existing investigation)
- [ ] New investigation (new investigation scaffold)
- [ ] Schema change (additions or corrections to JSON Schema)
- [ ] Bug fix (broken reference, typo, validation error)
- [ ] Documentation update
- [ ] Platform tooling (scripts, CI, GitHub config)

## Methodology Checklist

For PRs that touch investigation data:

- [ ] All claims are falsifiable and atomic (one assertion per claim)
- [ ] Every evidence entity is referenced by at least one ClaimEvidenceLink (no orphans); polarity lives on links, never on evidence
- [ ] All sources have documented provenance (origin + obtained_via); tier A/B sources have a SHA-256 artifact digest computed from the actual retrieved bytes
- [ ] All assessments record conclusion, confidence (with paired label), dispute status, and a substantive rationale
- [ ] Known contradicting links are included in assessments, not omitted
- [ ] No published entity version file was modified — changes create a new version_id, a Revision entity, and a manifest update
- [ ] `package.yaml` lists exactly one current version per entity and matches the files it references
- [ ] All IDs follow `boe:<type>:<ulid>`; all version_ids are new ULIDs

## Validation

- [ ] `python scripts/validate.py --self-test` and `python scripts/validate.py` pass locally

## Declarations

- [ ] This PR contains no confidential material and nothing the contributors lack the right to publish
- [ ] AI assistance is disclosed below per AI_GUIDELINES.md

AI assistance disclosure (or "none"): 

Conflict of interest (or "none"): 

## Related Issues

<!-- Link to related issues: Closes #123, Relates to #456 -->
