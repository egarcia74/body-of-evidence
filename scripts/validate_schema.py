#!/usr/bin/env python3
"""
Body of Evidence — Schema Validation

Validates all YAML entity files against their JSON Schema definitions,
and package manifests against package.schema.json.

Each entity YAML file must have a 'type' field mapping to schema/<type>.schema.json.
Package manifests (package.yaml) are validated against schema/package.schema.json.
"""

import json
from pathlib import Path

from boe_files import (
    Diagnostic,
    discover_packages,
    entity_files_from,
    find_manifest,
    load_yaml,
    preflight_diagnostics,
)

try:
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False

VALIDATOR = "schema"


def _err(code: str, path, message: str, location: str = "") -> Diagnostic:
    return Diagnostic(code, VALIDATOR, str(path), message, location)


def build_registry(schema_dir: Path):
    """Register all local schemas so $refs resolve locally, never over the network."""
    registry = Registry()
    for schema_path in schema_dir.glob("*.schema.json"):
        with open(schema_path) as f:
            schema = json.load(f)
        resource = Resource.from_contents(schema)
        # Register under both the $id and the bare filename used in $refs
        registry = registry.with_resource(schema["$id"], resource)
        registry = registry.with_resource(schema_path.name, resource)
    return registry


def load_schema(schema_dir: Path, entity_type: str) -> dict | None:
    schema_path = schema_dir / f"{entity_type}.schema.json"
    if not schema_path.exists():
        return None
    with open(schema_path) as f:
        return json.load(f)


def validate_data(data: dict, schema: dict, registry, context: str) -> list[Diagnostic]:
    """Validate one document, reporting ALL errors, not just the first."""
    validator = Draft202012Validator(schema, registry=registry)
    errors = []
    for error in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        json_path = " > ".join(str(p) for p in error.path) or "(root)"
        errors.append(_err(
            "SCHEMA_VALIDATION_ERROR", context,
            f"{context}: {error.message} (at: {json_path})",
            json_path,
        ))
    return errors


def run_schema_validation(
    investigation_paths: list[Path],
    schema_dir: Path,
    verbose: bool = False,
) -> tuple[bool, list[Diagnostic]]:
    """Returns (passed, errors). Counts validated files so callers can detect vacuous runs."""
    if not JSONSCHEMA_AVAILABLE:
        return False, [_err(
            "SCHEMA_JSONSCHEMA_UNAVAILABLE", "<repo>",
            "jsonschema>=4.18 not installed — run: pip install -r scripts/requirements.txt"
        )]

    registry = build_registry(schema_dir)
    # One walk per package root produces every preflight fact (symlinked
    # root, internal symlink, unreadable subtree) this check must fail
    # closed on, instead of certifying a package it did not completely or
    # safely inspect (eighth-pass M-22, tenth-pass M-24/M-27 — every
    # standalone check shares one discovery, not its own walk).
    discoveries = discover_packages(investigation_paths)
    all_errors = preflight_diagnostics(discoveries, VALIDATOR)
    validated = 0

    # Entity files
    for yaml_file in entity_files_from(discoveries):
        data, error = load_yaml(yaml_file)
        if error:
            all_errors.append(_err("YAML_PARSE_ERROR", yaml_file, error))
            continue
        if data is None:
            continue
        entity_type = data.get("type")
        if not entity_type:
            all_errors.append(_err(
                "SCHEMA_MISSING_TYPE", yaml_file, f"{yaml_file}: Missing required 'type' field"
            ))
            continue
        schema = load_schema(schema_dir, entity_type)
        if schema is None:
            all_errors.append(_err(
                "SCHEMA_UNKNOWN_TYPE", yaml_file,
                f"{yaml_file}: No schema for type '{entity_type}' "
                f"(expected schema/{entity_type}.schema.json)"
            ))
            continue
        errors = validate_data(data, schema, registry, str(yaml_file))
        all_errors.extend(errors)
        validated += 1
        if verbose and not errors:
            print(f"    OK: {yaml_file.name} ({entity_type})")

    # Package manifests
    package_schema = load_schema(schema_dir, "package")
    for inv_path in investigation_paths:
        manifest_path = find_manifest(inv_path)
        if manifest_path is None:
            continue
        data, error = load_yaml(manifest_path)
        if error:
            all_errors.append(_err("YAML_PARSE_ERROR", manifest_path, error))
            continue
        if data is None or package_schema is None:
            continue
        errors = validate_data(data, package_schema, registry, str(manifest_path))
        all_errors.extend(errors)
        validated += 1
        if verbose and not errors:
            print(f"    OK: {manifest_path} (package manifest)")

    if validated == 0 and not all_errors:
        all_errors.append(_err("SCHEMA_VACUOUS_RUN", "<repo>", "No files were validated — vacuous run"))

    return len(all_errors) == 0, all_errors


if __name__ == "__main__":
    import sys
    repo_root = Path(__file__).parent.parent
    inv_paths = [
        p for p in (repo_root / "investigations").iterdir()
        if p.is_dir() and not p.name.startswith("_")
    ]
    passed, errors = run_schema_validation(inv_paths, repo_root / "schema", verbose=True)
    for e in errors:
        print(f"ERROR: {e}")
    sys.exit(0 if passed else 1)
