#!/usr/bin/env python3
"""
Body of Evidence — Reference Validation

Checks that every ID referenced in any entity resolves to the CURRENT
version of an entity of the EXPECTED TYPE, owned by the SAME PACKAGE, and
that package manifests are consistent with the entity files they list.

Package scoping (fifth-pass review finding H-02c): investigation packages
are meant to be self-contained. By default, EVERY reference below must
resolve to an entity owned by the referencing entity's own package —
cross-package references are rejected, not just tolerated with a warning.
There is deliberately no way yet to declare "package A depends on package
B" — that is future work (see DECISIONS.md D-019/D-020/D-021); until it
exists, any reference that crosses a package boundary is a defect.

Manifest currency (seventh-pass review finding H-20): a stable id existing
as SOME file in the package is not enough — it must be the package
manifest's CURRENT version of that id. Historical/superseded version files
are legitimately unmanifested by design (D-009); a link, assessment, or
revision that references one of them is referencing something the release
does not actually contain. Manifests are therefore parsed BEFORE ordinary
reference validation runs, and check_ref resolves against each package's
current-entity map, not merely against "does a file with this id exist
somewhere in the package."

REFERENCE_FIELDS / NESTED_REFERENCE_FIELDS below are the single declarative
source of truth for every schema-defined reference field (sixth-pass review
H-18) — they drive validate_references_in_file AT RUNTIME (seventh-pass
review M-19 closed the gap where NESTED_REFERENCE_FIELDS existed only for
tests/test_validation.py's completeness check but had no executable effect)
AND that same completeness check, so a new reference field added to a
schema without a matching registry entry fails a test instead of silently
validating nothing.
"""

from pathlib import Path
from typing import Tuple, List

from boe_files import Diagnostic, iter_entities, find_manifest, find_all_symlinks, find_traversal_errors, load_yaml

VALIDATOR = "references"

# entity_type -> [(field, is_list, want_type_or_None), ...]
# want_type is None for polymorphic references ("any" type) that are either
# unconstrained (revision.entity_id) or type-checked separately against a
# sibling discriminator field (relationship.from_id/to_id vs from_type/
# to_type; review.subject_id vs subject_type — see the special cases in
# validate_references_in_file).
REFERENCE_FIELDS: dict[str, list[tuple[str, bool, str | None]]] = {
    "claim_evidence_link": [
        ("claim_id", False, "claim"),
        ("evidence_id", False, "evidence"),
    ],
    "evidence": [
        ("source_id", False, "source"),
    ],
    "claim": [
        ("investigation_id", False, "investigation"),
    ],
    "assessment": [
        ("claim_id", False, "claim"),
        ("link_ids", True, "claim_evidence_link"),
    ],
    "finding": [
        ("investigation_id", False, "investigation"),
        ("claim_ids", True, "claim"),
    ],
    "timeline": [
        ("investigation_id", False, "investigation"),
        ("event_ids", True, "event"),
    ],
    "revision": [
        ("entity_id", False, None),
        ("triggered_by_review_id", False, "review"),
    ],
    "review": [
        ("subject_id", False, None),
        ("resolved_by_revision_id", False, "revision"),
        ("counter_evidence_ids", True, "evidence"),
    ],
    "relationship": [
        ("from_id", False, None),
        ("to_id", False, None),
        ("claim_id", False, "claim"),
        ("source_ids", True, "source"),
        ("investigation_ids", True, "investigation"),
    ],
    "person": [
        ("organisations", True, "organisation"),
        ("investigation_ids", True, "investigation"),
    ],
    "organisation": [
        ("parent_organisation_id", False, "organisation"),
        ("investigation_ids", True, "investigation"),
    ],
    "event": [
        ("claim_ids", True, "claim"),
        ("source_ids", True, "source"),
        ("person_ids", True, "person"),
        ("organisation_ids", True, "organisation"),
        ("investigation_ids", True, "investigation"),
    ],
    "source": [
        ("related_source_ids", True, "source"),
    ],
    "investigation": [
        ("related_investigations", True, "investigation"),
    ],
}

