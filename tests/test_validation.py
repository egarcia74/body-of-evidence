"""
Body of Evidence — Validation Tests

These tests prove the validators do what they claim:
- The valid fixture package passes every check.
- Every invalid fixture package fails at least one check.
- Schema files are well-formed; examples validate against them.

Run with: pytest tests/
"""

import json
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from validate_schema import run_schema_validation
from validate_ids import run_id_validation, validate_id_format, validate_ulid
from validate_references import run_reference_validation
from validate_orphans import run_orphan_validation
from validate_provenance import run_provenance_validation

SCHEMA_DIR = REPO_ROOT / "schema"
FIXTURES = REPO_ROOT / "fixtures"

ALL_CHECKS = [
    run_schema_validation,
    run_id_validation,
    run_reference_validation,
    run_orphan_validation,
    run_provenance_validation,
]

EXPECTED_SCHEMAS = [
    "common.schema.json",
    "investigation.schema.json",
    "claim.schema.json",
    "claim_evidence_link.schema.json",
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
    "package.schema.json",
]


class TestSchemaFiles:
    def test_schema_files_exist(self):
        for schema_name in EXPECTED_SCHEMAS:
            assert (SCHEMA_DIR / schema_name).exists(), f"Missing schema: {schema_name}"

    def test_schema_files_are_valid_json(self):
        for schema_file in SCHEMA_DIR.glob("*.json"):
            with open(schema_file) as f:
                json.load(f)

    def test_examples_parse_and_have_required_identity_fields(self):
        examples_dir = REPO_ROOT / "examples"
        checked = 0
        for yaml_file in examples_dir.glob("*.yaml"):
            with open(yaml_file) as f:
                data = yaml.safe_load(f)
            assert isinstance(data, dict), f"{yaml_file}: expected a mapping"
            if yaml_file.name == "package.yaml":
                assert "manifest_version" in data, f"{yaml_file}: missing manifest_version"
            else:
                assert "id" in data, f"{yaml_file}: missing 'id'"
                assert "type" in data, f"{yaml_file}: missing 'type'"
                assert "version_id" in data, f"{yaml_file}: missing 'version_id'"
            checked += 1
        assert checked >= 14, f"Expected at least 14 example files, found {checked}"

    def test_examples_validate_against_schemas(self):
        """Every example must validate against its declared schema."""
        passed, errors = run_schema_validation(
            [REPO_ROOT / "examples"], SCHEMA_DIR, verbose=False
        )
        assert passed, "Examples failed schema validation:\n" + "\n".join(str(e) for e in errors)


class TestUlidValidation:
    def test_valid_ids(self):
        for id_str in [
            "boe:claim:01HV8QKJZ9XTMK3P2R7N5W6D4F",
            "boe:claim_evidence_link:01JF0000000000000000000005",
            "boe:investigation:01HV8QKJZ9XTMK3P2R7N5W6D4E",
        ]:
            is_valid, error = validate_id_format(id_str)
            assert is_valid, f"'{id_str}' should be valid: {error}"

    def test_invalid_ids(self):
        for id_str in [
            "claim:01HV8QKJZ9XTMK3P2R7N5W6D4F",       # missing boe:
            "boe:01HV8QKJZ9XTMK3P2R7N5W6D4F",          # missing type
            "boe:claim:not-a-ulid",                     # not a ULID
            "boe:claim:",                               # empty
            "BOE:CLAIM:01HV8QKJZ9XTMK3P2R7N5W6D4F",   # wrong case
            "boe:claim:01HVILLEGALULIDOOOOOOOO4F",     # I/L/O/U chars
            "boe:claim:81HV8QKJZ9XTMK3P2R7N5W6D4F",   # first char > 7
        ]:
            is_valid, _ = validate_id_format(id_str)
            assert not is_valid, f"'{id_str}' should be invalid"

    def test_ulid_charset(self):
        ok, _ = validate_ulid("01HV8QKJZ9XTMK3P2R7N5W6D4F")
        assert ok
        bad, _ = validate_ulid("01HV8QKJZ9XTMK3P2R7N5W6DIL")  # I and L invalid
        assert not bad


class TestValidFixture:
    """The valid fixture package must pass every check — this is what makes
    the validation suite non-vacuous."""

    @pytest.fixture
    def valid_packages(self):
        pkgs = sorted(p for p in (FIXTURES / "valid").iterdir() if p.is_dir())
        assert pkgs, "fixtures/valid must contain at least one package"
        return pkgs

    @pytest.mark.parametrize("check", ALL_CHECKS, ids=lambda c: c.__name__)
    def test_valid_fixture_passes(self, valid_packages, check):
        passed, errors = check(
            investigation_paths=valid_packages,
            schema_dir=SCHEMA_DIR,
            verbose=False,
        )
        assert passed, f"{check.__name__} failed on valid fixture:\n" + "\n".join(str(e) for e in errors)


