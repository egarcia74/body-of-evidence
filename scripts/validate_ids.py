#!/usr/bin/env python3
"""
Body of Evidence — ID Validation

Checks:
1. All entity IDs match boe:<type>:<ulid> with a genuinely valid ULID
   (Crockford Base32 charset AND a first character in 0–7, since the
   48-bit ULID timestamp cannot start higher).
2. All version_ids are valid ULIDs.
3. No duplicate entity IDs across the scanned scope.
4. No duplicate version_ids across the scanned scope.
5. The type prefix in the ID matches the entity's 'type' field.
"""

import re
from pathlib import Path
from typing import Tuple, List

from boe_files import iter_entities

# Crockford Base32 excludes I, L, O, U. First char of a ULID is 0-7
# (the 48-bit millisecond timestamp's top bits).
ULID_RE = re.compile(r'^[0-7][0-9A-HJKMNP-TV-Z]{25}$')
BOE_ID_RE = re.compile(r'^boe:([a-z_]+):([0-9A-HJKMNP-TV-Z]{26})$')


def validate_ulid(value: str) -> tuple[bool, str]:
    if not ULID_RE.match(value):
        return False, (
            f"'{value}' is not a valid ULID (26 chars, Crockford Base32 "
            f"excluding I/L/O/U, first char 0-7)"
        )
    return True, ""


def validate_id_format(entity_id: str) -> tuple[bool, str]:
    match = BOE_ID_RE.match(entity_id)
    if not match:
        return False, f"ID '{entity_id}' does not match pattern boe:<type>:<ulid>"
    ok, err = validate_ulid(match.group(2))
    if not ok:
        return False, f"ID '{entity_id}': {err}"
    return True, ""


def run_id_validation(
    investigation_paths: list[Path],
    schema_dir: Path,
    verbose: bool = False,
) -> Tuple[bool, List[str]]:
    all_errors = []
    seen_ids = {}
    seen_versions = {}

    for yaml_file, data in iter_entities(investigation_paths):
        entity_id = data.get("id")
        entity_type = data.get("type")
        version_id = data.get("version_id")

        if not entity_id:
            all_errors.append(f"{yaml_file}: Missing 'id' field")
            continue

        is_valid, error = validate_id_format(entity_id)
        if not is_valid:
            all_errors.append(f"{yaml_file}: {error}")
            continue

        id_type_prefix = BOE_ID_RE.match(entity_id).group(1)
        if entity_type and entity_type != id_type_prefix:
            all_errors.append(
                f"{yaml_file}: ID type prefix '{id_type_prefix}' does not match "
                f"entity type '{entity_type}' (ID: {entity_id})"
            )

        if version_id:
            ok, err = validate_ulid(version_id)
            if not ok:
                all_errors.append(f"{yaml_file}: version_id {err}")
            elif version_id in seen_versions:
                all_errors.append(
                    f"{yaml_file}: Duplicate version_id '{version_id}' "
                    f"(first seen in {seen_versions[version_id]})"
                )
            else:
                seen_versions[version_id] = yaml_file

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
    inv_paths = [
        p for p in (repo_root / "investigations").iterdir()
        if p.is_dir() and not p.name.startswith("_")
    ]
    passed, errors = run_id_validation(inv_paths, repo_root / "schema", verbose=True)
    for e in errors:
        print(f"ERROR: {e}")
    sys.exit(0 if passed else 1)