# Reference fields nested inside an array-of-objects property, not
# expressible as a flat (field, is_list, want_type) tuple: entity_type ->
# [(array_field, item_field, want_type_or_None), ...]. Unlike the fifth/
# sixth-pass version of this registry, these entries are executable —
# validate_references_in_file traverses them generically at runtime
# (seventh-pass review M-19); they are not merely descriptive metadata for
# the completeness test.
NESTED_REFERENCE_FIELDS: dict[str, list[tuple[str, str, str | None]]] = {
    "review": [("specific_concerns", "referenced_entity_id", None)],
}


def nested_field_schema_paths() -> dict[str, set[str]]:
    """NESTED_REFERENCE_FIELDS rendered as 'array[].item' path strings —
    the same shape tests/test_validation.py's schema-completeness scanner
    produces — so the two can be compared directly without the test module
    needing to know the executable tuple shape."""
    return {
        entity_type: {f"{array_field}[].{item_field}" for array_field, item_field, _ in entries}
        for entity_type, entries in NESTED_REFERENCE_FIELDS.items()
    }


def _err(code: str, path, message: str, location: str = "") -> Diagnostic:
    return Diagnostic(code, VALIDATOR, str(path), message, location)


def expected_type(ref_id: str) -> str:
    """Extract the type prefix from a boe ID."""
    parts = ref_id.split(":")
    return parts[1] if len(parts) == 3 else ""


def check_ref(ref_id, id_index: dict, path, field: str, errors: list,
              want_type: str | None = None, entity_package: Path | None = None,
              current_maps: dict[Path, dict] | None = None,
              referencing_is_current: bool = True):
    """
    Check one reference. `field` is the location (JSON-pointer-ish, e.g.
    'claim_id' or 'link_ids[2]') — carried on every diagnostic so tests and
    tools can distinguish which occurrence failed (fifth-pass review M-07b).

    `id_index[ref_id]` is a LIST of every entity file declaring that stable
    id — a stable id can legitimately appear in more than one file (D-009
    intra-package version history) and, before an explicit dependency
    mechanism exists, can also collide across packages. This prefers a
    same-package match when one exists, and only reports REF_WRONG_PACKAGE
    when NO same-package entry exists at all (sixth-pass review H-17).

    `current_maps[entity_package]` is that package's manifest current-entity
    map (id -> current version_id). A reference resolving to SOME file in
    the right package is not enough — it must be the package's CURRENT
    version of that id, or the reference points at something the release
    does not actually contain (seventh-pass review H-20).

    `referencing_is_current` (eighth-pass review H-21): the H-20 currency
    rule is about the CURRENT released graph — it must not be imposed on a
    reference made BY a historical/superseded entity version. Historical
    files are legitimately unmanifested by design (D-009), and a historical
    link describing what it referenced AT THAT TIME must remain valid even
    if the referenced entity has since been retired entirely. Only
    references originating from a version that is itself current are held
    to the "target must also be current" rule; historical referencing
    entities still get REF_NOT_FOUND / REF_TYPE_MISMATCH / REF_WRONG_PACKAGE
    checks — those are basic integrity facts, not release-graph membership.
    """
    if not ref_id:
        return
    ctx = f"{path}[{field}]"
    entries = id_index.get(ref_id)
    if not entries:
        errors.append(_err("REF_NOT_FOUND", path, f"{ctx}: Referenced ID '{ref_id}' not found", field))
        return
    if want_type and expected_type(ref_id) != want_type:
        errors.append(_err(
            "REF_TYPE_MISMATCH", path,
            f"{ctx}: Expected a {want_type} reference but got '{ref_id}'", field
        ))
    same_package = [e for e in entries if entity_package is not None and e["package"] == entity_package]
    if entity_package is not None and not same_package:
        other = entries[0]
        if other["package"] is not None:
            errors.append(_err(
                "REF_WRONG_PACKAGE", path,
                f"{ctx}: Referenced ID '{ref_id}' belongs to package "
                f"'{other['package']}', not this entity's own package "
                f"'{entity_package}' — cross-package references require an "
                f"explicit dependency declaration (not yet supported)",
                field,
            ))
        return  # Nothing meaningful to say about currency in the wrong package.

    if entity_package is not None and current_maps is not None and referencing_is_current:
        current_map = current_maps.get(entity_package, {})
        if ref_id not in current_map:
            errors.append(_err(
                "REF_NOT_CURRENT", path,
                f"{ctx}: Referenced ID '{ref_id}' exists in this package but "
                f"is not the CURRENT version per the package manifest — "
                f"historical/superseded versions are not part of the "
                f"released graph",
                field,
            ))


