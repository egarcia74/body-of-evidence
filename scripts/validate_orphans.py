#!/usr/bin/env python3
"""
Body of Evidence — Orphan Evidence Validation

Detects evidence entities that are not linked to any claim.
Orphaned evidence is evidence that has been added to the repository but
not connected to any claim — it cannot contribute to any finding and
represents incomplete work.

An evidence entity is orphaned if its 'claim_ids' field is empty or absent.
(The schema already requires at least one claim_id, so this catches data
that passes schema validation but was imported incorrectly.)
"""

from pathlib import Path
from typing import Tuple, List
import yaml


def run_orphan_validation(
    investigation_paths: list[Path],
    schema_dir: Path,
    verbose: bool = False,
) -> Tuple[bool, List[str]]:
    """
    Find orphaned evidence entities.

    Returns (passed: bool, errors: list[str])
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

            if data.get("type") != "evidence":
                continue

            claim_ids = data.get("claim_ids", [])
            if not claim_ids:
                all_errors.append(
                    f"{yaml_file}: Evidence entity '{data.get('id', 'unknown')}' "
                    f"has no claim_ids — orphaned evidence"
                )
            elif verbose:
                print(f"    OK: {data.get('id')} linked to {len(claim_ids)} claim(s)")

    return len(all_errors) == 0, all_errors


if __name__ == "__main__":
    import sys
    repo_root = Path(__file__).parent.parent
    investigations_dir = repo_root / "investigations"
    inv_paths = [
        p for p in investigations_dir.iterdir()
        if p.is_dir() and not p.name.startswith("_")
    ]
    passed, errors = run_orphan_validation(inv_paths, repo_root / "schema", verbose=True)
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        sys.exit(1)
    else:
        print("No orphaned evidence found.")
        sys.exit(0)
