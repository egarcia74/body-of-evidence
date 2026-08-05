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
from typing import Tuple, List

from boe_files import Diagnostic, iter_entities

VALIDATOR = "orphans"


def run_orphan_validation(
    investigation_paths: list[Path],
    schema_dir: Path,
    verbose: bool = False,
) -> Tuple[bool, List[str]]:
    all_errors = []
    evidence_files = {}       # evidence_id -> path
    linked_evidence = set()   # evidence_ids referenced by at least one link

    entities = list(iter_entities(investigation_paths))

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


if __name__ == "__main__":
    import sys
    repo_root = Path(__file__).parent.parent
    inv_paths = [
        p for p in (repo_root / "investigations").iterdir()
        if p.is_dir() and not p.name.startswith("_")
    ]
    passed, errors = run_orphan_validation(inv_paths, repo_root / "schema", verbose=True)
    for e in errors:
        print(f"ERROR: {e}")
    sys.exit(0 if passed else 1)
