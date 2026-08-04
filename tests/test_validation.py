"""
Body of Evidence — Validation Test Stubs

These tests verify that the validation scripts themselves work correctly.
They will be expanded when real investigation data is available.

Run with: pytest tests/
"""

import sys
from pathlib import Path

import pytest

# Add scripts/ to the path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))


class TestSchemaValidation:
    """Test schema validation script."""

    def test_schema_files_exist(self):
        """All expected schema files must be present."""
        schema_dir = REPO_ROOT / "schema"
        expected_schemas = [
            "common.schema.json",
            "investigation.schema.json",
            "claim.schema.json",
            "evidence.schema.json",
            "source.schema.json",
            "person.schema.json",
            "organisation.schema.json",
            "event.schema.json",
            "timeline.schema.json",
            "assessment.schema.json",
            "relationship.schema.json",
            "revision.schema.json",
            "review.schema.json",
            "finding.schema.json",
        ]
        for schema_name in expected_schemas:
            assert (schema_dir / schema_name).exists(), (
                f"Missing schema: {schema_name}"
            )

    def test_schema_files_are_valid_json(self):
        """All schema files must be valid JSON."""
        import json
        schema_dir = REPO_ROOT / "schema"
        for schema_file in schema_dir.glob("*.json"):
            with open(schema_file) as f:
                try:
                    json.load(f)
                except json.JSONDecodeError as e:
                    pytest.fail(f"Invalid JSON in {schema_file}: {e}")

    def test_examples_are_valid_yaml(self):
        """All example YAML files must parse without error."""
        import yaml
        examples_dir = REPO_ROOT / "examples"
        for yaml_file in examples_dir.glob("*.yaml"):
            with open(yaml_file) as f:
                try:
                    data = yaml.safe_load(f)
                    assert isinstance(data, dict), f"{yaml_file}: Expected a dict at root"
                except yaml.YAMLError as e:
                    pytest.fail(f"Invalid YAML in {yaml_file}: {e}")


class TestIdValidation:
    """Test ID format validation."""

    def test_valid_id_format(self):
        """Valid IDs should pass format check."""
        from validate_ids import validate_id_format
        valid_ids = [
            "boe:claim:01HV8QKJZ9XTMK3P2R7N5W6D4F",
            "boe:investigation:01HV8QKJZ9XTMK3P2R7N5W6D4E",
            "boe:source:01HV8QKJZ9XTMK3P2R7N5W6D4G",
        ]
        for id_str in valid_ids:
            is_valid, error = validate_id_format(id_str)
            assert is_valid, f"Expected valid ID '{id_str}' to pass: {error}"

    def test_invalid_id_formats(self):
        """Invalid IDs should fail format check."""
        from validate_ids import validate_id_format
        invalid_ids = [
            "claim:01HV8QKJZ9XTMK3P2R7N5W6D4F",    # Missing boe: prefix
            "boe:01HV8QKJZ9XTMK3P2R7N5W6D4F",       # Missing type
            "boe:claim:not-a-ulid",                   # Invalid ULID
            "boe:claim:",                              # Empty ULID
            "BOE:CLAIM:01HV8QKJZ9XTMK3P2R7N5W6D4F", # Wrong case
        ]
        for id_str in invalid_ids:
            is_valid, error = validate_id_format(id_str)
            assert not is_valid, f"Expected invalid ID '{id_str}' to fail"


class TestExampleEntityStructure:
    """Test that example YAML files have required fields."""

    def test_all_examples_have_id_and_type(self):
        """Every example must have both 'id' and 'type' fields."""
        import yaml
        examples_dir = REPO_ROOT / "examples"
        for yaml_file in examples_dir.glob("*.yaml"):
            with open(yaml_file) as f:
                data = yaml.safe_load(f)
            assert "id" in data, f"{yaml_file}: Missing 'id' field"
            assert "type" in data, f"{yaml_file}: Missing 'type' field"