def check_ref_list(ref_ids, id_index, path, field: str, errors,
                    want_type=None, entity_package: Path | None = None,
                    current_maps: dict[Path, dict] | None = None,
                    referencing_is_current: bool = True):
    for idx, ref_id in enumerate(ref_ids or []):
        check_ref(
            ref_id, id_index, path, f"{field}[{idx}]", errors, want_type,
            entity_package, current_maps, referencing_is_current,
        )


def validate_references_in_file(
    yaml_file: Path, data: dict, id_index: dict, entity_package: Path | None,
    current_maps: dict[Path, dict] | None = None,
) -> list[Diagnostic]:
    errors = []
    t = data.get("type", "unknown")

    # H-21 (eighth-pass review): the manifest-currency rule (H-20) applies to
    # the CURRENT released graph. A file is only held to "my references must
    # also be current" if IT is current — i.e. the manifest's current_map
    # maps this file's own id to this file's own version_id. A historical/
    # superseded referencing file (current_map doesn't list its version_id,
    # possibly because it doesn't list the id at all) is exempt: its
    # references are still checked for existence/type/package, just not
    # manifest currency, so history stays valid after a referenced entity is
    # later retired entirely.
    referencing_is_current = True
    if entity_package is not None and current_maps is not None:
        current_map = current_maps.get(entity_package, {})
        referencing_is_current = current_map.get(data.get("id")) == data.get("version_id")

    def ref(field, ref_id, want_type=None):
        check_ref(
            ref_id, id_index, yaml_file, field, errors, want_type,
            entity_package, current_maps, referencing_is_current,
        )

    def ref_list(field, ref_ids, want_type=None):
        check_ref_list(
            ref_ids, id_index, yaml_file, field, errors, want_type,
            entity_package, current_maps, referencing_is_current,
        )

    for field, is_list, want_type in REFERENCE_FIELDS.get(t, []):
        (ref_list if is_list else ref)(field, data.get(field), want_type)

    # Nested (array-of-object) reference fields, driven generically by
    # NESTED_REFERENCE_FIELDS (seventh-pass review M-19 — this used to be a
    # hardcoded review.specific_concerns loop with no connection to the
    # registry a completeness test claimed was authoritative).
    for array_field, item_field, want_type in NESTED_REFERENCE_FIELDS.get(t, []):
        for idx, item in enumerate(data.get(array_field) or []):
            ref_id = item.get(item_field) if isinstance(item, dict) else None
            ref(f"{array_field}[{idx}].{item_field}", ref_id, want_type)

    # Polymorphic type-discriminator cases: these cross-check a SIBLING
    # field, not just resolve a reference, so they aren't expressible as a
    # registry entry.
    if t == "relationship":
        for end, type_field in (("from_id", "from_type"), ("to_id", "to_type")):
            ref_id = data.get(end)
            declared = data.get(type_field)
            if ref_id and declared and expected_type(ref_id) != declared:
                errors.append(_err(
                    "REF_DECLARED_TYPE_MISMATCH", yaml_file,
                    f"{yaml_file}[{end}]: ID '{ref_id}' is a {expected_type(ref_id)} "
                    f"but {type_field} declares '{declared}'",
                    end,
                ))

    if t == "review":
        subject_id, subject_type = data.get("subject_id"), data.get("subject_type")
        if subject_id and subject_type and expected_type(subject_id) != subject_type:
            errors.append(_err(
                "REF_DECLARED_TYPE_MISMATCH", yaml_file,
                f"{yaml_file}[subject_id]: ID '{subject_id}' is a "
                f"{expected_type(subject_id)} but subject_type declares "
                f"'{subject_type}'",
                "subject_id",
            ))

    return errors


