#!/usr/bin/env python3
"""
Body of Evidence — ID Validation

Checks:
1. All IDs match the boe:<type>:<ulid> format
2. No duplicate IDs across the repository
3. The 'type' in the ID matches the entity's 'type' field
"""

import re
from pathlib import Path
from typing import Tuple, List
from collections import defaultdict

import yaml

# ULID character set: Crockford Base32 (excludes I, L, O, U)
ULID_PATTERN = re.compile(r'^boe:([a-z_]+):([0-9A-HJKMNP-TV-Z]{26})$')

# Map of entity type field values to the expected type prefix in IDs
TYPE_TO_PREFIX = {
    "investigation": "investigation",
    "claim": "claim",
    "evidence": "evidence",
    "source": "source",
    "person": "person",
    "organisation": "organisation",
    "event": "event",
    "timeline": "timeline",
    "assessment": "assessment",
    "relationship": "relationship",
    "revision": "revision",
    "review": "review",
    "finding": "finding",
}


def validate_id_format(entity_id: str) -> tuple[bool, str]:
    """
    Validate an ID against the boe:<type>:<ulid> pattern.
    Returns (is_valid, error_message)
    """
    match = ULID_PATTERN.match(entity_id)
    if not match:
        return False, f"ID '{entity_id}' does not match pattern boe:<type>:<ulid>"
    return True, ""


def run_id_validation(
    investigation_paths: list[Path],
    schema_dir: Path,
    verbose: bool = False,
) -> Tuple[bool, List[str]]:
    """
    Run ID format and uniqueness validation.

    Returns (passed: bool, errors: list[str])
    """
    all_errors = []
    seen_ids = {}  # id -> file path

    for inv_path in investigation_paths:
        for yaml_file in sorted(inv_path.rglob("*.yaml")):
            try:
                with open(yaml_file) as f:
                    data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                all_errors.append(f"{yaml_file}: YAML parse error: {e}")
                continue

            if not isinstance(data, dict):
                continue

            entity_id = data.get("id")
            entity_type = data.get("type")

            if not entity_id:
                all_errors.append(f"{yaml_file}: Missing 'id' field")
                continue

            # Format check
            is_valid, error = validate_id_format(entity_id)
            if not is_valid:
                all_errors.append(f"{yaml_file}: {error}")
                continue

            # Type consistency check
            match = ULID_PATTERN.match(entity_id)
            id_type_prefix = match.group(1)
            if entity_type and entity_type != id_type_prefix:
                all_errors.append(
                    f"{yaml_file}: ID type prefix '{id_type_prefix}' does not match "
                    f"entity type '{entity_type}' (ID: {entity_id})"
                )

            # Duplicate check
            if entity_id in seen_ids:
                all_errors.append(
                    f"{yaml_file}: Duplicate ID '{entity_id}' "
                    f"(first seen in {seen_ids[entity_id]})"
                )
            else:
                seen_ids[entity_id] = yaml_file
                if verbose:
                    print(f"    OK: {entity_id}")

    return len(all_errors) == 0, all_errors


if __name__ == "__main__":
    import sys
    repo_root = Path(__file__).parent.parent
    investigations_dir = repo_root / "investigations"
    inv_paths = [
        p for p in investigations_dir.iterdir()
        if p.is_dir() and not p.name.startswith("_")
    ]
    passed, errors = run_id_validation(inv_paths, repo_root / "schema", verbose=True)
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        sys.exit(1)
    else:
        print("All ID validation passed.")
        sys.exit(0)
