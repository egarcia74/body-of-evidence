"""
Body of Evidence — Validation Tests

These tests prove the validators do what they claim:
- The valid fixture package passes every check.
- Every invalid fixture package fails at least one check.
- Schema files are well-formed; examples validate against them.

Run with: pytest tests/
"""

import json
import shutil
import subprocess
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
    diagnostics passing silently. Fifth-pass review finding M-07b: even the
    exact (validator, code) SET is insufficient — a Python `set` collapses
    duplicate diagnostics (two dangling references in one file look the
    same as one) and discards which field/entry each occurrence is about.

    Each fixture therefore declares an exact, order-independent but
    duplicate-preserving MULTISET of (validator, code, path, location)
    tuples across ALL checks — a sorted list, compared for equality, not a
    set. `location` is the field or JSON pointer the diagnostic is about
    (see boe_files.Diagnostic); "" for diagnostics that aren't field-level."""

    def _relativize(self, raw_path: str) -> str:
        """Diagnostic.path is str(yaml_file), absolute or relative depending
        on how investigation_paths was built — normalise to repo-relative
        (lexically, WITHOUT following symlinks — resolving would turn a
        symlinked package root's own path into its target's path) so
        expected literals stay short and checkout-location independent.
        Sentinel paths like '<repo>' pass through unchanged."""
        p = Path(raw_path)
        if p.is_absolute():
            try:
                return str(p.relative_to(REPO_ROOT))
            except ValueError:
                return raw_path
        return raw_path

    def _all_diagnostics(self, pkg: Path) -> list[tuple[str, str, str, str]]:
        tuples = []
        for check in ALL_CHECKS:
            _, errors = check(
                investigation_paths=[pkg], schema_dir=SCHEMA_DIR, verbose=False
            )
            tuples.extend((e.validator, e.code, self._relativize(e.path), e.location) for e in errors)
        return sorted(tuples)

    @pytest.mark.parametrize(
        "pkg_name,expected",
        [
            ("duplicate-version-id", [
                ("ids", "VERSION_ID_DUPLICATE", "fixtures/invalid/duplicate-version-id/claim-b.yaml", ""),
            ]),
            ("broken-reference", [
                ("references", "REF_NOT_FOUND", "fixtures/invalid/broken-reference/link-dangling.yaml", "claim_id"),
                ("references", "REF_NOT_FOUND", "fixtures/invalid/broken-reference/link-dangling.yaml", "evidence_id"),
            ]),
            ("orphan-evidence", [
                ("orphans", "ORPHAN_EVIDENCE", "fixtures/invalid/orphan-evidence/evidence-orphan.yaml", ""),
            ]),
            ("missing-provenance", [
                ("provenance", "PROVENANCE_MISSING", "fixtures/invalid/missing-provenance/source-no-provenance.yaml", ""),
                ("schema", "SCHEMA_VALIDATION_ERROR", "fixtures/invalid/missing-provenance/source-no-provenance.yaml", "(root)"),
            ]),
            ("bad-id-format", [
                ("ids", "ID_BAD_FORMAT", "fixtures/invalid/bad-id-format/claim-bad-id.yaml", ""),
                ("schema", "SCHEMA_VALIDATION_ERROR", "fixtures/invalid/bad-id-format/claim-bad-id.yaml", "id"),
            ]),
            ("missing-manifest", [
                ("references", "MANIFEST_MISSING", "fixtures/invalid/missing-manifest", ""),
            ]),
            ("revision-unrelated-endpoints", [
                ("references", "REVISION_ENTITY_MISMATCH",
                 "fixtures/invalid/revision-unrelated-endpoints/revision-broken.yaml", "old_version_id"),
            ]),
            ("manifest-no-investigation", [
                ("references", "MANIFEST_NO_INVESTIGATION", "fixtures/invalid/manifest-no-investigation/package.yaml", ""),
            ]),
            ("manifest-symlink-escape", [
                # Root cause is the symlink; MANIFEST_NO_INVESTIGATION is a
                # derived/cascading diagnostic — the manifest's only
                # Investigation entry is the rejected symlinked path, so the
                # manifest also has no accepted Investigation. Declared
                # explicitly, not hidden (this is the exact case the
                # fourth-pass review flagged as silently tolerated).
                ("references", "MANIFEST_NO_INVESTIGATION", "fixtures/invalid/manifest-symlink-escape/package.yaml", ""),
                ("references", "MANIFEST_PATH_SYMLINK", "fixtures/invalid/manifest-symlink-escape/package.yaml", "escape.yaml"),
            ]),
            ("investigation-root-symlink", [
                # A tracked symlink AT the package-directory level (not an
                # entity path inside one) — fifth-pass review H-15. Every
                # validator refuses to descend into it (boe_files skips a
                # symlinked root entirely); references reports the precise
                # root cause, schema reports the resulting empty run.
                ("references", "INVESTIGATION_ROOT_SYMLINK", "fixtures/invalid/investigation-root-symlink", ""),
                ("schema", "SCHEMA_VACUOUS_RUN", "<repo>", ""),
            ]),
        ],
    )
    def test_invalid_fixture_rejected(self, pkg_name, expected):
        pkg = FIXTURES / "invalid" / pkg_name
        assert pkg.exists(), f"Missing invalid fixture: {pkg_name}"
        actual = self._all_diagnostics(pkg)
        assert actual == sorted(expected), (
            f"invalid/{pkg_name}: expected exactly {sorted(expected)}, "
            f"got {actual}"
        )


