#!/usr/bin/env python3
"""
Body of Evidence — Master Validation Runner

Runs all validation checks against the evidence data.

A validator that reports success without validating anything is worse than
no validator. This runner therefore:
- FAILS by default if there are no investigations to validate
  (pass --allow-empty to permit an empty investigations/ directory,
  which CI does only in combination with --self-test)
- Provides --self-test, which proves the validators work by checking that
  fixtures/valid/ passes every check and every fixtures/invalid/* package
  fails at least one check.

Usage:
    python scripts/validate.py                     # validate all investigations
    python scripts/validate.py --investigation X   # validate one investigation
    python scripts/validate.py --self-test         # prove validators catch what they claim to
    python scripts/validate.py --allow-empty       # do not fail on zero investigations

Exit codes:
    0 — All checks passed (and, for --self-test, all invalid fixtures were rejected)
    1 — One or more checks failed, or nothing was validated
"""

import argparse
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
REPO_ROOT = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from boe_files import ValidationContext
from validate_schema import run_schema_validation
from validate_ids import run_id_validation
from validate_references import run_reference_validation
from validate_orphans import run_orphan_validation
from validate_provenance import run_provenance_validation

CHECKS = {
    "schema": run_schema_validation,
    "ids": run_id_validation,
    "references": run_reference_validation,
    "orphans": run_orphan_validation,
    "provenance": run_provenance_validation,
}


def run_all_checks(paths: list[Path], schema_dir: Path, verbose: bool, checks: dict) -> tuple[bool, dict]:
    """
    Run the given checks over the given paths. Returns (all_passed, results).

    Builds ONE ValidationContext (one filesystem walk and one read of each
    document per package root) and passes it to every check, rather than
    letting each run_*_validation build its own — a whole-CLI-run invocation
    (the common case: all five checks, or --self-test's per-fixture pass)
    previously still walked every package once per validator, even though
    each validator's OWN walk count had already been reduced to one
    (tenth-pass review CodeRabbit follow-up to D-025/M-24: "one walk per
    package" was true per validator call, not true for a full run).

    Sharing the context is also what makes all five checks inspect the same
    bytes: the context carries parsed document content, so no validator
    re-opens a path another validator already read (eleventh-pass M-29).
    """
    context = ValidationContext.for_paths(paths)
    results = {}
    all_passed = True
    for check_name, check_fn in checks.items():
        passed, errors = check_fn(context=context, schema_dir=schema_dir, verbose=verbose)
        results[check_name] = {"passed": passed, "errors": errors}
        if not passed:
            all_passed = False
    return all_passed, results


def print_results(results: dict):
    for check_name, result in results.items():
        if result["passed"]:
            print(f"  [{check_name}] OK")
        else:
            print(f"  [{check_name}] FAILED")
            for error in result["errors"]:
                print(f"      {error}")


def self_test(schema_dir: Path, verbose: bool) -> bool:
    """
    Prove the validators are not vacuous:
    - fixtures/valid/* must pass ALL checks
    - each fixtures/invalid/* must fail AT LEAST ONE check
    """
    fixtures_dir = REPO_ROOT / "fixtures"
    valid_dir = fixtures_dir / "valid"
    invalid_dir = fixtures_dir / "invalid"
    ok = True

    valid_packages = sorted(p for p in valid_dir.iterdir() if p.is_dir()) if valid_dir.exists() else []
    invalid_packages = sorted(p for p in invalid_dir.iterdir() if p.is_dir()) if invalid_dir.exists() else []

    if not valid_packages or not invalid_packages:
        print("SELF-TEST FAILED: fixtures/valid/ and fixtures/invalid/ must both contain packages")
        return False

    print(f"\n[SELF-TEST] {len(valid_packages)} valid, {len(invalid_packages)} invalid fixture package(s)")

    for pkg in valid_packages:
        passed, results = run_all_checks([pkg], schema_dir, verbose, CHECKS)
        if passed:
            print(f"  valid/{pkg.name}: passes all checks — OK")
        else:
            ok = False
            print(f"  valid/{pkg.name}: FAILED checks that should pass:")
            print_results({k: v for k, v in results.items() if not v["passed"]})

    for pkg in invalid_packages:
        passed, results = run_all_checks([pkg], schema_dir, False, CHECKS)
        if not passed:
            failing = [k for k, v in results.items() if not v["passed"]]
            print(f"  invalid/{pkg.name}: correctly rejected by [{', '.join(failing)}] — OK")
        else:
            ok = False
            print(f"  invalid/{pkg.name}: WAS NOT REJECTED — the validators have a hole")

    return ok


