#!/usr/bin/env python3
"""
Body of Evidence — Reference Validation

Checks that every ID referenced in any entity resolves to an existing entity
of the EXPECTED TYPE and the SAME PACKAGE, and that package manifests are
consistent with the entity files they list.

Package scoping (fifth-pass review finding H-02c): investigation packages
are meant to be self-contained. By default, EVERY reference below must
resolve to an entity owned by the referencing entity's own package —
cross-package references are rejected, not just tolerated with a warning.
There is deliberately no way yet to declare "package A depends on package
B" — that is future work (see DECISIONS.md D-019); until it exists, any
reference that crosses a package boundary is a defect, whether accidental
(a copy-pasted id) or adversarial (a package claiming another package's
entities as its own).

Reference map (single-direction — backlinks are derived, never stored):
- claim_evidence_link.claim_id      → claim
- claim_evidence_link.evidence_id   → evidence
- evidence.source_id                → source
- claim.investigation_id            → investigation
- assessment.claim_id               → claim
- assessment.link_ids[]             → claim_evidence_link
- finding.claim_ids[]               → claim
- finding.investigation_id          → investigation
- timeline.event_ids[]              → event
- timeline.investigation_id         → investigation
- revision.entity_id                → any
- review.subject_id                 → any
- relationship.from_id / to_id      → any (type checked against from_type/to_type)
- relationship.claim_id             → claim
- person.organisations[]            → organisation
- event.{claim,source,person,organisation}_ids[] → respective types
- package manifest entities[]       → path exists, id and version_id match the file
"""

from pathlib import Path
from typing import Tuple, List

from boe_files import Diagnostic, iter_entities, find_manifest, load_yaml

VALIDATOR = "references"


def _err(code: str, path, message: str, location: str = "") -> Diagnostic:
    return Diagnostic(code, VALIDATOR, str(path), message, location)


def expected_type(ref_id: str) -> str:
    """Extract the type prefix from a boe ID."""
    parts = ref_id.split(":")
    return parts[1] if len(parts) == 3 else ""


def check_ref(ref_id, id_index: dict, path, field: str, errors: list,
              want_type: str | None = None, entity_package: Path | None = None):
    """
    Check one reference. `field` is the location (JSON-pointer-ish, e.g.
    'claim_id' or 'link_ids[2]') — carried on every diagnostic so tests and
    tools can distinguish which occurrence failed, not just that some
    reference in this file failed (fifth-pass review M-07b).

    Package scoping (H-02c): if the referencing entity's package
    (`entity_package`) and the target's package are both known and differ,
    that is a defect regardless of whether the target exists and has the
    right type — self-contained packages are the model, and there is no
    dependency-declaration mechanism yet to make a cross-package reference
    intentional.
    """
    if not ref_id:
        return
    ctx = f"{path}[{field}]"
    entry = id_index.get(ref_id)
    if entry is None:
        errors.append(_err("REF_NOT_FOUND", path, f"{ctx}: Referenced ID '{ref_id}' not found", field))
        return
    if want_type and expected_type(ref_id) != want_type:
        errors.append(_err(
            "REF_TYPE_MISMATCH", path,
            f"{ctx}: Expected a {want_type} reference but got '{ref_id}'", field
        ))
    target_package = entry["package"]
    if entity_package is not None and target_package is not None and target_package != entity_package:
        errors.append(_err(
            "REF_WRONG_PACKAGE", path,
            f"{ctx}: Referenced ID '{ref_id}' belongs to package "
            f"'{target_package}', not this entity's own package "
            f"'{entity_package}' — cross-package references require an "
            f"explicit dependency declaration (not yet supported)",
            field,
        ))


def check_ref_list(ref_ids, id_index, path, field: str, errors,
                    want_type=None, entity_package: Path | None = None):
    for idx, ref_id in enumerate(ref_ids or []):
        check_ref(ref_id, id_index, path, f"{field}[{idx}]", errors, want_type, entity_package)