class TestVersioningModel:
    """D-009: repeated stable ids across version files are VALID (that is the
    versioning model working); the valid fixture contains a superseded claim
    version sharing its id with the current version to prove it."""

    def test_valid_fixture_contains_multiple_versions_of_one_entity(self):
        pkg = FIXTURES / "valid" / "harbour-tender-inquiry"
        ids = []
        for f in pkg.rglob("*.yaml"):
            if f.name == "package.yaml":
                continue
            with open(f) as fh:
                data = yaml.safe_load(fh)
            if isinstance(data, dict) and "id" in data:
                ids.append(data["id"])
        duplicated = {i for i in ids if ids.count(i) > 1}
        assert duplicated, (
            "The valid fixture must contain at least one entity with multiple "
            "version files — otherwise the D-009 workflow is never proven to validate"
        )

    def test_repeated_stable_id_with_distinct_versions_passes(self):
        pkg = FIXTURES / "valid" / "harbour-tender-inquiry"
        passed, errors = run_id_validation(
            investigation_paths=[pkg], schema_dir=SCHEMA_DIR, verbose=False
        )
        assert passed, (
            "Repeated stable id with distinct version_ids must validate:\n"
            + "\n".join(str(e) for e in errors)
        )


class TestInvalidFixtures:
    """Every invalid fixture must be rejected by the intended check WITH the
    intended error. Fourth-pass review finding M-07/M-10: asserting only a
    substring of one error tolerates extra, unrelated, or cascading
    diagnostics passing silently (the tracked manifest-symlink-escape
    fixture emits two diagnostics; the old substring assertion never
    noticed). Diagnostics are now structured (boe_files.Diagnostic) and each
    fixture declares its EXACT (validator, code) set across ALL checks —
    equality, not membership."""

    def _all_diagnostics(self, pkg: Path) -> set[tuple[str, str]]:
        codes = set()
        for check in ALL_CHECKS:
            _, errors = check(
                investigation_paths=[pkg], schema_dir=SCHEMA_DIR, verbose=False
            )
            codes.update((e.validator, e.code) for e in errors)
        return codes

    @pytest.mark.parametrize(
        "pkg_name,expected_codes",
        [
            ("duplicate-version-id", {("ids", "VERSION_ID_DUPLICATE")}),
            ("broken-reference", {("references", "REF_NOT_FOUND")}),
            ("orphan-evidence", {("orphans", "ORPHAN_EVIDENCE")}),
            ("missing-provenance", {
                ("schema", "SCHEMA_VALIDATION_ERROR"),
                ("provenance", "PROVENANCE_MISSING"),
            }),
            ("bad-id-format", {
                ("schema", "SCHEMA_VALIDATION_ERROR"),
                ("ids", "ID_BAD_FORMAT"),
            }),
            ("missing-manifest", {("references", "MANIFEST_MISSING")}),
            ("revision-unrelated-endpoints", {("references", "REVISION_ENTITY_MISMATCH")}),
            ("manifest-no-investigation", {("references", "MANIFEST_NO_INVESTIGATION")}),
            ("manifest-symlink-escape", {
                ("references", "MANIFEST_PATH_SYMLINK"),
                # Root cause is the symlink; this is a derived/cascading
                # diagnostic — the manifest's only Investigation entry is
                # the rejected symlinked path, so the manifest also has no
                # accepted Investigation. Declared explicitly, not hidden.
                ("references", "MANIFEST_NO_INVESTIGATION"),
            }),
        ],
    )
    def test_invalid_fixture_rejected(self, pkg_name, expected_codes):
        pkg = FIXTURES / "invalid" / pkg_name
        assert pkg.exists(), f"Missing invalid fixture: {pkg_name}"
        actual_codes = self._all_diagnostics(pkg)
        assert actual_codes == expected_codes, (
            f"invalid/{pkg_name}: expected exactly {expected_codes}, "
            f"got {actual_codes}"
        )


class TestCrossPackageRevision:
    """H-02b (fourth-pass review): a Revision must only connect versions
    owned by its OWN package. fixtures/cross_package/{pkg-a,pkg-b} share a
    stable claim id across two independent packages on purpose — package
    A's revision claims a transition from a version that actually lives in
    package B. This can only be exercised by validating both packages
    TOGETHER (one list of investigation_paths), which the single-package
    fixtures/invalid/* self-test loop cannot do — hence a dedicated test
    rather than another self-test fixture."""

    def test_revision_cannot_claim_version_from_another_package(self):
        pkg_a = FIXTURES / "cross_package" / "pkg-a"
        pkg_b = FIXTURES / "cross_package" / "pkg-b"
        assert pkg_a.exists() and pkg_b.exists(), "Missing cross_package fixtures"

        passed, errors = run_reference_validation(
            investigation_paths=[pkg_a, pkg_b], schema_dir=SCHEMA_DIR, verbose=False
        )
        assert not passed, "Cross-package revision endpoint was not rejected"
        codes = {(e.validator, e.code) for e in errors}
        assert ("references", "REVISION_ENDPOINT_WRONG_PACKAGE") in codes, (
            f"Expected REVISION_ENDPOINT_WRONG_PACKAGE, got: {codes}"
        )

    def test_each_package_is_independently_well_formed(self):
        """The cross-package defect, not incidental fixture breakage, must
        be what fails — each package alone should pass every other check."""
        for pkg_name in ("pkg-a", "pkg-b"):
            pkg = FIXTURES / "cross_package" / pkg_name
            for check in (run_schema_validation, run_id_validation, run_orphan_validation, run_provenance_validation):
                passed, errors = check(investigation_paths=[pkg], schema_dir=SCHEMA_DIR, verbose=False)
                assert passed, f"{pkg_name} unexpectedly failed {check.__name__}: {[str(e) for e in errors]}"