def _path_is_contained(path_str: str) -> bool:
    """Lexical containment: relative, no '..' segments."""
    if not path_str:
        return False
    p = Path(path_str)
    if p.is_absolute():
        return False
    if ".." in p.parts:
        return False
    return True


def _resolved_containment_error(inv_path: Path, path_str: str) -> tuple[str, str] | None:
    """
    Two independent checks, both enforced (fourth-pass review M-11), for
    MANIFEST-LISTED paths specifically (unmanifested-file / non-YAML /
    directory symlinks are caught separately — see boe_files.find_all_symlinks
    and H-19/M-20 below):

    1. No path component between the package root and the entity file may
       itself be a symlink.
    2. Resolved containment: the target — after following any symlinks that
       do exist — must still live under the package root.

    The package ROOT itself being a symlink is handled separately, before
    file discovery even begins (fifth-pass review H-15) — by the time this
    function runs, `inv_path` is guaranteed not to be a symlink.

    Returns (code, message), or None if the path is clean.
    """
    root = inv_path.resolve()
    entity_file = inv_path / path_str

    walked = inv_path
    for part in Path(path_str).parts:
        walked = walked / part
        if walked.is_symlink():
            return (
                "MANIFEST_PATH_SYMLINK",
                f"Path '{path_str}' contains a symlink at '{walked.relative_to(inv_path)}' "
                f"— symlinks anywhere in a package path are prohibited (they can "
                f"escape the package after lexical checks pass)"
            )

    try:
        resolved = entity_file.resolve()
        if not resolved.is_relative_to(root):
            return (
                "MANIFEST_PATH_ESCAPES_ROOT",
                f"Path '{path_str}' resolves to '{resolved}', outside the "
                f"package root"
            )
    except OSError as e:
        return ("MANIFEST_PATH_UNRESOLVABLE", f"Path '{path_str}' could not be resolved: {e}")
    return None


