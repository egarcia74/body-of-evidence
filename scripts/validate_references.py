#!/usr/bin/env python3
"""
Body of Evidence — Reference Validation

Checks that every ID referenced in any entity file resolves to an existing
entity. Catches broken cross-references before they make it into the repository.

Checks:
- evidence.source_id → source exists
- evidence.claim_ids → each claim exists
- claim.evidence_ids → each evidence exists
- claim.assessment_ids → each assessment exists
- claim.investigation_id → investigation exists
- assessment.claim_id → claim exists
- finding.claim_ids → each claim exists
- finding.investigation_id → investigation exists
- revision.entity_id → entity exists
- review.subject_id → entity exists
- relationship.from_id, to_id → entities exist
- timeline.event_ids → each event exists
- person.organisations → each organisation exists
"""

from pathlib import Path
from typing import Tuple, List
import yaml


def collect_all_ids(investigation_paths: list[Path]) -> set[str]:
    """Collect all entity IDs defined across all investigations."""
    all_ids = set()
    for inv_path in investigation_paths:
        for yaml_file in inv_path.rglob("*.yaml"):
            try:
                with open(yaml_file) as f:
                    data = yaml.safe_load(f)
                if isinstance(data, dict) and "id" in data:
                    all_ids.add(data["id"])
            except yaml.YAMLError:
                continue
    return all_ids


def check_ref(ref_id: str, all_ids: set[str], context: str, errors: list[str]):
    """Check that a reference resolves and add to errors if not."""
    if ref_id and ref_id not in all_ids:
        errors.append(f"{context}: Referenced ID '{ref_id}' not found")


def check_ref_list(ref_ids: list, all_ids: set[str], context: str, errors: list[str]):
    """Check a list of references."""
    if not ref_ids:
        return
    for ref_id in ref_ids:
        check_ref(ref_id, all_ids, context, errors)


def validate_references_in_file(
    yaml_file: Path,
    data: dict,
    all_ids: set[str],
) -> list[str]:
    """Validate all references within a single entity file."""
    errors = []
    entity_type = data.get("type", "unknown")
    ctx = str(yaml_file)

    if entity_type == "evidence":
        check_ref(data.get("source_id"), all_ids, f"{ctx}[source_id]", errors)
        check_ref_list(data.get("claim_ids", []), all_ids, f"{ctx}[claim_ids]", errors)

    elif entity_type == "claim":
        check_ref(data.get("investigation_id"), all_ids, f"{ctx}[investigation_id]", errors)
        check_ref_list(data.get("evidence_ids", []), all_ids, f"{ctx}[evidence_ids]", errors)
        check_ref_list(data.get("assessment_ids", []), all_ids, f"{ctx}[assessment_ids]", errors)
        check_ref_list(data.get("related_claim_ids", []), all_ids, f"{ctx}[related_claim_ids]", errors)

    elif entity_type == "assessment":
        check_ref(data.get("claim_id"), all_ids, f"{ctx}[claim_id]", errors)
        check_ref_list(data.get("evidence_considered", []), all_ids, f"{ctx}[evidence_considered]", errors)
        check_ref_list(data.get("contradictory_evidence", []), all_ids, f"{ctx}[contradictory_evidence]", errors)

    elif entity_type == "finding":
        check_ref(data.get("investigation_id"), all_ids, f"{ctx}[investigation_id]", errors)
        check_ref_list(data.get("claim_ids", []), all_ids, f"{ctx}[claim_ids]", errors)

    elif entity_type == "timeline":
        check_ref(data.get("investigation_id"), all_ids, f"{ctx}[investigation_id]", errors)
        check_ref_list(data.get("event_ids", []), all_ids, f"{ctx}[event_ids]", errors)

    elif entity_type == "revision":
        check_ref(data.get("entity_id"), all_ids, f"{ctx}[entity_id]", errors)
        if data.get("superseded_entity_id"):
            check_ref(data["superseded_entity_id"], all_ids, f"{ctx}[superseded_entity_id]", errors)

    elif entity_type == "review":
        check_ref(data.get("subject_id"), all_ids, f"{ctx}[subject_id]", errors)

    elif entity_type == "relationship":
        check_ref(data.get("from_id"), all_ids, f"{ctx}[from_id]", errors)
        check_ref(data.get("to_id"), all_ids, f"{ctx}[to_id]", errors)

    elif entity_type == "person":
        check_ref_list(data.get("organisations", []), all_ids, f"{ctx}[organisations]", errors)

    return errors


def run_reference_validation(
    investigation_paths: list[Path],
    schema_dir: Path,
    verbose: bool = False,
) -> Tuple[bool, List[str]]:
    """
    Run reference integrity validation.

    Returns (passed: bool, errors: list[str])
    """
    # First pass: collect all defined IDs
    all_ids = collect_all_ids(investigation_paths)

    if verbose:
        print(f"    Found {len(all_ids)} defined entity IDs")

    # Second pass: validate all references
    all_errors = []
    for inv_path in investigation_paths:
        for yaml_file in sorted(inv_path.rglob("*.yaml")):
            try:
                with open(yaml_file) as f:
                    data = yaml.safe_load(f)
            except yaml.YAMLError:
                continue

            if not isinstance(data, dict):
                continue

            errors = validate_references_in_file(yaml_file, data, all_ids)
            all_errors.extend(errors)

    return len(all_errors) == 0, all_errors


if __name__ == "__main__":
    import sys
    repo_root = Path(__file__).parent.parent
    investigations_dir = repo_root / "investigations"
    inv_paths = [
        p for p in investigations_dir.iterdir()
        if p.is_dir() and not p.name.startswith("_")
    ]
    passed, errors = run_reference_validation(inv_paths, repo_root / "schema", verbose=True)
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        sys.exit(1)
    else:
        print("All reference validation passed.")
        sys.exit(0)
