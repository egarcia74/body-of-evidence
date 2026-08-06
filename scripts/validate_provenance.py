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
    ValidationContext,
    preflight_diagnostics,
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
    for yaml_file, data in context.entities():
        if data.get("type") != "source":
            continue
        errors = validate_source(yaml_file, data)
        all_errors.extend(errors)
        if verbose and not errors:
            print(f"    OK: {data.get('id')} — provenance and fixity complete")
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
        "validate_provenance.py is not a command-line entry point.\n"
        "Run:  python3 scripts/validate.py --check provenance [--root DIR]"
    )