def validate_manifest(inv_path: Path):
    """
    The manifest is the release authority — validate it hard:
    - it must exist (a package without a manifest has no defined current state)
    - listed paths are contained within the package, lexically AND resolved
      (symlinked entity paths are rejected)
    - listed files exist and their id/version_id match the entry
    - exactly one current entry per stable entity id
    - no duplicate version_ids or paths among entries
    - the manifest slug matches the package directory name
    - the manifest lists EXACTLY ONE Investigation entity, whose id matches
      the manifest's investigation_id (a package that omits its own
      Investigation has no defined subject)

    Returns (errors, current_map) where current_map maps entity id ->
    current version_id per this manifest. current_map is used by ordinary
    reference validation (H-20) AND revision transition validation.
    """
    manifest_path = find_manifest(inv_path)
    if manifest_path is None:
        return [_err(
            "MANIFEST_MISSING", inv_path,
            f"{inv_path}: Missing package.yaml manifest — a package without a "
            f"manifest has no defined current state (see D-012)"
        )], {}
    data, error = load_yaml(manifest_path)
    if error:
        return [_err("YAML_PARSE_ERROR", manifest_path, error)], {}
    if not data:
        return [_err("MANIFEST_EMPTY", manifest_path, f"{manifest_path}: Manifest is empty")], {}

    errors = []
    current_map = {}
    investigation_entries = []
    ctx = str(manifest_path)

    if data.get("slug") and data["slug"] != inv_path.name:
        errors.append(_err(
            "MANIFEST_SLUG_MISMATCH", manifest_path,
            f"{ctx}: Manifest slug '{data['slug']}' does not match package "
            f"directory name '{inv_path.name}'", "slug"
        ))

    seen_entry_ids = {}
    seen_entry_versions = {}
    seen_entry_paths = {}

    for entry in data.get("entities", []):
        eid, vid, path = entry.get("id"), entry.get("version_id"), entry.get("path")

        if eid:
            if eid in seen_entry_ids:
                errors.append(_err(
                    "MANIFEST_DUPLICATE_ENTITY_ID", manifest_path,
                    f"{ctx}: Entity id '{eid}' listed more than once — the "
                    f"manifest defines exactly one CURRENT version per entity",
                    eid,
                ))
            seen_entry_ids[eid] = entry
            if vid:
                current_map[eid] = vid
        if vid:
            if vid in seen_entry_versions:
                errors.append(_err(
                    "MANIFEST_DUPLICATE_VERSION_ID", manifest_path,
                    f"{ctx}: version_id '{vid}' listed more than once", vid
                ))
            seen_entry_versions[vid] = entry
        if path:
            if path in seen_entry_paths:
                errors.append(_err(
                    "MANIFEST_DUPLICATE_PATH", manifest_path, f"{ctx}: Path '{path}' listed more than once", path
                ))
            seen_entry_paths[path] = entry

            if not _path_is_contained(path):
                errors.append(_err(
                    "MANIFEST_PATH_NOT_CONTAINED", manifest_path,
                    f"{ctx}: Path '{path}' is not contained in the package "
                    f"(absolute paths and '..' are rejected)", path
                ))
                continue

            containment_error = _resolved_containment_error(inv_path, path)
            if containment_error:
                code, message = containment_error
                errors.append(_err(code, manifest_path, f"{ctx}: {message}", path))
                continue

            entity_file = inv_path / path
            if not entity_file.exists():
                errors.append(_err(
                    "MANIFEST_PATH_MISSING", manifest_path, f"{ctx}: Listed path '{path}' does not exist", path
                ))
                continue
            file_data, ferr = load_yaml(entity_file)
            if ferr or not file_data:
                continue  # Parse errors reported by schema validation
            if eid and file_data.get("id") != eid:
                errors.append(_err(
                    "MANIFEST_ENTRY_ID_MISMATCH", manifest_path,
                    f"{ctx}: Entry id '{eid}' does not match id "
                    f"'{file_data.get('id')}' in {path}", path
                ))
            if vid and file_data.get("version_id") != vid:
                errors.append(_err(
                    "MANIFEST_ENTRY_VERSION_MISMATCH", manifest_path,
                    f"{ctx}: Entry version_id '{vid}' does not match version_id "
                    f"'{file_data.get('version_id')}' in {path}", path
                ))
            if file_data.get("type") == "investigation":
                investigation_entries.append((entry, file_data))

    # Exactly one Investigation entity, matching the manifest's investigation_id.
    manifest_inv_id = data.get("investigation_id")
    if len(investigation_entries) == 0:
        errors.append(_err(
            "MANIFEST_NO_INVESTIGATION", manifest_path,
            f"{ctx}: Manifest lists no Investigation entity — a package that "
            f"omits its own Investigation has no defined subject"
        ))
    elif len(investigation_entries) > 1:
        errors.append(_err(
            "MANIFEST_MULTIPLE_INVESTIGATIONS", manifest_path,
            f"{ctx}: Manifest lists {len(investigation_entries)} Investigation "
            f"entities — exactly one is required"
        ))
    elif manifest_inv_id:
        _, inv_data = investigation_entries[0]
        if inv_data.get("id") != manifest_inv_id:
            errors.append(_err(
                "MANIFEST_INVESTIGATION_ID_MISMATCH", manifest_path,
                f"{ctx}: investigation_id '{manifest_inv_id}' does not match "
                f"the Investigation entity '{inv_data.get('id')}' listed in "
                f"the manifest", "investigation_id"
            ))

    return errors, current_map


