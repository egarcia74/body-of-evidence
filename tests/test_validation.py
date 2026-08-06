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

from boe_files import ValidationContext
from validate_schema import run_schema_validation
from validate_ids import run_id_validation, validate_id_format, validate_ulid
from validate_references import run_reference_validation
from validate_orphans import run_orphan_validation
from validate_provenance import run_provenance_validation

SCHEMA_DIR = REPO_ROOT / "schema"

# The dataclass InitVar name for PackageDiscovery's proof-of-walk token;
# asserted absent from constructed instances (see the H-23 tests below).
_WALK_TOKEN_NAME = "token"
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
            ValidationContext.for_paths([REPO_ROOT / "examples"]), SCHEMA_DIR, verbose=False
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
            context=ValidationContext.for_paths(valid_packages),
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
            context=ValidationContext.for_paths([pkg]), schema_dir=SCHEMA_DIR, verbose=False
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
                context=ValidationContext.for_paths([pkg]), schema_dir=SCHEMA_DIR, verbose=False
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
                # Root-cause-adjacent diagnostics for the same tracked
                # symlink, all declared explicitly rather than picking one
                # and hiding the rest:
                # - MANIFEST_PATH_SYMLINK: the manifest-listed path check
                #   (fourth-pass M-11) catches it as a LISTED entry.
                #   references-only — manifest-path validation only exists
                #   in validate_references.py.
                # - PACKAGE_SYMLINK: sixth-pass H-19's unconditional
                #   discovery-level check ALSO independently catches it —
                #   this is deliberately redundant with the check above;
                #   H-19 exists specifically because a symlinked file might
                #   NOT be manifest-listed (see investigation-root-symlink
                #   for the package-root case, and the H-19 fixtures below
                #   for the unmanifested case). Reported by ALL FIVE
                #   standalone validators (tenth-pass review M-27 — every
                #   check shares one boe_files.preflight_diagnostics call,
                #   not just references), same pattern as
                #   investigation-root-symlink below.
                # - MANIFEST_NO_INVESTIGATION: derived/cascading — the
                #   manifest's only Investigation entry is the rejected
                #   symlinked path, so the manifest also has no accepted
                #   Investigation (the case the fourth-pass review flagged
                #   as silently tolerated by the old substring-only test).
                #   references-only — manifest-content validation only
                #   exists in validate_references.py.
                ("ids", "PACKAGE_SYMLINK", "fixtures/invalid/manifest-symlink-escape/escape.yaml", ""),
                ("orphans", "PACKAGE_SYMLINK", "fixtures/invalid/manifest-symlink-escape/escape.yaml", ""),
                ("provenance", "PACKAGE_SYMLINK", "fixtures/invalid/manifest-symlink-escape/escape.yaml", ""),
                ("references", "MANIFEST_NO_INVESTIGATION", "fixtures/invalid/manifest-symlink-escape/package.yaml", ""),
                ("references", "MANIFEST_PATH_SYMLINK", "fixtures/invalid/manifest-symlink-escape/package.yaml", "escape.yaml"),
                ("references", "PACKAGE_SYMLINK", "fixtures/invalid/manifest-symlink-escape/escape.yaml", ""),
                ("schema", "PACKAGE_SYMLINK", "fixtures/invalid/manifest-symlink-escape/escape.yaml", ""),
            ]),
            ("investigation-root-symlink", [
                # A tracked symlink AT the package-directory level (not an
                # entity path inside one) — fifth-pass review H-15. Every
                # validator refuses to descend into it (boe_files skips a
                # symlinked root entirely) AND now reports it explicitly,
                # each under its own validator name (PR #13 review
                # follow-up to eighth-pass M-22: a validator that only saw
                # zero files for a symlinked root used to pass vacuously
                # instead of explaining why — schema was the sole
                # exception, via its pre-existing SCHEMA_VACUOUS_RUN
                # fallback, which no longer fires now that all_errors is
                # non-empty before that check runs).
                ("schema", "INVESTIGATION_ROOT_SYMLINK", "fixtures/invalid/investigation-root-symlink", ""),
                ("ids", "INVESTIGATION_ROOT_SYMLINK", "fixtures/invalid/investigation-root-symlink", ""),
                ("references", "INVESTIGATION_ROOT_SYMLINK", "fixtures/invalid/investigation-root-symlink", ""),
                ("orphans", "INVESTIGATION_ROOT_SYMLINK", "fixtures/invalid/investigation-root-symlink", ""),
                ("provenance", "INVESTIGATION_ROOT_SYMLINK", "fixtures/invalid/investigation-root-symlink", ""),
            ]),
            ("unmanifested-symlink", [
                # sixth-pass review H-19: a symlinked entity file that is
                # NOT listed in package.yaml at all (unlike
                # manifest-symlink-escape's escape.yaml, which IS listed).
                # The manifest-path containment check can't see this by
                # construction — it only inspects listed paths — which is
                # exactly why H-19 required an unconditional discovery-level
                # check independent of the manifest. Reported by ALL FIVE
                # standalone validators (tenth-pass review M-27), not just
                # references — see manifest-symlink-escape above.
                ("ids", "PACKAGE_SYMLINK",
                 "fixtures/invalid/unmanifested-symlink/claim-unlisted-symlink.yaml", ""),
                ("orphans", "PACKAGE_SYMLINK",
                 "fixtures/invalid/unmanifested-symlink/claim-unlisted-symlink.yaml", ""),
                ("provenance", "PACKAGE_SYMLINK",
                 "fixtures/invalid/unmanifested-symlink/claim-unlisted-symlink.yaml", ""),
                ("references", "PACKAGE_SYMLINK",
                 "fixtures/invalid/unmanifested-symlink/claim-unlisted-symlink.yaml", ""),
                ("schema", "PACKAGE_SYMLINK",
                 "fixtures/invalid/unmanifested-symlink/claim-unlisted-symlink.yaml", ""),
            ]),
            ("broken-unmanifested-symlink", [
                # Same as above, but the symlink target doesn't exist. Must
                # produce this diagnostic, not an uncaught FileNotFoundError
                # crashing the whole run (sixth-pass review H-19). Reported
                # by all five standalone validators (tenth-pass M-27).
                ("ids", "PACKAGE_SYMLINK",
                 "fixtures/invalid/broken-unmanifested-symlink/claim-broken-symlink.yaml", ""),
                ("orphans", "PACKAGE_SYMLINK",
                 "fixtures/invalid/broken-unmanifested-symlink/claim-broken-symlink.yaml", ""),
                ("provenance", "PACKAGE_SYMLINK",
                 "fixtures/invalid/broken-unmanifested-symlink/claim-broken-symlink.yaml", ""),
                ("references", "PACKAGE_SYMLINK",
                 "fixtures/invalid/broken-unmanifested-symlink/claim-broken-symlink.yaml", ""),
                ("schema", "PACKAGE_SYMLINK",
                 "fixtures/invalid/broken-unmanifested-symlink/claim-broken-symlink.yaml", ""),
            ]),
            ("symlinked-subdirectory", [
                # seventh-pass review M-20: the sixth-pass symlink scan only
                # looked at *.yaml/*.yml files, so a symlinked SUBDIRECTORY
                # (aliased-claims -> .../harbour-tender-inquiry/claims) was
                # invisible to it — rglob doesn't currently follow a
                # symlinked directory in this pathlib version, so nothing
                # inside it is actually read, but the symlink itself went
                # completely undetected. boe_files walks with
                # os.walk(followlinks=False), which lists but never
                # descends into it, so the symlink is now reported without
                # ever reading through it — by all five standalone
                # validators (tenth-pass review M-27).
                ("ids", "PACKAGE_SYMLINK",
                 "fixtures/invalid/symlinked-subdirectory/aliased-claims", ""),
                ("orphans", "PACKAGE_SYMLINK",
                 "fixtures/invalid/symlinked-subdirectory/aliased-claims", ""),
                ("provenance", "PACKAGE_SYMLINK",
                 "fixtures/invalid/symlinked-subdirectory/aliased-claims", ""),
                ("references", "PACKAGE_SYMLINK",
                 "fixtures/invalid/symlinked-subdirectory/aliased-claims", ""),
                ("schema", "PACKAGE_SYMLINK",
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
        assert pkg_a.exists(), "Missing cross_package fixture pkg-a"
        assert pkg_b.exists(), "Missing cross_package fixture pkg-b"

        passed, errors = run_reference_validation(
            context=ValidationContext.for_paths([pkg_a, pkg_b]), schema_dir=SCHEMA_DIR, verbose=False
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
            context=ValidationContext.for_paths([pkg_a, pkg_b]), schema_dir=SCHEMA_DIR, verbose=False
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
                passed, errors = check(context=ValidationContext.for_paths([pkg]), schema_dir=SCHEMA_DIR, verbose=False)
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
                context=ValidationContext.for_paths(order), schema_dir=SCHEMA_DIR, verbose=False
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
        entry and asserts each one actually produces EXACTLY REF_NOT_FOUND
        — an exact list, not membership (L-07, eighth-pass review: a
        membership assertion would miss an extra or duplicated diagnostic
        the registry entry also happened to produce)."""
        import validate_references as vr

        FAKE_ID = "boe:nonexistent:01JF0000000000000000000000"

        for entity_type, fields in vr.REFERENCE_FIELDS.items():
            for field, is_list, _want_type in fields:
                data = {"type": entity_type, field: [FAKE_ID] if is_list else FAKE_ID}
                errors = vr.validate_references_in_file(
                    Path(f"synthetic-{entity_type}.yaml"), data, id_index={}, entity_package=None
                )
                codes = sorted((e.code, e.location) for e in errors)
                expected_location = f"{field}[0]" if is_list else field
                assert codes == [("REF_NOT_FOUND", expected_location)], (
                    f"{entity_type}.{field}: registered but a dangling value "
                    f"produced {codes}, expected exactly one REF_NOT_FOUND — "
                    f"this registry entry is not actually executed"
                )

        for entity_type, nested_fields in vr.NESTED_REFERENCE_FIELDS.items():
            for array_field, item_field, _want_type in nested_fields:
                data = {"type": entity_type, array_field: [{item_field: FAKE_ID}]}
                errors = vr.validate_references_in_file(
                    Path(f"synthetic-{entity_type}.yaml"), data, id_index={}, entity_package=None
                )
                codes = sorted((e.code, e.location) for e in errors)
                expected_location = f"{array_field}[0].{item_field}"
                assert codes == [("REF_NOT_FOUND", expected_location)], (
                    f"{entity_type}.{array_field}[].{item_field}: registered "
                    f"but a dangling value produced {codes}, expected exactly "
                    f"one REF_NOT_FOUND — this nested registry entry is not "
                    f"actually executed"
                )

    def test_every_registered_field_enforces_currency_when_source_is_current(self):
        """L-07 (eighth-pass review): the dangling-reference test above
        proves every registered field is CHECKED, but only exercises
        REF_NOT_FOUND — none of the 32 registered locations were ever
        parameterized to prove REF_NOT_CURRENT (H-20) actually fires for
        each of them individually. This constructs, for every flat and
        nested registry entry, a CURRENT referencing entity (its own id and
        version_id ARE in current_maps) pointing at a reference that
        resolves to an EXISTING file in the right package and type but is
        NOT the manifest's current version — and asserts EXACTLY one
        REF_NOT_CURRENT.

        Renamed from `..._when_historical` (tenth-pass review M-28): the
        original name and docstring claimed this proved the H-21 historical
        exemption across all 32 locations. It does not — `self_id` is
        present in `current_maps`, so `referencing_is_current` is True
        throughout, meaning this test exercises ONLY the current-source
        case. See `test_every_registered_field_exempts_historical_source_from_currency`
        below for the actual historical-source coverage."""
        import validate_references as vr

        pkg = Path("synthetic-pkg")
        self_id = "boe:synthetic-self:01JF00000000000000000SELF"
        self_version = "01JFV00000000000000000SELF"
        current_maps = {pkg: {self_id: self_version}}  # target id deliberately absent

        def _target_id(want_type):
            return f"boe:{want_type or 'synthetic-target'}:01JF000000000000000000TRGT"

        for entity_type, fields in vr.REFERENCE_FIELDS.items():
            for field, is_list, want_type in fields:
                target_id = _target_id(want_type)
                id_index = {target_id: [{"path": Path("target.yaml"), "package": pkg}]}
                data = {
                    "type": entity_type, "id": self_id, "version_id": self_version,
                    field: [target_id] if is_list else target_id,
                }
                errors = vr.validate_references_in_file(
                    Path("synthetic.yaml"), data, id_index, entity_package=pkg, current_maps=current_maps
                )
                codes = sorted((e.code, e.location) for e in errors)
                expected_location = f"{field}[0]" if is_list else field
                assert codes == [("REF_NOT_CURRENT", expected_location)], (
                    f"{entity_type}.{field}: a reference to an existing but "
                    f"non-current target produced {codes}, expected exactly "
                    f"one REF_NOT_CURRENT"
                )

        for entity_type, nested_fields in vr.NESTED_REFERENCE_FIELDS.items():
            for array_field, item_field, want_type in nested_fields:
                target_id = _target_id(want_type)
                id_index = {target_id: [{"path": Path("target.yaml"), "package": pkg}]}
                data = {
                    "type": entity_type, "id": self_id, "version_id": self_version,
                    array_field: [{item_field: target_id}],
                }
                errors = vr.validate_references_in_file(
                    Path("synthetic.yaml"), data, id_index, entity_package=pkg, current_maps=current_maps
                )
                codes = sorted((e.code, e.location) for e in errors)
                expected_location = f"{array_field}[0].{item_field}"
                assert codes == [("REF_NOT_CURRENT", expected_location)], (
                    f"{entity_type}.{array_field}[].{item_field}: a reference "
                    f"to an existing but non-current target produced {codes}, "
                    f"expected exactly one REF_NOT_CURRENT"
                )

    def test_every_registered_field_exempts_historical_source_from_currency(self):
        """M-28 (tenth-pass review): the H-21 historical-reference exemption
        (D-023) is proven end-to-end for exactly two hand-picked cases by
        TestHistoricalReferencesRemainValid, but was never parameterized
        across all 32 registered flat and nested reference locations the
        way REF_NOT_FOUND and current-source REF_NOT_CURRENT are above. A
        previous version of this test claimed to provide that coverage; it
        did not (see the renamed test above) — its `self_id` was present in
        `current_maps`, so every field it exercised had a CURRENT
        referencing entity, never a historical one.

        This constructs, for every flat and nested registry entry, a
        HISTORICAL referencing entity — `self_id`/`self_version` are
        deliberately ABSENT from `current_maps`, so
        `validate_references_in_file` computes `referencing_is_current =
        False` — pointing at a reference that resolves to an EXISTING file
        in the right package and type but is NOT the manifest's current
        version. Per D-023/H-21, a historical source is exempt from
        currency: asserts NO REF_NOT_CURRENT (or any other diagnostic) is
        produced for that field, for every one of the 32 locations."""
        import validate_references as vr

        pkg = Path("synthetic-pkg")
        self_id = "boe:synthetic-self:01JF00000000000000000SELF"
        self_version = "01JFV00000000000000000SELF"
        # self_id deliberately ABSENT from current_maps — this is what
        # makes the referencing entity historical, not current.
        current_maps = {pkg: {}}

        def _target_id(want_type):
            return f"boe:{want_type or 'synthetic-target'}:01JF000000000000000000TRGT"

        for entity_type, fields in vr.REFERENCE_FIELDS.items():
            for field, is_list, want_type in fields:
                target_id = _target_id(want_type)
                id_index = {target_id: [{"path": Path("target.yaml"), "package": pkg}]}
                data = {
                    "type": entity_type, "id": self_id, "version_id": self_version,
                    field: [target_id] if is_list else target_id,
                }
                errors = vr.validate_references_in_file(
                    Path("synthetic.yaml"), data, id_index, entity_package=pkg, current_maps=current_maps
                )
                assert errors == [], (
                    f"{entity_type}.{field}: a historical referencing entity "
                    f"pointing at an existing, correctly-typed, same-package "
                    f"but non-current target produced {errors}, expected no "
                    f"diagnostics — historical sources are exempt from "
                    f"manifest currency (D-023/H-21)"
                )

        for entity_type, nested_fields in vr.NESTED_REFERENCE_FIELDS.items():
            for array_field, item_field, want_type in nested_fields:
                target_id = _target_id(want_type)
                id_index = {target_id: [{"path": Path("target.yaml"), "package": pkg}]}
                data = {
                    "type": entity_type, "id": self_id, "version_id": self_version,
                    array_field: [{item_field: target_id}],
                }
                errors = vr.validate_references_in_file(
                    Path("synthetic.yaml"), data, id_index, entity_package=pkg, current_maps=current_maps
                )
                assert errors == [], (
                    f"{entity_type}.{array_field}[].{item_field}: a historical "
                    f"referencing entity pointing at an existing, correctly-"
                    f"typed, same-package but non-current target produced "
                    f"{errors}, expected no diagnostics — historical sources "
                    f"are exempt from manifest currency (D-023/H-21)"
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
            context=ValidationContext.for_paths([pkg]), schema_dir=SCHEMA_DIR, verbose=False
        )
        not_current = [e for e in errors if e.code == "REF_NOT_CURRENT"]
        assert not not_current, f"Valid fixture's current references were rejected: {not_current}"
        assert passed, f"Valid fixture unexpectedly failed references: {[str(e) for e in errors]}"


class TestHistoricalReferencesRemainValid:
    """H-21 (eighth-pass review): H-20's currency rule is about the CURRENT
    released graph — it must not be imposed on a reference made BY a
    historical/superseded entity version. A historical ClaimEvidenceLink
    describing what it referenced at that point in time must remain valid
    even after the referenced entity is later retired entirely; otherwise
    valid history becomes impossible to keep. Historical files still get
    ordinary existence/type/package checks — only the "target must be
    current" rule is exempted."""

    def _write(self, path: Path, **fields):
        path.write_text(yaml.safe_dump(fields, sort_keys=False))

    def test_historical_link_referencing_retired_evidence_is_not_rejected(self, tmp_path):
        pkg = tmp_path / "pkg"
        pkg.mkdir()

        self._write(
            pkg / "investigation.yaml",
            id="boe:investigation:01JF00000000000000000A0001",
            version_id="01JFV0000000000000000A0001",
            type="investigation",
        )
        self._write(
            pkg / "claim.yaml",
            id="boe:claim:01JF00000000000000000A0002",
            version_id="01JFV0000000000000000A0002",
            type="claim",
        )
        # Retired: exists on disk (D-009 historical version) but NOT listed
        # in the manifest — exactly the unmanifested-by-design case H-20
        # was written to catch when the REFERENCE is current.
        self._write(
            pkg / "evidence-retired.yaml",
            id="boe:evidence:01JF00000000000000000A0003",
            version_id="01JFV0000000000000000A0003",
            type="evidence",
        )
        # Historical: also unmanifested. References the retired evidence —
        # this is the probe the review demonstrated failing.
        self._write(
            pkg / "link-historical.yaml",
            id="boe:claim_evidence_link:01JF00000000000000000A0004",
            version_id="01JFV0000000000000000A0004",
            type="claim_evidence_link",
            claim_id="boe:claim:01JF00000000000000000A0002",
            evidence_id="boe:evidence:01JF00000000000000000A0003",
        )
        self._write(
            pkg / "package.yaml",
            manifest_version="1",
            investigation_id="boe:investigation:01JF00000000000000000A0001",
            slug="pkg",
            entities=[
                {"id": "boe:investigation:01JF00000000000000000A0001",
                 "version_id": "01JFV0000000000000000A0001", "path": "investigation.yaml"},
                {"id": "boe:claim:01JF00000000000000000A0002",
                 "version_id": "01JFV0000000000000000A0002", "path": "claim.yaml"},
            ],
        )

        passed, errors = run_reference_validation(
            context=ValidationContext.for_paths([pkg]), schema_dir=SCHEMA_DIR, verbose=False
        )
        not_current = [e for e in errors if e.code == "REF_NOT_CURRENT"]
        assert not not_current, (
            f"A historical link's reference to a retired entity must not be "
            f"held to current-manifest membership: {[str(e) for e in not_current]}"
        )
        assert passed, f"Historical reference unexpectedly failed: {[str(e) for e in errors]}"

    def test_historical_file_referencing_something_nonexistent_still_fails(self, tmp_path):
        """A historical referencing file is exempt from REF_NOT_CURRENT, not
        from every check — a dangling reference must still be REF_NOT_FOUND
        even when it originates from a historical file."""
        pkg = tmp_path / "pkg"
        pkg.mkdir()

        self._write(
            pkg / "investigation.yaml",
            id="boe:investigation:01JF00000000000000000B0001",
            version_id="01JFV0000000000000000B0001",
            type="investigation",
        )
        self._write(
            pkg / "claim.yaml",
            id="boe:claim:01JF00000000000000000B0002",
            version_id="01JFV0000000000000000B0002",
            type="claim",
        )
        self._write(
            pkg / "link-historical.yaml",
            id="boe:claim_evidence_link:01JF00000000000000000B0003",
            version_id="01JFV0000000000000000B0003",
            type="claim_evidence_link",
            claim_id="boe:claim:01JF00000000000000000B0002",
            evidence_id="boe:evidence:01JF00000000000000000B9999",  # never existed
        )
        self._write(
            pkg / "package.yaml",
            manifest_version="1",
            investigation_id="boe:investigation:01JF00000000000000000B0001",
            slug="pkg",
            entities=[
                {"id": "boe:investigation:01JF00000000000000000B0001",
                 "version_id": "01JFV0000000000000000B0001", "path": "investigation.yaml"},
                {"id": "boe:claim:01JF00000000000000000B0002",
                 "version_id": "01JFV0000000000000000B0002", "path": "claim.yaml"},
            ],
        )

        passed, errors = run_reference_validation(
            context=ValidationContext.for_paths([pkg]), schema_dir=SCHEMA_DIR, verbose=False
        )
        assert not passed
        assert any(e.code == "REF_NOT_FOUND" for e in errors), (
            f"A historical file's dangling reference must still be REF_NOT_FOUND: {[str(e) for e in errors]}"
        )


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
        assert broken.is_symlink(), "Fixture must be a symlink"
        assert not broken.exists(), "Fixture symlink must be dangling"
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
        assert error is not None
        assert "could not read file" in error.lower()


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

    def test_cli_rejects_dangling_symlinked_sibling_package(self, tmp_path):
        """H-22 (eighth-pass review): a DANGLING package-root symlink fails
        is_dir() and was previously invisible to default CLI discovery
        entirely — silently excluded before the symlink validator ever ran,
        rather than rejected like the live-symlink case above. Whether a
        symlink is dangling is environment-dependent (it could resolve to
        real, sensitive content elsewhere), so passing CI must not depend
        on it happening to be broken here."""
        shutil.copytree(FIXTURES / "valid" / "harbour-tender-inquiry", tmp_path / "harbour-tender-inquiry")
        (tmp_path / "dangling-alias").symlink_to(tmp_path / "_does-not-exist", target_is_directory=True)
        result = self._run_cli(tmp_path)
        assert result.returncode != 0, (
            f"CLI silently accepted a dangling package-root symlink under --root:\n{result.stdout}"
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
            # L-08 (eighth-pass review): skipping whenever the CLI returns 0
            # is the wrong test for "did permissions actually block
            # enumeration" — in a privileged environment enumeration can
            # succeed while some LATER check still returns non-zero for an
            # unrelated reason, which would make this test fail for the
            # wrong reason instead of skipping. Check the local filesystem
            # operation directly first; only invoke the CLI (and assert on
            # its diagnostic) once we know PermissionError actually fires
            # here.
            try:
                list(unreadable.iterdir())
            except PermissionError:
                pass
            else:
                pytest.skip("Directory permissions did not block enumeration in this environment (e.g. running as root)")
            result = self._run_cli(unreadable)
        finally:
            unreadable.chmod(0o755)  # restore so pytest can clean up tmp_path
        assert "Traceback" not in result.stderr, f"CLI crashed instead of reporting a diagnostic:\n{result.stderr}"
        assert "could not enumerate" in result.stdout.lower()


class TestUnreadableSubtreeFailsClosed:
    """M-22 (eighth-pass review): os.walk without an `onerror` callback
    silently skips any subdirectory it cannot list — a package containing
    an unreadable subtree (which could just as easily be hiding a
    prohibited symlink or a policy-violating entity file) was certified as
    clean without ever having been fully inspected."""

    def test_find_all_symlinks_reports_unreadable_subtree_as_error_not_silence(self, tmp_path):
        import boe_files
        pkg = tmp_path / "pkg"
        locked = pkg / "locked"
        locked.mkdir(parents=True)
        (locked / "hidden-symlink.yaml").symlink_to(
            FIXTURES / "valid" / "harbour-tender-inquiry" / "investigation.yaml"
        )
        locked.chmod(0o000)
        try:
            if list_dir_is_readable(locked):
                pytest.skip("Directory permissions did not block traversal in this environment (e.g. running as root)")
            symlinks = boe_files.find_all_symlinks([pkg])
            errors = boe_files.find_traversal_errors([pkg])
        finally:
            locked.chmod(0o755)  # restore so pytest can clean up tmp_path

        assert symlinks == [], (
            f"A symlink inside an unreadable directory cannot be seen "
            f"directly by definition, got: {symlinks}"
        )
        assert len(errors) == 1, f"Expected exactly one traversal error, got: {errors}"
        assert errors[0][0] == pkg

    def test_run_reference_validation_fails_closed_on_unreadable_subtree(self, tmp_path):
        pkg = tmp_path / "pkg"
        shutil.copytree(FIXTURES / "valid" / "harbour-tender-inquiry", pkg)
        locked = pkg / "locked-subdir"
        locked.mkdir()
        locked.chmod(0o000)
        try:
            if list_dir_is_readable(locked):
                pytest.skip("Directory permissions did not block traversal in this environment (e.g. running as root)")
            passed, errors = run_reference_validation(
                context=ValidationContext.for_paths([pkg]), schema_dir=SCHEMA_DIR, verbose=False
            )
        finally:
            locked.chmod(0o755)  # restore so pytest can clean up tmp_path

        assert not passed, "An unreadable subtree must fail validation, not silently pass"
        assert any(e.code == "PACKAGE_SUBTREE_UNREADABLE" for e in errors), (
            f"Expected a PACKAGE_SUBTREE_UNREADABLE diagnostic, got: {[str(e) for e in errors]}"
        )

    @pytest.mark.parametrize("check_fn", ALL_CHECKS, ids=lambda f: f.__module__)
    def test_every_single_check_fails_closed_on_unreadable_subtree(self, tmp_path, check_fn):
        """Follow-up finding (automated review, post-M-22): the initial fix
        only wired find_traversal_errors into run_reference_validation. A
        standalone invocation of any OTHER check — e.g. `--check schema` —
        still walked entity files via find_entity_files/iter_entities,
        which silently omits an unreadable subtree the same way
        find_all_symlinks did, and so could certify an incompletely-
        inspected package on its own. Every run_*_validation function must
        independently fail closed, not just references — this proves it
        for all five."""
        # Named to match the fixture's manifest slug — an arbitrary
        # destination name (as the looser test above uses) would also
        # legitimately produce MANIFEST_SLUG_MISMATCH, which this test's
        # exact assertion must not have to account for.
        pkg = tmp_path / "harbour-tender-inquiry"
        shutil.copytree(FIXTURES / "valid" / "harbour-tender-inquiry", pkg)
        locked = pkg / "locked-subdir"
        locked.mkdir()
        locked.chmod(0o000)
        try:
            if list_dir_is_readable(locked):
                pytest.skip("Directory permissions did not block traversal in this environment (e.g. running as root)")
            passed, errors = check_fn(context=ValidationContext.for_paths([pkg]), schema_dir=SCHEMA_DIR, verbose=False)
        finally:
            locked.chmod(0o755)  # restore so pytest can clean up tmp_path

        assert not passed, (
            f"{check_fn.__module__}: an unreadable subtree must fail this "
            f"check on its own, not silently pass"
        )
        # Exact (validator, code, path, location) tuples — the same shape
        # TestInvalidFixtures uses — not just membership, so an extra or
        # duplicated diagnostic would be caught too (CodeRabbit finding).
        actual = sorted((e.validator, e.code, e.path, e.location) for e in errors)
        expected_validator = check_fn.__module__.replace("validate_", "", 1)
        assert actual == [(expected_validator, "PACKAGE_SUBTREE_UNREADABLE", str(locked), "")], (
            f"{check_fn.__module__}: expected exactly one "
            f"PACKAGE_SUBTREE_UNREADABLE diagnostic under its own validator "
            f"name, got: {actual}"
        )

    @pytest.mark.parametrize("check_fn", ALL_CHECKS, ids=lambda f: f.__module__)
    def test_every_single_check_fails_closed_on_symlinked_root(self, tmp_path, check_fn):
        """Same class of gap as the unreadable-subtree test above, but at
        the package ROOT rather than a subtree: find_entity_files silently
        skips a symlinked investigation root entirely (by design), so a
        validator that only calls find_entity_files/iter_entities saw zero
        files for that path and passed VACUOUSLY — only references had its
        own INVESTIGATION_ROOT_SYMLINK check. This proves the other four
        now reject it too, each under its own validator name."""
        real_target = tmp_path / "_outside"
        shutil.copytree(FIXTURES / "valid" / "harbour-tender-inquiry", real_target)
        symlinked_root = tmp_path / "alias"
        symlinked_root.symlink_to(real_target, target_is_directory=True)

        passed, errors = check_fn(context=ValidationContext.for_paths([symlinked_root]), schema_dir=SCHEMA_DIR, verbose=False)

        assert not passed, (
            f"{check_fn.__module__}: a symlinked package root must fail this "
            f"check on its own, not silently pass"
        )
        actual = sorted((e.validator, e.code, e.path, e.location) for e in errors)
        expected_validator = check_fn.__module__.replace("validate_", "", 1)
        assert actual == [(expected_validator, "INVESTIGATION_ROOT_SYMLINK", str(symlinked_root), "")], (
            f"{check_fn.__module__}: expected exactly one "
            f"INVESTIGATION_ROOT_SYMLINK diagnostic under its own validator "
            f"name, got: {actual}"
        )

    @pytest.mark.parametrize("check_fn", ALL_CHECKS, ids=lambda f: f.__module__)
    def test_every_single_check_fails_closed_on_internal_symlink(self, tmp_path, check_fn):
        """M-27 (tenth-pass review): the same vacuous-pass failure class as
        the unreadable-subtree and symlinked-root tests above, but for an
        ordinary INTERNAL symlink — a file inside the package, not the
        root, not manifest-listed. Before this fix, only
        run_reference_validation rejected internal symlinks
        (PACKAGE_SYMLINK); the other four standalone checks reached the
        symlinked file via find_entity_files, which already silently
        excludes symlinks by design, and so passed VACUOUSLY without ever
        explaining why. This proves all five now reject it, each under its
        own validator name, from one shared ValidationContext walk (not five
        independent ones)."""
        pkg = tmp_path / "harbour-tender-inquiry"
        shutil.copytree(FIXTURES / "valid" / "harbour-tender-inquiry", pkg)
        stray_symlink = pkg / "claims" / "stray-symlink.yaml"
        stray_symlink.symlink_to(pkg / "investigation.yaml")

        passed, errors = check_fn(context=ValidationContext.for_paths([pkg]), schema_dir=SCHEMA_DIR, verbose=False)

        assert not passed, (
            f"{check_fn.__module__}: an internal symlink must fail this "
            f"check on its own, not silently pass"
        )
        actual = sorted((e.validator, e.code, e.path, e.location) for e in errors)
        expected_validator = check_fn.__module__.replace("validate_", "", 1)
        assert actual == [(expected_validator, "PACKAGE_SYMLINK", str(stray_symlink), "")], (
            f"{check_fn.__module__}: expected exactly one PACKAGE_SYMLINK "
            f"diagnostic under its own validator name, got: {actual}"
        )


class TestSharedDiscoveryAcrossChecks:
    """Tenth-pass review CodeRabbit follow-up to D-024/M-24: the initial fix
    made each run_*_validation build its own discovery exactly once, but
    run_all_checks (the actual CLI/self-test entry point) still called each
    of the five checks independently, so a real `--check all` invocation —
    or a single --self-test fixture pass — walked every package root once
    PER VALIDATOR, five times total, not once for the whole run. The claim
    "one walk per package" was true per validator call, false for a full
    run. run_all_checks now builds one ValidationContext and passes it to
    every check.

    Eleventh-pass review L-12: the original version of this test patched
    the discover_package FACTORY and counted its calls, which proves the
    wiring but not the I/O invariant — it would still have passed if a
    validator reached past the factory to _walk_package or to one of the
    retained find_* primitives, which is exactly the escape hatch the claim
    needs to exclude. The factory-call test is kept below as a wiring test;
    the authoritative one patches _walk_package, the single function in the
    codebase that actually touches the directory tree."""

    @staticmethod
    def _counting(monkeypatch, attr):
        """Patch boe_files.<attr> with a call-counting wrapper. Both the
        factory and _walk_package are looked up as module globals at call
        time, so patching here reaches every caller including validators
        that imported names via `from boe_files import ...`."""
        import boe_files

        calls = []
        real = getattr(boe_files, attr)

        def counting(inv_path, *args, **kwargs):
            calls.append(inv_path)
            return real(inv_path, *args, **kwargs)

        monkeypatch.setattr(boe_files, attr, counting)
        return calls

    def test_run_all_checks_walks_each_package_exactly_once(self, monkeypatch):
        """The real I/O invariant: one filesystem traversal per package root
        for a complete five-check run, counted at _walk_package itself."""
        import validate as v

        walks = self._counting(monkeypatch, "_walk_package")

        pkg = FIXTURES / "valid" / "harbour-tender-inquiry"
        passed, results = v.run_all_checks([pkg], SCHEMA_DIR, False, v.CHECKS)

        assert passed, f"Valid fixture must pass run_all_checks: {results}"
        assert walks == [pkg], (
            f"Expected exactly one _walk_package call for one package root "
            f"across all five checks, got {walks} — a check is traversing "
            f"the tree independently instead of using the context "
            f"run_all_checks already built"
        )

    def test_run_all_checks_walks_each_of_several_packages_exactly_once(self, monkeypatch):
        """One walk PER ROOT, not one walk total — a context that dropped or
        deduplicated a root would pass a single-package version of this test.
        """
        import validate as v

        walks = self._counting(monkeypatch, "_walk_package")

        pkg_a = FIXTURES / "cross_package" / "pkg-a"
        pkg_b = FIXTURES / "cross_package" / "pkg-b"
        v.run_all_checks([pkg_a, pkg_b], SCHEMA_DIR, False, v.CHECKS)

        assert sorted(walks) == sorted([pkg_a, pkg_b]), (
            f"Expected exactly one _walk_package call per package root, got {walks}"
        )

    def test_run_all_checks_builds_the_discovery_factory_once_per_package(self, monkeypatch):
        """Wiring-level companion to the traversal test above: the context
        factory itself is also invoked once per root, so a regression that
        rebuilt contexts per validator is reported as such rather than only
        showing up as extra walks."""
        import validate as v

        built = self._counting(monkeypatch, "discover_package")

        pkg = FIXTURES / "valid" / "harbour-tender-inquiry"
        v.run_all_checks([pkg], SCHEMA_DIR, False, v.CHECKS)

        assert built == [pkg], (
            f"Expected exactly one discover_package call for one package "
            f"root across all five checks, got {built}"
        )

    def test_each_document_is_read_exactly_once_per_run(self, monkeypatch):
        """Eleventh-pass review M-29: five validators re-opening the same
        paths could each observe different bytes, so "the package that
        passed schema validation" and "the package that passed reference
        validation" were not necessarily the same content. Content is now
        read once at discovery and shared, so every validator in a run
        inspects identical bytes."""
        import boe_files
        import validate as v

        pkg = FIXTURES / "valid" / "harbour-tender-inquiry"
        # Build the expectation BEFORE patching, so this probe's own reads
        # are not counted as the run's.
        context = boe_files.ValidationContext.for_paths([pkg])
        expected = set(context.entity_files()) | {pkg / boe_files.MANIFEST_NAME}

        reads = self._counting(monkeypatch, "load_yaml")
        passed, results = v.run_all_checks([pkg], SCHEMA_DIR, False, v.CHECKS)

        assert passed, f"Valid fixture must pass run_all_checks: {results}"
        assert len(reads) == len(set(reads)), (
            f"Every document must be read exactly once per run; these were "
            f"read more than once: "
            f"{sorted({p for p in reads if reads.count(p) > 1})}"
        )
        assert set(reads) == expected, (
            f"Reads did not match the discovered document set. "
            f"Unexpected: {set(reads) - expected}; missing: {expected - set(reads)}"
        )


class TestValidationContextIsSelfConsistent:
    """Eleventh-pass review H-23. Every run_*_validation used to accept BOTH
    `investigation_paths` and an optional `discoveries` list, with no
    boundary checking that the two described the same packages. The review
    passed an EMPTY discovery alongside the known-invalid
    fixtures/invalid/duplicate-version-id root and got `passed=True,
    errors=[]` — a vacuous pass, which core invariant 10 exists to prohibit.

    The fix is structural rather than defensive: roots are DERIVED from the
    discoveries, so a context whose roots and discovery disagree cannot be
    constructed at all. These tests pin that down from both directions —
    the known-invalid package cannot be hidden, AND the inconsistent inputs
    that used to hide it are now rejected at construction."""

    INVALID_PKG = FIXTURES / "invalid" / "duplicate-version-id"

    @pytest.mark.parametrize("check_fn", ALL_CHECKS, ids=lambda f: f.__module__)
    def test_no_check_accepts_a_bare_path_list_in_place_of_a_context(self, check_fn):
        """The old vacuous-pass shape is now a type error, not a silent
        success: there is no parameter left that takes roots separately."""
        with pytest.raises((TypeError, AttributeError)):
            check_fn(
                context=[self.INVALID_PKG], schema_dir=SCHEMA_DIR, verbose=False
            )

    def test_known_invalid_package_is_rejected_through_its_own_context(self):
        """Baseline for the tests below: built the one supported way, this
        package fails. Any 'passed' result in this class is therefore a real
        finding about the API, not about the fixture."""
        passed, errors = run_id_validation(
            context=ValidationContext.for_paths([self.INVALID_PKG]),
            schema_dir=SCHEMA_DIR, verbose=False,
        )
        assert not passed and errors, (
            "fixtures/invalid/duplicate-version-id must fail id validation"
        )

    def test_empty_context_cannot_be_pointed_at_a_package(self):
        """The review's exact probe: an empty discovery can still be built,
        but it no longer carries the invalid root along with it — validating
        nothing now reports nothing, and the CLI's own empty-run guard
        (validate.py main) is what turns that into a failure."""
        passed, errors = run_id_validation(
            context=ValidationContext(discoveries=()),
            schema_dir=SCHEMA_DIR, verbose=False,
        )
        assert passed and errors == [], (
            "An empty context validates nothing, so it has nothing to report"
        )
        # The point being that it cannot ALSO claim to have covered a root.
        assert ValidationContext(discoveries=()).roots == ()

    @pytest.mark.parametrize("documents", [
        pytest.param("empty", id="empty-discovery"),
        pytest.param("foreign", id="foreign-discovery"),
    ])
    def test_a_fabricated_discovery_cannot_be_built_at_all(self, documents):
        """The review's required proof, at its root cause: an EMPTY discovery
        claiming a known-invalid package, and a FOREIGN one carrying another
        package's documents, are both unconstructible. Only discover_package
        holds the proof-of-walk token, so no caller can assert something
        about a package without having actually walked it."""
        import boe_files

        if documents == "empty":
            docs = ()
        else:
            docs = boe_files.discover_package(
                FIXTURES / "valid" / "harbour-tender-inquiry"
            ).documents

        with pytest.raises(ValueError, match="must be built by discover_package"):
            boe_files.PackageDiscovery(
                root=self.INVALID_PKG, documents=docs, manifest=None,
                root_is_symlink=False, internal_symlinks=(), traversal_errors=(),
            )

    def test_containment_is_enforced_beneath_the_walk_token(self):
        """Defence in depth: even reaching past the proof-of-walk guard —
        which only test code can do, by importing the private token — a
        discovery whose contents belong to a different root is rejected. The
        token stops fabrication; this stops a future factory bug from
        producing a self-inconsistent discovery."""
        import boe_files

        foreign = boe_files.discover_package(FIXTURES / "valid" / "harbour-tender-inquiry")
        with pytest.raises(ValueError, match="outside that root"):
            boe_files.PackageDiscovery(
                root=self.INVALID_PKG, documents=foreign.documents, manifest=None,
                root_is_symlink=False, internal_symlinks=(), traversal_errors=(),
                token=boe_files._WALK_TOKEN,
            )

    def test_a_real_discovery_of_the_invalid_package_still_reports_it(self):
        """The complement of the fabrication tests: the ONLY discovery a
        caller can obtain for this package is a truthful one, and a truthful
        one still fails. There is no constructible input to run_id_validation
        that names this package and reports it clean."""
        import boe_files

        real = boe_files.discover_package(self.INVALID_PKG)
        assert real.documents, "A real walk of this fixture finds its files"
        passed, errors = run_id_validation(
            context=ValidationContext(discoveries=(real,)),
            schema_dir=SCHEMA_DIR, verbose=False,
        )
        assert not passed and errors

    def test_a_real_discovery_does_not_hand_out_the_proof_token(self):
        """Caught by the local CodeRabbit pass on this response: the token
        was first written as a stored field, so `discovery.token` returned
        `_WALK_TOKEN` — and every validator holds real discoveries, making
        the guarantee self-defeating. It is an InitVar now: consumed at
        construction, never stored."""
        import boe_files

        real = boe_files.discover_package(self.INVALID_PKG)
        assert _WALK_TOKEN_NAME not in vars(real), (
            f"'{_WALK_TOKEN_NAME}' must not be stored on a discovery instance"
        )
        # The InitVar's declared default leaves a class attribute behind, so
        # the attribute resolves — what matters is that it is NOT the token.
        assert getattr(real, _WALK_TOKEN_NAME, None) is not boe_files._WALK_TOKEN, (
            "PackageDiscovery must not expose the proof-of-walk token — any "
            "holder of a real discovery could read it and forge one"
        )
        # And the forgery that would enable is still refused.
        with pytest.raises(ValueError, match="must be built by discover_package"):
            boe_files.PackageDiscovery(
                root=self.INVALID_PKG, documents=(), manifest=None,
                root_is_symlink=False, internal_symlinks=(), traversal_errors=(),
                token=getattr(real, _WALK_TOKEN_NAME, None),
            )

    def test_manifest_entry_pointing_at_a_non_entity_path_fails_closed(self, tmp_path):
        """A manifest entry whose path exists but is not a discovered entity
        document (here: the manifest itself) must be reported, not skipped.
        Reading such a path used to be attempted directly, so a failure
        silently bypassed the id/version_id checks — fail-open. Also caught
        by the local CodeRabbit pass on this response."""
        pkg = tmp_path / "harbour-tender-inquiry"
        shutil.copytree(FIXTURES / "valid" / "harbour-tender-inquiry", pkg)
        manifest_path = pkg / "package.yaml"
        manifest = yaml.safe_load(manifest_path.read_text())
        manifest["entities"].append({
            "id": "boe:claim:01JQ0000000000000000000000",
            "version_id": "01JQV000000000000000000000",
            "path": "package.yaml",
        })
        manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False))

        passed, errors = run_reference_validation(
            context=ValidationContext.for_paths([pkg]), schema_dir=SCHEMA_DIR, verbose=False
        )
        assert not passed
        assert any(
            e.code == "MANIFEST_PATH_NOT_AN_ENTITY" and e.location == "package.yaml"
            for e in errors
        ), f"Expected MANIFEST_PATH_NOT_AN_ENTITY for the package.yaml entry, got: {errors}"

    def test_context_rejects_duplicate_roots(self):
        """A root listed twice would validate the package twice and report
        every diagnostic twice — which the exact, duplicate-preserving
        assertions elsewhere in this file would then read as real
        duplicates."""
        import boe_files

        d = boe_files.discover_package(self.INVALID_PKG)
        with pytest.raises(ValueError, match="duplicate package roots"):
            ValidationContext(discoveries=(d, d))

    def test_context_rejects_a_mutable_discoveries_collection(self):
        import boe_files

        with pytest.raises(TypeError, match="must be a tuple"):
            ValidationContext(discoveries=[boe_files.discover_package(self.INVALID_PKG)])


class TestDiscoveryIsGenuinelyImmutable:
    """Eleventh-pass review M-29: PackageDiscovery was declared
    `@dataclass(frozen=True)` while holding ordinary mutable lists, and the
    review demonstrated the gap by calling `.clear()` on a discovery's file
    list after construction. `frozen=True` prevents field REASSIGNMENT; it
    does not freeze objects stored in the fields."""

    @pytest.mark.parametrize(
        "field", ["documents", "internal_symlinks", "traversal_errors"]
    )
    def test_collection_fields_are_tuples(self, field):
        import boe_files

        d = boe_files.discover_package(FIXTURES / "valid" / "harbour-tender-inquiry")
        value = getattr(d, field)
        assert isinstance(value, tuple), (
            f"{field} is {type(value).__name__}, not a tuple — a frozen "
            f"dataclass holding a mutable list is not immutable"
        )
        with pytest.raises(AttributeError):
            value.clear()

    def test_constructing_with_a_list_is_rejected(self):
        """Reaches past the proof-of-walk token (see
        TestValidationContextIsSelfConsistent) to test the layer beneath it:
        a future factory change that produced lists would be caught here
        rather than silently reintroducing mutable state."""
        import boe_files

        with pytest.raises(TypeError, match="must be a tuple"):
            boe_files.PackageDiscovery(
                root=FIXTURES / "valid" / "harbour-tender-inquiry",
                documents=[], manifest=None, root_is_symlink=False,
                internal_symlinks=(), traversal_errors=(),
                token=boe_files._WALK_TOKEN,
            )

    def test_symlinked_root_discovery_must_be_empty(self):
        """`root_is_symlink=True` means the walk never happened, so a
        discovery asserting both is internally contradictory."""
        import boe_files

        real = boe_files.discover_package(FIXTURES / "valid" / "harbour-tender-inquiry")
        with pytest.raises(ValueError, match="must be"):
            boe_files.PackageDiscovery(
                root=real.root, documents=real.documents, manifest=None,
                root_is_symlink=True, internal_symlinks=(), traversal_errors=(),
                token=boe_files._WALK_TOKEN,
            )


def list_dir_is_readable(path: Path) -> bool:
    """True if listing `path` succeeds despite an attempted chmod(0o000) —
    e.g. when the test runs as root, where permission bits don't apply."""
    try:
        list(path.iterdir())
    except PermissionError:
        return False
    return True
