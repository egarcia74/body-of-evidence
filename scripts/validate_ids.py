#!/usr/bin/env python3
"""
Body of Evidence — ID Validation

The versioning model (D-009): an entity's stable `id` is SHARED by every
version of that entity; each version file carries a unique `version_id`.
A repeated stable id across files is therefore NORMAL — it is how history
is kept. What must be unique is the (id, version_id) pair and the
version_id globally. Which version is current is the manifest's job
(checked in validate_references), not this validator's.

Checks:
1. All entity IDs match boe:<type>:<ulid> with a genuinely valid ULID
   (Crockford Base32 charset AND a first character in 0–7, since the
   48-bit ULID timestamp cannot start higher).
2. All version_ids are valid ULIDs and globally unique.
3. Files sharing a stable id declare the same entity type (guaranteed
   by the type prefix embedded in the id, checked per file).
4. No two files carry the same (id, version_id) pair.
5. The type prefix in the ID matches the entity's 'type' field.
"""

import re
from pathlib import Path
from typing import Tuple, List

from boe_files import Diagnostic, iter_entities

VALIDATOR = "ids"

# Crockford Base32 excludes I, L, O, U. First char of a ULID is 0-7
# (the 48-bit millisecond timestamp's top bits).
ULID_RE = re.compile(r'^[0-7][0-9A-HJKMNP-TV-Z]{25}$')
BOE_ID_RE = re.compile(r'^boe:([a-z_]+):([0-9A-HJKMNP-TV-Z]{26})$')


def _err(code: str, path, message: str) -> Diagnostic:
    return Diagnostic(code, VALIDATOR, str(path), message)


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
    seen_versions = {}       # version_id -> path (must be globally unique)
    seen_pairs = {}          # (id, version_id) -> path (a file duplicated verbatim)
    id_types = {}            # id -> (type, first path) (all versions must agree on type)

    for yaml_file, data in iter_entities(investigation_paths):
        entity_id = data.get("id")
        entity_type = data.get("type")
        version_id = data.get("version_id")

        if not entity_id:
            all_errors.append(_err("ID_MISSING", yaml_file, f"{yaml_file}: Missing 'id' field"))
            continue

        is_valid, error = validate_id_format(entity_id)
        if not is_valid:
            all_errors.append(_err("ID_BAD_FORMAT", yaml_file, f"{yaml_file}: {error}"))
            continue

        id_type_prefix = BOE_ID_RE.match(entity_id).group(1)
        if entity_type and entity_type != id_type_prefix:
            all_errors.append(_err(
                "ID_TYPE_PREFIX_MISMATCH", yaml_file,
                f"{yaml_file}: ID type prefix '{id_type_prefix}' does not match "
                f"entity type '{entity_type}' (ID: {entity_id})"
            ))

        # Repeated stable ids are the versioning model working as designed —
        # but every version sharing an id must be the same entity type.
        if entity_id in id_types:
            prev_type, prev_path = id_types[entity_id]
            if entity_type and prev_type and entity_type != prev_type:
                all_errors.append(_err(
                    "ID_TYPE_CONFLICT_ACROSS_VERSIONS", yaml_file,
                    f"{yaml_file}: Entity id '{entity_id}' used with type "
                    f"'{entity_type}' but '{prev_type}' in {prev_path}"
                ))
        else:
            id_types[entity_id] = (entity_type, yaml_file)

        if not version_id:
            all_errors.append(_err(
                "VERSION_ID_MISSING", yaml_file,
                f"{yaml_file}: Missing 'version_id' — every entity version "
                f"needs one (schema requires it)"
            ))
            continue

        ok, err = validate_ulid(version_id)
        if not ok:
            all_errors.append(_err("VERSION_ID_BAD_ULID", yaml_file, f"{yaml_file}: version_id {err}"))
            continue

        pair = (entity_id, version_id)
        if pair in seen_pairs:
            all_errors.append(_err(
                "ID_DUPLICATE_PAIR", yaml_file,
                f"{yaml_file}: Duplicate entity version ({entity_id} @ "
                f"{version_id}) — first seen in {seen_pairs[pair]}"
            ))
        elif version_id in seen_versions:
            all_errors.append(_err(
                "VERSION_ID_DUPLICATE", yaml_file,
                f"{yaml_file}: Duplicate version_id '{version_id}' "
                f"(first seen in {seen_versions[version_id]}) — version_ids "
                f"are globally unique, even across different entities"
            ))
        else:
            seen_pairs[pair] = yaml_file
            seen_versions[version_id] = yaml_file
            if verbose:
                print(f"    OK: {entity_id} @ {version_id}")

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