def validate_revision_transition(
    yaml_file: Path, data: dict, version_index: dict, current_map: dict, inv_path: Path
) -> list[Diagnostic]:
    """
    A Revision connects two versions OF THE SAME ENTITY, OWNED BY THE SAME
    PACKAGE. version_ids are globally unique by invariant #8, so — unlike
    id_index — version_index does not need multimap treatment.

    Checks:
    - old/new version_ids correspond to existing version files
    - old != new
    - both endpoint files carry the Revision's entity_id
    - both endpoint files carry the Revision's entity_type
    - both endpoint files are owned by the package containing this Revision
    - the OLD version is not listed as current in the package manifest
    Note: the NEW version is deliberately not required to be current —
    revision chains (v1→v2, v2→v3) keep intermediate revisions valid. This
    is why revision endpoints are checked against version_index directly
    rather than through check_ref's H-20 currency rule, which is specific
    to stable-id references like entity_id (checked separately, in
    validate_references_in_file, and which DOES require the entity concept
    itself to currently exist).
    """
    errors = []
    ctx = str(yaml_file)
    entity_id = data.get("entity_id")
    entity_type = data.get("entity_type")

    for field in ("old_version_id", "new_version_id"):
        vid = data.get(field)
        if not vid:
            continue
        info = version_index.get(vid)
        if info is None:
            errors.append(_err(
                "REVISION_ENDPOINT_NOT_FOUND", yaml_file,
                f"{ctx}[{field}]: version_id '{vid}' does not correspond to "
                f"any entity version file", field
            ))
            continue
        if entity_id and info["id"] != entity_id:
            errors.append(_err(
                "REVISION_ENTITY_MISMATCH", yaml_file,
                f"{ctx}[{field}]: version '{vid}' belongs to entity "
                f"'{info['id']}', not the revised entity '{entity_id}' — a "
                f"revision must connect two versions of the same entity", field
            ))
        if entity_type and info["type"] != entity_type:
            errors.append(_err(
                "REVISION_TYPE_MISMATCH", yaml_file,
                f"{ctx}[{field}]: version '{vid}' is a '{info['type']}', but "
                f"the revision declares entity_type '{entity_type}'", field
            ))
        if info["package"] is not None and info["package"] != inv_path:
            errors.append(_err(
                "REVISION_ENDPOINT_WRONG_PACKAGE", yaml_file,
                f"{ctx}[{field}]: version '{vid}' belongs to package "
                f"'{info['package']}', not this revision's package "
                f"'{inv_path}' — a revision may only connect versions owned "
                f"by its own package", field
            ))

    old, new = data.get("old_version_id"), data.get("new_version_id")
    if old and new and old == new:
        errors.append(_err(
            "REVISION_SAME_ENDPOINTS", yaml_file, f"{ctx}: old_version_id and new_version_id are identical"
        ))

    if entity_id and old and current_map.get(entity_id) == old:
        errors.append(_err(
            "REVISION_OLD_STILL_CURRENT", yaml_file,
            f"{ctx}: old_version_id '{old}' is still listed as CURRENT for "
            f"'{entity_id}' in the manifest — a superseded version cannot be "
            f"the current version", "old_version_id"
        ))

    return errors


def _owning_package(path: Path, investigation_paths: list[Path]) -> Path | None:
    """Which of the passed-in package roots contains this file, if any."""
    for inv_path in investigation_paths:
        try:
            path.relative_to(inv_path)
            return inv_path
        except ValueError:
            continue
    return None


