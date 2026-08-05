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
                # Three diagnostics, all root-cause-adjacent to the same
                # tracked symlink, all declared explicitly rather than
                # picking one and hiding the rest:
                # - MANIFEST_PATH_SYMLINK: the manifest-listed path check
                #   (fourth-pass M-11) catches it as a LISTED entry.
                # - PACKAGE_SYMLINK: sixth-pass H-19's unconditional
                #   discovery-level check ALSO independently catches it —
                #   this is deliberately redundant with the check above;
                #   H-19 exists specifically because a symlinked file might
                #   NOT be manifest-listed (see investigation-root-symlink
                #   for the package-root case, and the H-19 fixtures below
                #   for the unmanifested case).
                # - MANIFEST_NO_INVESTIGATION: derived/cascading — the
                #   manifest's only Investigation entry is the rejected
                #   symlinked path, so the manifest also has no accepted
                #   Investigation (the case the fourth-pass review flagged
                #   as silently tolerated by the old substring-only test).
                ("references", "PACKAGE_SYMLINK", "fixtures/invalid/manifest-symlink-escape/escape.yaml", ""),
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
            ("unmanifested-symlink", [
                # sixth-pass review H-19: a symlinked entity file that is
                # NOT listed in package.yaml at all (unlike
                # manifest-symlink-escape's escape.yaml, which IS listed).
                # The manifest-path containment check can't see this by
                # construction — it only inspects listed paths — which is
                # exactly why H-19 required an unconditional discovery-level
                # check independent of the manifest.
                ("references", "PACKAGE_SYMLINK",
                 "fixtures/invalid/unmanifested-symlink/claim-unlisted-symlink.yaml", ""),
            ]),
            ("broken-unmanifested-symlink", [
                # Same as above, but the symlink target doesn't exist. Must
                # produce this diagnostic, not an uncaught FileNotFoundError
                # crashing the whole run (sixth-pass review H-19).
                ("references", "PACKAGE_SYMLINK",
                 "fixtures/invalid/broken-unmanifested-symlink/claim-broken-symlink.yaml", ""),
            ]),
            ("symlinked-subdirectory", [
                # seventh-pass review M-20: the sixth-pass symlink scan only
                # looked at *.yaml/*.yml files, so a symlinked SUBDIRECTORY
                # (aliased-claims -> .../harbour-tender-inquiry/claims) was
                # invisible to it — rglob doesn't currently follow a
                # symlinked directory in this pathlib version, so nothing
                # inside it is actually read, but the symlink itself went
                # completely undetected. find_all_symlinks walks with
                # os.walk(followlinks=False), which lists but never
                # descends into it, so the symlink is now reported without
                # ever reading through it.
                ("references", "PACKAGE_SYMLINK",
                 "fixtures/invalid/symlinked-subdirectory/aliased-claims", ""),
            ]),
            ("reference-not-current", [
                # H-20 (seventh-pass review): claim-uncurrent.yaml exists as
                # a file and is schema/id valid, but package.yaml does NOT
                # list it — link.yaml's claim_id reference must be rejected
                # because "a file with this id exists in the package" is
                # not the same guarantee as "the release's manifest
                # contains this id as its current version."
                ("references", "REF_NOT_CURRENT",
                 "fixtures/invalid/reference-not-current/link.yaml", "claim_id"),
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

    def test_locally_resolvable_reference_is_not_a_false_positive(self):
        """H-17 (sixth-pass review): claim-cross-ref shares its stable id
        (...802) with package B's claim-old.yaml. Before H-17, a lossy
        last-writer-wins id_index made revision-cross-package.yaml's
        entity_id resolve to WHICHEVER package was indexed last — even
        though a locally valid match exists in pkg-a itself — producing a
        spurious REF_WRONG_PACKAGE for a reference that is, in fact,
        resolvable within its own package. Only the genuinely cross-package
        references (asserted in the two tests above) should be flagged."""
        pkg_a = FIXTURES / "cross_package" / "pkg-a"
        pkg_b = FIXTURES / "cross_package" / "pkg-b"

        for order in ([pkg_a, pkg_b], [pkg_b, pkg_a]):
            _, errors = run_reference_validation(
                investigation_paths=order, schema_dir=SCHEMA_DIR, verbose=False
            )
            false_positives = [
                e for e in errors
                if e.path.endswith("revision-cross-package.yaml") and e.location == "entity_id"
            ]
            assert not false_positives, (
                f"revision-cross-package.yaml's entity_id is locally resolvable "
                f"within pkg-a and must not be flagged, got: "
                f"{[(e.code, e.location) for e in false_positives]} (order={[p.name for p in order]})"
            )


def _is_boe_id_pattern(node: dict) -> bool:
    """True if a JSON Schema node constrains a string to the
    boe:<type>:<ulid> ID pattern, directly (an inline `pattern`) or via a
    $ref to a common definition following that same naming convention
    (e.g. investigationReference)."""
    if node.get("pattern", "").startswith("^boe:"):
        return True
    return node.get("$ref", "").endswith("Reference")


def _reference_shaped_field_paths(schema: dict, prefix: str = "") -> set[str]:
    """
    Recursively find every property path in a schema whose value is
    constrained to the boe: ID pattern — i.e. every field that IS a
    reference, regardless of whether any validator currently checks it.
    `id` and `version_id` are excluded: they are an entity's OWN identity,
    not an outbound reference to something else. Array-of-object
    properties are traversed with a '[]' path segment, matching the
    convention validate_references.NESTED_REFERENCE_FIELDS uses.

    This is the schema-completeness half of sixth-pass review H-18: the
    reviewer found five reference fields that existed in schemas but had
    no corresponding check at all. A registry entry can be wrong, but it
    can't silently not exist — this scanner finds the field independent of
    whatever validate_references.py currently claims to cover, so the
    completeness test below can compare the two and fail loudly on drift.
    """
    found = set()
    for name, node in (schema.get("properties") or {}).items():
        if name in ("id", "version_id"):
            continue
        path = f"{prefix}{name}"
        if node.get("type") == "array":
            items = node.get("items") or {}
            if items.get("type") == "object":
                found |= _reference_shaped_field_paths(items, f"{path}[].")
                continue
            if _is_boe_id_pattern(items):
                found.add(path)
            continue
        if _is_boe_id_pattern(node):
            found.add(path)
    return found


class TestReferenceRegistryCompleteness:
    """H-18 (sixth-pass review): the reviewer found five schema-declared
    reference fields (event/person/organisation/relationship's
    investigation_ids, review.specific_concerns[].referenced_entity_id)
    that validate_references_in_file's old hand-maintained if/elif chain
    never checked at all — dangling, wrong-type, or cross-package values in
    those fields produced zero diagnostics. The fix replaced the chain with
    a declarative registry (REFERENCE_FIELDS + NESTED_REFERENCE_FIELDS);
    THIS test is what stops that regressing — it scans every schema for
    reference-shaped fields independent of the registry and asserts the two
    agree, so a future schema change that adds a reference field without a
    matching registry entry fails a test instead of silently validating
    nothing."""

    def test_every_schema_reference_field_is_registered(self):
        import validate_references as vr

        registered: dict[str, set[str]] = {}
        for entity_type, fields in vr.REFERENCE_FIELDS.items():
            registered[entity_type] = {field for field, _, _ in fields}
        for entity_type, paths in vr.nested_field_schema_paths().items():
            registered.setdefault(entity_type, set()).update(paths)

        missing = {}
        for schema_file in sorted(SCHEMA_DIR.glob("*.schema.json")):
            entity_type = schema_file.stem.replace(".schema", "")
            if entity_type in ("common", "package"):
                continue  # not entity types; package.yaml has its own checks
            with open(schema_file) as f:
                schema = json.load(f)
            found = _reference_shaped_field_paths(schema)
            gap = found - registered.get(entity_type, set())
            if gap:
                missing[entity_type] = gap

        assert not missing, (
            f"Schema-declared reference fields with no validate_references.py "
            f"registry entry (dangling/wrong-type/cross-package values in "
            f"these fields currently validate as if nothing were wrong): "
            f"{missing}"
        )

    def test_registry_has_no_stale_entries(self):
        """The inverse check: a registry entry for a field the schema no
        longer declares is dead code, not a safety issue, but it's worth
        catching too — it means the registry and the schema have drifted."""
        import validate_references as vr

        for schema_file in sorted(SCHEMA_DIR.glob("*.schema.json")):
            entity_type = schema_file.stem.replace(".schema", "")
            if entity_type in ("common", "package"):
                continue
            with open(schema_file) as f:
                schema = json.load(f)
            found = _reference_shaped_field_paths(schema)
            registered = {field for field, _, _ in vr.REFERENCE_FIELDS.get(entity_type, [])}
            registered |= vr.nested_field_schema_paths().get(entity_type, set())
            stale = registered - found
            assert not stale, f"{entity_type}: registry entries with no matching schema field: {stale}"

    def test_every_registered_field_actually_validates_when_dangling(self):
        """M-19 (seventh-pass review): NESTED_REFERENCE_FIELDS previously
        existed only to satisfy the completeness tests above — nothing at
        RUNTIME actually consumed it, since review.specific_concerns was a
        hardcoded loop with no connection to the registry. A future nested
        field could be added to both a schema and the registry, make the
        completeness test pass, and still never be checked — completeness
        (the field is LISTED) is not the same guarantee as correctness
        (the field is CHECKED). This constructs a synthetic dangling
        reference for every REFERENCE_FIELDS and NESTED_REFERENCE_FIELDS
        entry and asserts each one actually produces REF_NOT_FOUND."""
        import validate_references as vr

        FAKE_ID = "boe:nonexistent:01JF0000000000000000000000"

        for entity_type, fields in vr.REFERENCE_FIELDS.items():
            for field, is_list, _want_type in fields:
                data = {"type": entity_type, field: [FAKE_ID] if is_list else FAKE_ID}
                errors = vr.validate_references_in_file(
                    Path(f"synthetic-{entity_type}.yaml"), data, id_index={}, entity_package=None
                )
                codes = [(e.code, e.location) for e in errors]
                expected_location = f"{field}[0]" if is_list else field
                assert ("REF_NOT_FOUND", expected_location) in codes, (
                    f"{entity_type}.{field}: registered but a dangling value "
                    f"produced no REF_NOT_FOUND (got {codes}) — this registry "
                    f"entry is not actually executed"
                )

        for entity_type, nested_fields in vr.NESTED_REFERENCE_FIELDS.items():
            for array_field, item_field, _want_type in nested_fields:
                data = {"type": entity_type, array_field: [{item_field: FAKE_ID}]}
                errors = vr.validate_references_in_file(
                    Path(f"synthetic-{entity_type}.yaml"), data, id_index={}, entity_package=None
                )
                codes = [(e.code, e.location) for e in errors]
                expected_location = f"{array_field}[0].{item_field}"
                assert ("REF_NOT_FOUND", expected_location) in codes, (
                    f"{entity_type}.{array_field}[].{item_field}: registered but "
                    f"a dangling value produced no REF_NOT_FOUND (got {codes}) — "
                    f"this nested registry entry is not actually executed"
                )


class TestManifestCurrencyRequired:
    """H-20 (seventh-pass review): a reference resolving to SOME file with
    the right stable id in the right package is not enough — it must be
    that package's manifest's CURRENT version of that id. Covered as a
    self-test fixture too (fixtures/invalid/reference-not-current), but
    the valid fixture's positive case (a reference to something that IS
    current must still pass) is worth asserting directly since it's the
    same code path that could over-reject."""

    def test_valid_fixture_references_remain_accepted(self):
        """Regression guard: the valid fixture's links/assessments/revision
        reference the CURRENT claim version — H-20 must not turn every
        ordinary, correct reference into a false REF_NOT_CURRENT."""
        pkg = FIXTURES / "valid" / "harbour-tender-inquiry"
        passed, errors = run_reference_validation(
            investigation_paths=[pkg], schema_dir=SCHEMA_DIR, verbose=False
        )
        not_current = [e for e in errors if e.code == "REF_NOT_CURRENT"]
        assert not not_current, f"Valid fixture's current references were rejected: {not_current}"
        assert passed, f"Valid fixture unexpectedly failed references: {[str(e) for e in errors]}"


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


class TestUnmanifestedEntitySymlinks:
    """H-19 (sixth-pass review): unlike H-15's package-ROOT symlinks, these
    are individual entity files that are symlinks — and specifically ones
    NOT listed in package.yaml, so the manifest-path containment check
    (which only inspects listed paths) can't see them by construction.
    Historical/superseded version files are legitimately unmanifested by
    design (D-009), which is exactly why this needed an unconditional
    discovery-level check rather than extending the manifest check."""

    def test_find_entity_files_skips_symlinked_file(self):
        import boe_files
        pkg = FIXTURES / "invalid" / "unmanifested-symlink"
        symlink = pkg / "claim-unlisted-symlink.yaml"
        assert symlink.is_symlink(), "Fixture must be a tracked symlink"
        files = boe_files.find_entity_files([pkg])
        assert symlink not in files, (
            f"find_entity_files must not read a symlinked entity file, got: {files}"
        )

    def test_find_all_symlinks_reports_it(self):
        import boe_files
        pkg = FIXTURES / "invalid" / "unmanifested-symlink"
        symlink = pkg / "claim-unlisted-symlink.yaml"
        assert boe_files.find_all_symlinks([pkg]) == [symlink]

    def test_broken_symlink_does_not_crash_discovery(self):
        """The specific defect the reviewer demonstrated: a dangling
        unmanifested symlink must not raise FileNotFoundError."""
        import boe_files
        pkg = FIXTURES / "invalid" / "broken-unmanifested-symlink"
        broken = pkg / "claim-broken-symlink.yaml"
        assert broken.is_symlink() and not broken.exists(), "Fixture symlink must be dangling"
        # Must not raise:
        files = boe_files.find_entity_files([pkg])
        assert broken not in files
        assert boe_files.find_all_symlinks([pkg]) == [broken]

    def test_load_yaml_reports_broken_symlink_as_diagnostic_not_crash(self):
        """Backstop test for load_yaml itself (independent of discovery
        skipping it first) — any future call site that hands load_yaml a
        dangling path must get an error tuple, never an exception."""
        import boe_files
        broken = FIXTURES / "invalid" / "broken-unmanifested-symlink" / "claim-broken-symlink.yaml"
        data, error = boe_files.load_yaml(broken)
        assert data is None
        assert error is not None and "could not read file" in error.lower()


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

    def test_cli_rejects_nonexistent_root_with_diagnostic_not_traceback(self, tmp_path):
        """M-18 (sixth-pass review): a nonexistent --root previously reached
        iterdir() unguarded and crashed with an uncaught FileNotFoundError."""
        result = self._run_cli(tmp_path / "does-not-exist")
        assert result.returncode != 0
        assert "Traceback" not in result.stderr, f"CLI crashed instead of reporting a diagnostic:\n{result.stderr}"
        assert "does not exist" in result.stdout

    def test_cli_rejects_root_that_is_a_file(self, tmp_path):
        """M-18: --root must be a directory, not just exist."""
        not_a_dir = tmp_path / "just-a-file"
        not_a_dir.write_text("not a directory")
        result = self._run_cli(not_a_dir)
        assert result.returncode != 0
        assert "Traceback" not in result.stderr, f"CLI crashed instead of reporting a diagnostic:\n{result.stderr}"
        assert "not a directory" in result.stdout

    def test_cli_rejects_symlinked_root(self, tmp_path):
        """M-18: --root itself must not be a symlink, consistent with the
        symlinked-package-root policy applied one level down."""
        real_target = tmp_path / "_outside"
        real_target.mkdir()
        alias = tmp_path / "alias-root"
        alias.symlink_to(real_target, target_is_directory=True)
        result = self._run_cli(alias)
        assert result.returncode != 0
        assert "Traceback" not in result.stderr, f"CLI crashed instead of reporting a diagnostic:\n{result.stderr}"
        assert "symlink" in result.stdout.lower()

    def test_cli_reports_unreadable_root_without_traceback(self, tmp_path):
        """M-21 (seventh-pass review): --root's existence/type/symlink
        checks (M-18) all pass for an unreadable directory — the crash
        happened one step later, at iterdir() itself, which raises
        PermissionError. That enumeration failure must also become a
        diagnostic."""
        unreadable = tmp_path / "no-access"
        unreadable.mkdir()
        (unreadable / "harbour-tender-inquiry").mkdir()
        unreadable.chmod(0o000)
        try:
            result = self._run_cli(unreadable)
        finally:
            unreadable.chmod(0o755)  # restore so pytest can clean up tmp_path
        if result.returncode == 0:
            pytest.skip("Directory permissions did not block enumeration in this environment (e.g. running as root)")
        assert "Traceback" not in result.stderr, f"CLI crashed instead of reporting a diagnostic:\n{result.stderr}"
        assert "could not enumerate" in result.stdout.lower()