def validate_references_in_file(
    yaml_file: Path, data: dict, id_index: dict, entity_package: Path | None
) -> list[Diagnostic]:
    errors = []
    t = data.get("type", "unknown")

    def ref(field, ref_id, want_type=None):
        check_ref(ref_id, id_index, yaml_file, field, errors, want_type, entity_package)

    def ref_list(field, ref_ids, want_type=None):
        check_ref_list(ref_ids, id_index, yaml_file, field, errors, want_type, entity_package)

    if t == "claim_evidence_link":
        ref("claim_id", data.get("claim_id"), "claim")
        ref("evidence_id", data.get("evidence_id"), "evidence")

    elif t == "evidence":
        ref("source_id", data.get("source_id"), "source")

    elif t == "claim":
        ref("investigation_id", data.get("investigation_id"), "investigation")

    elif t == "assessment":
        ref("claim_id", data.get("claim_id"), "claim")
        ref_list("link_ids", data.get("link_ids"), "claim_evidence_link")

    elif t == "finding":
        ref("investigation_id", data.get("investigation_id"), "investigation")
        ref_list("claim_ids", data.get("claim_ids"), "claim")

    elif t == "timeline":
        ref("investigation_id", data.get("investigation_id"), "investigation")
        ref_list("event_ids", data.get("event_ids"), "event")

    elif t == "revision":
        ref("entity_id", data.get("entity_id"))
        ref("triggered_by_review_id", data.get("triggered_by_review_id"), "review")

    elif t == "review":
        ref("subject_id", data.get("subject_id"))
        ref("resolved_by_revision_id", data.get("resolved_by_revision_id"), "revision")
        ref_list("counter_evidence_ids", data.get("counter_evidence_ids"), "evidence")

    elif t == "relationship":
        for end, type_field in (("from_id", "from_type"), ("to_id", "to_type")):
            ref_id = data.get(end)
            ref(end, ref_id)
            declared = data.get(type_field)
            if ref_id and declared and expected_type(ref_id) != declared:
                errors.append(_err(
                    "REF_DECLARED_TYPE_MISMATCH", yaml_file,
                    f"{yaml_file}[{end}]: ID '{ref_id}' is a {expected_type(ref_id)} "
                    f"but {type_field} declares '{declared}'",
                    end,
                ))
        ref("claim_id", data.get("claim_id"), "claim")
        ref_list("source_ids", data.get("source_ids"), "source")

    elif t == "person":
        ref_list("organisations", data.get("organisations"), "organisation")

    elif t == "organisation":
        ref("parent_organisation_id", data.get("parent_organisation_id"), "organisation")

    elif t == "event":
        ref_list("claim_ids", data.get("claim_ids"), "claim")
        ref_list("source_ids", data.get("source_ids"), "source")
        ref_list("person_ids", data.get("person_ids"), "person")
        ref_list("organisation_ids", data.get("organisation_ids"), "organisation")

    elif t == "source":
        ref_list("related_source_ids", data.get("related_source_ids"), "source")

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
    Two independent checks, both enforced (fourth-pass review M-11):

    1. No path component between the package root and the entity file may
       itself be a symlink — not just the entity file, but every parent
       directory in between.
    2. Resolved containment: the target — after following any symlinks that
       do exist — must still live under the package root.

    The package ROOT itself being a symlink is handled separately, before
    file discovery even begins (fifth-pass review H-15) — by the time this
    function runs, `inv_path` is guaranteed not to be a symlink.

    Returns (code, message), or None if the path is clean.
    """
    root = inv_path.resolve()
    entity_file = inv_path / path_str

    # Rule 1: no symlink anywhere from the package root down to the file.
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

    # Rule 2: even without a tracked symlink, the resolved target must stay
    # under the package root.
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


def validate_manifest(inv_path: Path, id_index: dict, version_index: dict):
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
    current version_id per this manifest. current_map is used by revision
    transition validation.
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
    PACKAGE. Endpoint existence alone is not enough — a revision whose
    endpoints belong to unrelated entities is syntactically valid and
    semantically meaningless (third-pass finding); a revision whose
    endpoints belong to a DIFFERENT package is likewise meaningless
    (fourth-pass finding H-02b).

    Each endpoint is checked independently and its diagnostics carry
    `location=field` (old_version_id / new_version_id) so a caller can
    tell "one endpoint is wrong" from "both endpoints are wrong" — the
    fifth-pass review demonstrated that a (validator, code) set alone
    collapses those two very different situations into one entry
    (finding M-07b).

    Checks:
    - old/new version_ids correspond to existing version files
    - old != new
    - both endpoint files carry the Revision's entity_id
    - both endpoint files carry the Revision's entity_type
    - both endpoint files are owned by the package containing this Revision
    - the OLD version is not listed as current in the package manifest
      (a "superseded" version that is still current is a contradiction)
    Note: the NEW version is deliberately not required to be current —
    revision chains (v1→v2, v2→v3) keep intermediate revisions valid.
    """
    errors = []
    ctx = str(yaml_file)
    entity_id = data.get("entity_id")
    entity_type = data.get("entity_type")

    endpoints = {}
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
        endpoints[field] = info
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
    # discovery — the resolved root would traverse to arbitrary content
    # outside the checkout entirely (fifth-pass review H-15). boe_files
    # already refuses to descend into such a root for every validator;
    # this is what actually reports the defect.
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

    # Pass 1: index all defined IDs and versions. Both indexes carry
    # package identity — a lossy version_id -> path map cannot support
    # revision transition validation (third-pass review finding), and
    # without package identity a reference or transition can silently
    # cross package boundaries (fourth-pass H-02b, fifth-pass H-02c).
    id_index = {}
    version_index = {}
    entities = list(iter_entities(real_investigation_paths))
    for path, data in entities:
        package = _owning_package(path, real_investigation_paths)
        if "id" in data:
            id_index[data["id"]] = {"path": path, "package": package}
        if "version_id" in data:
            version_index[data["version_id"]] = {
                "path": path,
                "id": data.get("id"),
                "type": data.get("type"),
                "package": package,
            }

    if verbose:
        print(f"    Indexed {len(id_index)} entity IDs, {len(version_index)} versions")

    # Pass 2: cross-entity references, package-scoped by default (H-02c)
    for path, data in entities:
        entity_package = _owning_package(path, real_investigation_paths)
        all_errors.extend(validate_references_in_file(path, data, id_index, entity_package))

    # Pass 3: per-package — manifests (mandatory, the release authority),
    # then revision transitions against that package's current map
    for inv_path in real_investigation_paths:
        manifest_errors, current_map = validate_manifest(
            inv_path, id_index, version_index
        )
        all_errors.extend(manifest_errors)
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