def run_reference_validation(
    investigation_paths: list[Path],
    schema_dir: Path,
    verbose: bool = False,
) -> Tuple[bool, List[Diagnostic]]:
    all_errors = []

    # A symlinked package root is rejected outright, before any file
    # discovery (fifth-pass review H-15).
    real_investigation_paths = []
    for inv_path in investigation_paths:
        if inv_path.is_symlink():
            all_errors.append(_err(
                "INVESTIGATION_ROOT_SYMLINK", inv_path,
                f"{inv_path}: package root is a symlink — symlinked package "
                f"roots are prohibited (they can point anywhere on disk, "
                f"bypassing every per-path containment check)"
            ))
            continue
        real_investigation_paths.append(inv_path)

    # ANY symlink anywhere inside a package is rejected outright — a file,
    # a directory, any extension, manifested or not (sixth-pass H-19,
    # broadened by seventh-pass M-20: the narrower YAML-only scan missed
    # symlinked subdirectories and non-YAML symlinks). boe_files already
    # refuses to read through these; this reports the precise cause instead
    # of the package silently appearing to have fewer entries than it does.
    for symlinked in find_all_symlinks(real_investigation_paths):
        all_errors.append(_err(
            "PACKAGE_SYMLINK", symlinked,
            f"{symlinked}: symlink found inside a package — symlinks are "
            f"prohibited anywhere in a package, including unmanifested "
            f"historical versions, subdirectories, and non-YAML files "
            f"(they can indirect to content outside the package, or crash "
            f"validation if broken)"
        ))

    # A subtree os.walk could not list (e.g. permission denied) is fail-
    # closed, not silently skipped (eighth-pass review M-22): a package
    # cannot be certified when part of it was never actually inspected —
    # an unreadable directory could just as easily be hiding a prohibited
    # symlink or a policy-violating entity file.
    for inv_path, exc in find_traversal_errors(real_investigation_paths):
        failed_dir = getattr(exc, "filename", None) or inv_path
        all_errors.append(_err(
            "PACKAGE_SUBTREE_UNREADABLE", failed_dir,
            f"{failed_dir}: could not list directory contents ({exc}) — a "
            f"package cannot be certified when part of it was not "
            f"inspectable"
        ))

    # Pass 1: index all defined IDs and versions. id_index is a MULTIMAP —
    # a stable id can legitimately appear in more than one file (D-009
    # intra-package version history), so collapsing it to one entry loses
    # information a reference check needs (sixth-pass review H-17).
    id_index: dict[str, list[dict]] = {}
    version_index = {}
    entities = list(iter_entities(real_investigation_paths))
    for path, data in entities:
        package = _owning_package(path, real_investigation_paths)
        if "id" in data:
            id_index.setdefault(data["id"], []).append({"path": path, "package": package})
        if "version_id" in data:
            version_index[data["version_id"]] = {
                "path": path,
                "id": data.get("id"),
                "type": data.get("type"),
                "package": package,
            }

    if verbose:
        print(f"    Indexed {len(id_index)} entity IDs, {len(version_index)} versions")

    # Pass 2: manifests are parsed BEFORE ordinary reference validation
    # (seventh-pass review H-20) — a reference must resolve against each
    # package's CURRENT membership, not merely against "a file with this
    # id exists somewhere in the package", so current_maps must exist
    # before Pass 3 runs.
    current_maps: dict[Path, dict] = {}
    for inv_path in real_investigation_paths:
        manifest_errors, current_map = validate_manifest(inv_path)
        current_maps[inv_path] = current_map
        all_errors.extend(manifest_errors)

    # Pass 3: cross-entity references, package-scoped (H-02c) and
    # manifest-current-scoped (H-20) by default, covering every
    # schema-declared reference field (H-18/M-19).
    for path, data in entities:
        entity_package = _owning_package(path, real_investigation_paths)
        all_errors.extend(validate_references_in_file(path, data, id_index, entity_package, current_maps))

    # Pass 4: revision transitions against each package's current map.
    for inv_path in real_investigation_paths:
        current_map = current_maps[inv_path]
        for path, data in entities:
            if data.get("type") != "revision":
                continue
            try:
                path.relative_to(inv_path)
            except ValueError:
                continue  # revision belongs to a different package
            all_errors.extend(
                validate_revision_transition(path, data, version_index, current_map, inv_path)
            )

    return len(all_errors) == 0, all_errors


if __name__ == "__main__":
    import sys
    repo_root = Path(__file__).parent.parent
    inv_paths = [
        p for p in (repo_root / "investigations").iterdir()
        if p.is_dir() and not p.name.startswith("_")
    ]
    passed, errors = run_reference_validation(inv_paths, repo_root / "schema", verbose=True)
    for e in errors:
        print(f"ERROR: {e}")
    sys.exit(0 if passed else 1)
