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
- [ ] All evidence items are tied to at least one claim (no orphans)
- [ ] All sources have documented provenance (origin + obtained_via)
- [ ] All assessments include a confidence rationale (not just a level)
- [ ] Contradictory evidence is documented, not omitted
- [ ] No existing published entities were silently edited (use Revisions)
- [ ] All IDs follow `boe:<type>:<ulid>` format
- [ ] All referenced IDs exist in the repository

## Validation

- [ ] `python scripts/validate.py` passes locally

## Conflicts of Interest

<!-- State any conflicts of interest with the subject of this investigation, or "none". -->

Conflict of interest: 

## Related Issues

<!-- Link to related issues: Closes #123, Relates to #456 -->
