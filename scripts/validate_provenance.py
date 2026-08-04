#!/usr/bin/env python3
"""
Body of Evidence — Provenance Validation

Checks that Source entities have complete provenance and byte-level fixity:
- Every source has provenance.origin and provenance.obtained_via
- Tier A/B sources have authentication_notes
- Tier A/B sources have at least one artifact with a SHA-256 digest
  (a URL locates a source; a digest identifies its content)
- Tier D sources are flagged (cannot support confidence above 2)
- Tier E sources are flagged (cannot support positive conclusions)
"""

from pathlib import Path
from typing import Tuple, List

from boe_files import iter_entities


def validate_source(yaml_file: Path, data: dict) -> list[str]:
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

    quality_tier = data.get("quality_tier")

    if quality_tier in ("A", "B"):
        if not provenance.get("authentication_notes"):
            errors.append(
                f"{ctx}: Quality tier {quality_tier} source requires "
                f"provenance.authentication_notes"
            )
        artifacts = data.get("artifacts") or []
        if not any(a.get("sha256") for a in artifacts):
            errors.append(
                f"{ctx}: Quality tier {quality_tier} source requires at least "
                f"one artifact with a sha256 digest — a URL alone does not fix "
                f"the source's content"
            )

    if quality_tier == "D":
        errors.append(
            f"{ctx}: WARNING: quality_tier D (unverified) — cannot support "
            f"confidence above 2 (weak)"
        )
    elif quality_tier == "E":
        errors.append(
            f"{ctx}: WARNING: quality_tier E (disputed) — cannot support "
            f"a 'supported' conclusion"
        )

    return errors


def run_provenance_validation(
    investigation_paths: list[Path],
    schema_dir: Path,
    verbose: bool = False,
) -> Tuple[bool, List[str]]:
    all_errors = []
    for yaml_file, data in iter_entities(investigation_paths):
        if data.get("type") != "source":
            continue
        errors = validate_source(yaml_file, data)
        all_errors.extend(errors)
        if verbose and not errors:
            print(f"    OK: {data.get('id')} — provenance and fixity complete")
    return len(all_errors) == 0, all_errors


if __name__ == "__main__":
    import sys
    repo_root = Path(__file__).parent.parent
    inv_paths = [
        p for p in (repo_root / "investigations").iterdir()
        if p.is_dir() and not p.name.startswith("_")
    ]
    passed, errors = run_provenance_validation(inv_paths, repo_root / "schema", verbose=True)
    for e in errors:
        print(f"ERROR: {e}")
    sys.exit(0 if passed else 1)