class TestCrossPackageReferences:
    """H-02b (fourth-pass) + H-02c (fifth-pass): package ownership must be
    enforced for Revision endpoints AND for every ordinary cross-entity
    reference. fixtures/cross_package/{pkg-a,pkg-b} share a stable claim id
    across two independent packages on purpose: package A's revision claims
    a transition from a version that actually lives in package B (H-02b),
    and package A's claim-cross-ref.yaml has an investigation_id pointing
    directly at package B's Investigation (H-02c — an ordinary reference,
    not a Revision at all). This can only be exercised by validating both
    packages TOGETHER (one list of investigation_paths), which the
    single-package fixtures/invalid/* self-test loop cannot do — hence
    dedicated tests rather than more self-test fixtures."""

    def test_revision_cannot_claim_version_from_another_package(self):
        pkg_a = FIXTURES / "cross_package" / "pkg-a"
        pkg_b = FIXTURES / "cross_package" / "pkg-b"
        assert pkg_a.exists() and pkg_b.exists(), "Missing cross_package fixtures"

        passed, errors = run_reference_validation(
            investigation_paths=[pkg_a, pkg_b], schema_dir=SCHEMA_DIR, verbose=False
        )
        assert not passed, "Cross-package reference was not rejected"
        codes = {(e.validator, e.code) for e in errors}
        assert ("references", "REVISION_ENDPOINT_WRONG_PACKAGE") in codes, (
            f"Expected REVISION_ENDPOINT_WRONG_PACKAGE, got: {codes}"
        )

    def test_ordinary_reference_cannot_cross_package_boundary(self):
        """H-02c: package scoping must apply to EVERY reference type, not
        only Revision endpoints — this probes an ordinary Claim ->
        Investigation reference."""
        pkg_a = FIXTURES / "cross_package" / "pkg-a"
        pkg_b = FIXTURES / "cross_package" / "pkg-b"

        passed, errors = run_reference_validation(
            investigation_paths=[pkg_a, pkg_b], schema_dir=SCHEMA_DIR, verbose=False
        )
        assert not passed
        matches = [
            e for e in errors
            if e.validator == "references" and e.code == "REF_WRONG_PACKAGE"
            and e.path.endswith("claim-cross-ref.yaml") and e.location == "investigation_id"
        ]
        assert matches, (
            f"Expected a REF_WRONG_PACKAGE diagnostic for claim-cross-ref.yaml's "
            f"investigation_id, got: {[(e.validator, e.code, e.path, e.location) for e in errors]}"
        )

    def test_each_package_is_independently_well_formed(self):
        """The cross-package defect, not incidental fixture breakage, must
        be what fails — each package alone should pass every other check."""
        for pkg_name in ("pkg-a", "pkg-b"):
            pkg = FIXTURES / "cross_package" / pkg_name
            for check in (run_schema_validation, run_id_validation, run_orphan_validation, run_provenance_validation):
                passed, errors = check(investigation_paths=[pkg], schema_dir=SCHEMA_DIR, verbose=False)
                assert passed, f"{pkg_name} unexpectedly failed {check.__name__}: {[str(e) for e in errors]}"