def main():
    parser = argparse.ArgumentParser(description="Body of Evidence validation suite")
    parser.add_argument("--investigation", default=None,
                        help="Validate only a specific investigation by slug")
    parser.add_argument("--check", choices=[*CHECKS.keys(), "all"], default="all",
                        help="Run only a specific check (default: all)")
    parser.add_argument("--self-test", action="store_true",
                        help="Verify validators against valid/invalid fixtures")
    parser.add_argument("--allow-empty", action="store_true",
                        help="Do not fail when there are no investigations to validate")
    parser.add_argument("--root", default=None, type=Path,
                        help="Directory containing investigation package directories "
                             "(default: <repo>/investigations). Lets the production "
                             "multi-package discovery path be exercised against a "
                             "throwaway directory in tests, without mutating the repo "
                             "(fifth-pass review M-15).")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    schema_dir = REPO_ROOT / "schema"
    exit_code = 0

    if args.self_test and not self_test(schema_dir, args.verbose):
        exit_code = 1

    investigations_dir = args.root if args.root is not None else REPO_ROOT / "investigations"

    # Validate --root explicitly rather than letting iterdir() raise —
    # an unhandled traceback is not a diagnostic (sixth-pass review M-18).
    # Also refuse a symlinked root, consistent with the package-root
    # symlink policy applied to individual investigation directories.
    if args.root is not None:
        if not investigations_dir.exists():
            print(f"ERROR: --root '{investigations_dir}' does not exist")
            sys.exit(1)
        if investigations_dir.is_symlink():
            print(f"ERROR: --root '{investigations_dir}' is a symlink — refusing "
                  f"(it could point anywhere on disk)")
            sys.exit(1)
        if not investigations_dir.is_dir():
            print(f"ERROR: --root '{investigations_dir}' is not a directory")
            sys.exit(1)

    # Enumeration itself can still fail (e.g. an unreadable directory raises
    # PermissionError) even after the existence/type checks above — that
    # must also become a diagnostic, not a traceback (seventh-pass review
    # M-21, the same principle as M-18 one level down).
    try:
        if args.investigation:
            investigation_paths = [investigations_dir / args.investigation]
            # A DANGLING symlink fails .exists() too — but it must still
            # reach run_reference_validation's INVESTIGATION_ROOT_SYMLINK
            # check rather than be reported as merely "not found" (eighth-pass
            # review H-22: a dangling package-root symlink is environment-
            # dependent — it may resolve to something entirely different on
            # another machine, so it must never be silently invisible).
            if not investigation_paths[0].exists() and not investigation_paths[0].is_symlink():
                print(f"ERROR: Investigation '{args.investigation}' not found")
                sys.exit(1)
        else:
            # Same H-22 reasoning for default discovery: p.is_dir() is False
            # for a dangling symlink, which would otherwise silently vanish
            # before the symlink validator ever sees it.
            investigation_paths = sorted(
                p for p in investigations_dir.iterdir()
                if not p.name.startswith("_") and (p.is_symlink() or p.is_dir())
            )
    except OSError as e:
        print(f"ERROR: Could not enumerate '{investigations_dir}': {e}")
        sys.exit(1)

    checks = CHECKS if args.check == "all" else {args.check: CHECKS[args.check]}

    print(f"\nBody of Evidence Validation — {len(investigation_paths)} investigation(s)")
    print("=" * 60)

    if not investigation_paths:
        if args.allow_empty:
            print("No investigations present. Skipping (--allow-empty).")
        else:
            print("ERROR: No investigations to validate. A green result that")
            print("validated nothing is not a result. Pass --allow-empty if this")
            print("is intentional (e.g., pre-content CI combined with --self-test).")
            exit_code = 1
    else:
        passed, results = run_all_checks(investigation_paths, schema_dir, args.verbose, checks)
        print_results(results)
        if not passed:
            exit_code = 1

    print("=" * 60)
    print("PASSED" if exit_code == 0 else "FAILED")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
