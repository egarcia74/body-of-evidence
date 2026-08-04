#!/usr/bin/env python3
"""
Body of Evidence — Master Validation Runner

Runs all validation checks against the evidence data. Called by CI and
can be run locally before submitting a PR.

Usage:
    python scripts/validate.py
    python scripts/validate.py --investigation church-committee
    python scripts/validate.py --check schema
    python scripts/validate.py --verbose

Exit codes:
    0 — All checks passed
    1 — One or more checks failed
"""

import argparse
import sys
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Add scripts/ to path for imports
SCRIPTS_DIR = Path(__file__).parent
REPO_ROOT = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from validate_schema import run_schema_validation
from validate_ids import run_id_validation
from validate_references import run_reference_validation
from validate_orphans import run_orphan_validation
from validate_provenance import run_provenance_validation


def parse_args():
    parser = argparse.ArgumentParser(
        description="Body of Evidence validation suite"
    )
    parser.add_argument(
        "--investigation",
        help="Validate only a specific investigation by slug",
        default=None,
    )
    parser.add_argument(
        "--check",
        choices=["schema", "ids", "references", "orphans", "provenance", "all"],
        default="all",
        help="Run only a specific check (default: all)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output for each check",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    console = Console() if RICH_AVAILABLE else None

    investigations_dir = REPO_ROOT / "investigations"
    schema_dir = REPO_ROOT / "schema"

    if args.investigation:
        investigation_paths = [investigations_dir / args.investigation]
        if not investigation_paths[0].exists():
            print(f"ERROR: Investigation '{args.investigation}' not found at {investigation_paths[0]}")
            sys.exit(1)
    else:
        investigation_paths = [
            p for p in investigations_dir.iterdir()
            if p.is_dir() and not p.name.startswith("_")
        ]

    if not investigation_paths:
        print("No investigations found to validate.")
        sys.exit(0)

    checks = {
        "schema": run_schema_validation,
        "ids": run_id_validation,
        "references": run_reference_validation,
        "orphans": run_orphan_validation,
        "provenance": run_provenance_validation,
    }

    if args.check != "all":
        checks = {args.check: checks[args.check]}

    results = {}
    all_passed = True

    print(f"\nBody of Evidence Validation")
    print(f"Validating {len(investigation_paths)} investigation(s)")
    print("=" * 60)

    for check_name, check_fn in checks.items():
        print(f"\n[{check_name.upper()}]")
        passed, errors = check_fn(
            investigation_paths=investigation_paths,
            schema_dir=schema_dir,
            verbose=args.verbose,
        )
        results[check_name] = {"passed": passed, "errors": errors}
        if not passed:
            all_passed = False
            for error in errors:
                print(f"  ERROR: {error}")
        else:
            print(f"  OK — all {check_name} checks passed")

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All validation checks passed")
        sys.exit(0)
    else:
        failed = [k for k, v in results.items() if not v["passed"]]
        print(f"✗ Validation failed: {', '.join(failed)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
