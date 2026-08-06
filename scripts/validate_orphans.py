#!/usr/bin/env python3
"""
Body of Evidence — Orphan Evidence Validation

Evidence carries no claim references (polarity lives on ClaimEvidenceLink
entities). An evidence entity is therefore orphaned when NO link references
it. Orphaned evidence cannot contribute to any assessment and represents
incomplete work.

Also detects orphaned links: a claim_evidence_link whose claim or evidence
reference is missing is caught by reference validation; a link is flagged
here if it exists but its evidence is never used by any assessment — as a
warning only (unassessed evidence is normal during drafting).
"""

from pathlib import Path

from boe_files import (
    Diagnostic,
    ValidationContext,
    preflight_diagnostics,
)

VALIDATOR = "orphans"


def run_orphan_validation(
    context: ValidationContext,
    schema_dir: Path,
    verbose: bool = False,
) -> tuple[bool, list[Diagnostic]]:
    """`context` is the single, self-consistent input to this check: it
    owns both the package roots and the one-walk-one-read discovery of
    each (eleventh-pass review H-23 — this used to take `investigation_paths`
    and an optional `discoveries` list with nothing checking they described
    the same packages, so an empty discovery could silently certify a
    known-invalid package). Build it once per run with
    ValidationContext.for_paths and share it across all five checks.

    Preflight runs first, from that same discovery, so this check fails
    closed on a symlinked root, an internal symlink, or an unreadable
    subtree rather than certifying a package it did not completely or
    safely inspect (eighth-pass M-22, tenth-pass M-24/M-27)."""
    all_errors = preflight_diagnostics(context, VALIDATOR)
    evidence_files = {}       # evidence_id -> path
    linked_evidence = set()   # evidence_ids referenced by at least one link

    entities = list(context.entities())

    for path, data in entities:
        if data.get("type") == "evidence" and "id" in data:
            evidence_files[data["id"]] = path
        elif data.get("type") == "claim_evidence_link":
            ev = data.get("evidence_id")
            if ev:
                linked_evidence.add(ev)

    for evidence_id, path in sorted(evidence_files.items()):
        if evidence_id not in linked_evidence:
            all_errors.append(Diagnostic(
                "ORPHAN_EVIDENCE", VALIDATOR, str(path),
                f"{path}: Evidence '{evidence_id}' is not referenced by any "
                f"claim_evidence_link — orphaned evidence"
            ))
        elif verbose:
            print(f"    OK: {evidence_id} is linked")

    return len(all_errors) == 0, all_errors


# This module is not a CLI. `scripts/validate.py` is the only entry point;
# each of these modules used to carry its own runner that re-implemented
# package discovery as `p.is_dir()` — weaker than validate.py's
# `p.is_symlink() or p.is_dir()`, i.e. carrying the exact dangling-symlink
# blindness D-023/H-22 fixed — and had no empty-run guard, so it could report
# success having validated nothing. The D-026 signature change left four of
# them crashing on startup for a whole commit because nothing executed them
# (D-027/M-31). Refusing loudly beats both a crash and a silent exit 0.
if __name__ == "__main__":
    raise SystemExit(
        "validate_orphans.py is not a command-line entry point.\n"
        "Run:  python3 scripts/validate.py --check orphans [--root DIR]"
    )
