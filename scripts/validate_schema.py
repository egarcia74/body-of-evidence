#!/usr/bin/env python3
"""
Body of Evidence — Schema Validation

Validates all YAML entity files against their JSON Schema definitions.

Each YAML file must have a 'type' field that maps to a schema file:
    schema/<type>.schema.json
"""

import json
from pathlib import Path
from typing import List, Tuple

import yaml

# jsonschema is a required dependency
try:
    import jsonschema
    from jsonschema import validate, ValidationError, SchemaError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False


def load_schema(schema_dir: Path, entity_type: str) -> dict | None:
    """Load a JSON Schema for a given entity type."""
    schema_path = schema_dir / f"{entity_type}.schema.json"
    if not schema_path.exists():
        return None
    with open(schema_path) as f:
        return json.load(f)


def load_common_schema(schema_dir: Path) -> dict:
    """Load the common definitions schema."""
    common_path = schema_dir / "common.schema.json"
    if not common_path.exists():
        return {}
    with open(common_path) as f:
        return json.load(f)


def validate_yaml_file(yaml_path: Path, schema_dir: Path) -> list[str]:
    """
    Validate a single YAML file against its entity schema.
    Returns a list of error messages (empty if valid).
    """
    errors = []

    # Load YAML
    try:
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return [f"{yaml_path}: YAML parse error: {e}"]

    if not isinstance(data, dict):
        return [f"{yaml_path}: Expected a YAML mapping at the root level"]

    entity_type = data.get("type")
    if not entity_type:
        return [f"{yaml_path}: Missing required 'type' field"]

    if not JSONSCHEMA_AVAILABLE:
        return [f"jsonschema not installed — run: pip install -r scripts/requirements.txt"]

    # Load schema
    schema = load_schema(schema_dir, entity_type)
    if schema is None:
        return [f"{yaml_path}: No schema found for type '{entity_type}' (expected schema/{entity_type}.schema.json)"]

    # Validate
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        errors.append(f"{yaml_path}: {e.message} (path: {' > '.join(str(p) for p in e.path)})")
    except SchemaError as e:
        errors.append(f"Schema error in {entity_type}.schema.json: {e.message}")

    return errors


def find_yaml_files(investigation_paths: list[Path]) -> list[Path]:
    """Find all YAML entity files in the given investigation directories."""
    yaml_files = []
    for inv_path in investigation_paths:
        yaml_files.extend(inv_path.rglob("*.yaml"))
        yaml_files.extend(inv_path.rglob("*.yml"))
    return yaml_files


def run_schema_validation(
    investigation_paths: list[Path],
    schema_dir: Path,
    verbose: bool = False,
) -> Tuple[bool, List[str]]:
    """
    Run schema validation on all YAML files.

    Returns (passed: bool, errors: list[str])
    """
    yaml_files = find_yaml_files(investigation_paths)

    if not yaml_files:
        return True, []

    all_errors = []
    for yaml_file in sorted(yaml_files):
        errors = validate_yaml_file(yaml_file, schema_dir)
        all_errors.extend(errors)
        if verbose and not errors:
            print(f"    OK: {yaml_file.relative_to(yaml_file.parents[3])}")

    return len(all_errors) == 0, all_errors


if __name__ == "__main__":
    # Allow running standalone for quick checks
    import sys
    repo_root = Path(__file__).parent.parent
    schema_dir = repo_root / "schema"
    investigations_dir = repo_root / "investigations"

    inv_paths = [
        p for p in investigations_dir.iterdir()
        if p.is_dir() and not p.name.startswith("_")
    ]

    passed, errors = run_schema_validation(inv_paths, schema_dir, verbose=True)
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        sys.exit(1)
    else:
        print("All schema validation passed.")
        sys.exit(0)
