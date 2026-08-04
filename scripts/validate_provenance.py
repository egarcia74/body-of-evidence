#!/usr/bin/env python3
"""
Body of Evidence — Provenance Validation

Checks that all Source entities have the required provenance fields
documented. Sources without provenance cannot support high-confidence
assessments and represent incomplete evidence chains.

Checks:
- Every source has provenance.origin
- Every source has provenance.obtained_via
- Sources with quality_tier A or B have authentication_notes
- Sources with quality_tier D or E are flagged for review
"""

from pathlib import Path
from typing import Tuple, List
import yaml


def validate_source_provenance(yaml_file: Path, data: dict) -> list[str]:
    """Validate provenance completeness for a single source entity."""
    errors = []
    source_id = data.get("id", "unknown")
    ctx = f"{yaml_file} [{source_id}]"

    provenance = data.get("provenance")
    if not provenance:
        errors.append(f"{ctx}: Missing required 'provenance' field")
        return errors

    if not provenance.get("origin"):
        errors.append(f"{ctx}: Missing provenance.origin")

    if not provenance.get("obtained_via"):
        errors.append(f"{ctx}: Missing provenance.obtained_via")

    # Tier A and B sources should have authentication notes
    quality_tier = data.get("quality_tier")
    if quality_tier in ("A", "B") and not provenance.get("authentication_notes"):
        errors.append(
            f"{ctx}: Quality tier {quality_tier} source should have "
            f"provenance.authentication_notes documenting how authenticity was established"
        )

    # Tier D and E sources are flagged
    if quality_tier == "D":
        errors.append(
            f"{ctx}: WARNING: Source has quality_tier D (unverified). "
            f"This source cannot support confidence levels above 'plausible' (3)."
        )
    elif quality_tier == "E":
        errors.append(
            f"{ctx}: WARNING: Source has quality_tier E (disputed). "
            f"This source cannot support positive confidence assessments."
        )

    return errors


def run_provenance_validation(
    investigation_paths: list[Path],
    schema_dir: Path,
    verbose: bool = False,
) -> Tuple[bool, List[str]]:
    """
    Validate provenance completeness for all source entities.

    Returns (passed: bool, errors: list[str])

    Note: Tier D/E warnings are returned as errors for CI purposes but
    are considered warnings in context — they flag sources that need
    attention, not necessarily broken data.
    """
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

            if data.get("type") != "source":
                continue

            errors = validate_source_provenance(yaml_file, data)
            all_errors.extend(errors)
            if verbose and not errors:
                print(f"    OK: {data.get('id')} — provenance complete")

    return len(all_errors) == 0, all_errors


if __name__ == "__main__":
    import sys
    repo_root = Path(__file__).parent.parent
    investigations_dir = repo_root / "investigations"
    inv_paths = [
        p for p in investigations_dir.iterdir()
        if p.is_dir() and not p.name.startswith("_")
    ]
    passed, errors = run_provenance_validation(inv_paths, repo_root / "schema", verbose=True)
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        sys.exit(1)
    else:
        print("All provenance validation passed.")
        sys.exit(0)
