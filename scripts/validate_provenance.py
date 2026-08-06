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

from boe_files import (
    Diagnostic,
    iter_entities,
    symlinked_root_diagnostics,
    traversal_error_diagnostics,
)

VALIDATOR = "provenance"


def _err(code: str, path, message: str) -> Diagnostic:
    return Diagnostic(code, VALIDATOR, str(path), message)


def validate_source(yaml_file: Path, data: dict) -> list[Diagnostic]:
    errors = []
    source_id = data.get("id", "unknown")
    ctx = f"{yaml_file} [{source_id}]"

    provenance = data.get("provenance")
    if not provenance:
        errors.append(_err("PROVENANCE_MISSING", yaml_file, f"{ctx}: Missing required 'provenance' field"))
        return errors

    if not provenance.get("origin"):
        errors.append(_err("PROVENANCE_MISSING_ORIGIN", yaml_file, f"{ctx}: Missing provenance.origin"))
    if not provenance.get("obtained_via"):
        errors.append(_err("PROVENANCE_MISSING_OBTAINED_VIA", yaml_file, f"{ctx}: Missing provenance.obtained_via"))

    quality_tier = data.get("quality_tier")

    if quality_tier in ("A", "B"):
        if not provenance.get("authentication_notes"):
            errors.append(_err(
                "PROVENANCE_MISSING_AUTH_NOTES", yaml_file,
                f"{ctx}: Quality tier {quality_tier} source requires "
                f"provenance.authentication_notes"
            ))
        artifacts = data.get("artifacts") or []
        if not any(a.get("sha256") for a in artifacts):
            errors.append(_err(
                "PROVENANCE_MISSING_DIGEST", yaml_file,
                f"{ctx}: Quality tier {quality_tier} source requires at least "
                f"one artifact with a sha256 digest — a URL alone does not fix "
                f"the source's content"
            ))

    # Tier D/E are NOT errors — a disputed source is a legitimate, explicitly
    # uncertain part of the record. They are printed as advisories so the
    # confidence-ceiling rules are visible, but they never fail validation.
    if quality_tier == "D":
        print(
            f"    ADVISORY: {ctx}: quality_tier D (unverified) — cannot "
            f"support confidence above 2 (weak)"
        )
    elif quality_tier == "E":
        print(
            f"    ADVISORY: {ctx}: quality_tier E (disputed) — cannot "
            f"support a 'supported' conclusion"
        )

    return errors


def run_provenance_validation(
    investigation_paths: list[Path],
    schema_dir: Path,
    verbose: bool = False,
) -> tuple[bool, list[Diagnostic]]:
    # A symlinked root or an unreadable subtree must not let this check
    # certify a package it did not completely inspect (eighth-pass review
    # M-22 follow-up: fail-closed traversal/root-rejection must cover
    # every validator that walks entity files, not just references).
    all_errors = symlinked_root_diagnostics(investigation_paths, VALIDATOR)
    all_errors += traversal_error_diagnostics(investigation_paths, VALIDATOR)
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