class TestSymlinkedPackageRoot:
    """H-15 (fifth-pass review): an investigation ROOT that is itself a
    symlink must be rejected before any file discovery — `p.is_dir()` in
    package discovery is true for a symlink to a directory, so discovery
    alone cannot filter it out. Covered as a self-test fixture too
    (fixtures/invalid/investigation-root-symlink), but the underlying
    boe_files helpers are worth testing directly since every validator
    depends on them."""

    def test_find_entity_files_skips_symlinked_root(self):
        import boe_files
        real_pkg = FIXTURES / "valid" / "harbour-tender-inquiry"
        symlinked_pkg = FIXTURES / "invalid" / "investigation-root-symlink"
        assert symlinked_pkg.is_symlink(), "Fixture must be a tracked symlink"
        assert symlinked_pkg.resolve() == real_pkg.resolve(), (
            "Fixture must point at a real, otherwise-valid package — "
            "proving rejection is about the symlink, not broken content"
        )
        files_via_symlink = boe_files.find_entity_files([symlinked_pkg])
        assert files_via_symlink == [], (
            "find_entity_files must not traverse a symlinked package root "
            f"at all, got: {files_via_symlink}"
        )

    def test_find_manifest_refuses_symlinked_root(self):
        import boe_files
        symlinked_pkg = FIXTURES / "invalid" / "investigation-root-symlink"
        assert boe_files.find_manifest(symlinked_pkg) is None


class TestCliMultiPackageDiscovery:
    """M-15 (fifth-pass review): the cross-package tests above call
    run_reference_validation directly with a hand-built investigation_paths
    list. They never exercise validate.py's actual CLI discovery route
    (argv parsing, then `investigations_dir.iterdir()`), which is a
    materially different code path and the one real users and CI actually
    run. `--root` (added in response to this finding) lets that exact route
    be exercised against a throwaway directory instead of mutating the
    repository's real investigations/."""

    VALIDATE_PY = REPO_ROOT / "scripts" / "validate.py"

    def _run_cli(self, root: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(self.VALIDATE_PY), "--root", str(root), "--verbose"],
            capture_output=True, text=True,
        )

    def test_cli_accepts_valid_sibling_package(self, tmp_path):
        shutil.copytree(FIXTURES / "valid" / "harbour-tender-inquiry", tmp_path / "harbour-tender-inquiry")
        result = self._run_cli(tmp_path)
        assert result.returncode == 0, (
            f"CLI rejected a known-valid package under --root:\n{result.stdout}\n{result.stderr}"
        )

    def test_cli_rejects_cross_package_reference_via_real_discovery(self, tmp_path):
        """The same defect fixtures/cross_package/{pkg-a,pkg-b} prove via
        direct function calls, but discovered the way validate.py actually
        discovers packages in production: multiple sibling directories
        under one root, found by iterdir(), not a hand-assembled list."""
        shutil.copytree(FIXTURES / "cross_package" / "pkg-a", tmp_path / "pkg-a")
        shutil.copytree(FIXTURES / "cross_package" / "pkg-b", tmp_path / "pkg-b")
        result = self._run_cli(tmp_path)
        assert result.returncode != 0, (
            f"CLI accepted a cross-package reference under --root:\n{result.stdout}"
        )
        assert "belongs to package" in result.stdout, (
            f"Expected a package-ownership diagnostic in CLI output, got:\n{result.stdout}"
        )

    def test_cli_rejects_symlinked_sibling_package(self, tmp_path):
        """Same H-15 defect, via real discovery: a symlinked directory
        satisfies iterdir()'s is_dir() filter just like a real one."""
        real_target = tmp_path / "_outside"
        shutil.copytree(FIXTURES / "valid" / "harbour-tender-inquiry", real_target)
        (tmp_path / "alias").symlink_to(real_target, target_is_directory=True)
        result = self._run_cli(tmp_path)
        assert result.returncode != 0, (
            f"CLI accepted a symlinked package root under --root:\n{result.stdout}"
        )
        assert "symlink" in result.stdout.lower(), (
            f"Expected a symlink diagnostic in CLI output, got:\n{result.stdout}"
        )
