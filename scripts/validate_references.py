#!/usr/bin/env python3
"""
Body of Evidence — Reference Validation

Checks that every ID referenced in any entity resolves to an existing entity
of the EXPECTED TYPE, and that package manifests are consistent with the
entity files they list.

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


def _err(code: str, path, message: str) -> Diagnostic:
    return Diagnostic(code, VALIDATOR, str(path), message)


def expected_type(ref_id: str) -> str:
    """Extract the type prefix from a boe ID."""
    parts = ref_id.split(":")
    return parts[1] if len(parts) == 3 else ""


def check_ref(ref_id, id_index: dict, context: str, path, errors: list,
              want_type: str | None = None):
    if not ref_id:
        return
    if ref_id not in id_index:
        errors.append(_err("REF_NOT_FOUND", path, f"{context}: Referenced ID '{ref_id}' not found"))
        return
    if want_type and expected_type(ref_id) != want_type:
        errors.append(_err(
            "REF_TYPE_MISMATCH", path,
            f"{context}: Expected a {want_type} reference but got '{ref_id}'"
        ))


def check_ref_list(ref_ids, id_index, context, path, errors, want_type=None):
    for ref_id in ref_ids or []:
        check_ref(ref_id, id_index, context, path, errors, want_type)


def validate_references_in_file(yaml_file: Path, data: dict, id_index: dict) -> list[Diagnostic]:
    errors = []
    t = data.get("type", "unknown")
    ctx = str(yaml_file)

    if t == "claim_evidence_link":
        check_ref(data.get("claim_id"), id_index, f"{ctx}[claim_id]", yaml_file, errors, "claim")
        check_ref(data.get("evidence_id"), id_index, f"{ctx}[evidence_id]", yaml_file, errors, "evidence")

    elif t == "evidence":
        check_ref(data.get("source_id"), id_index, f"{ctx}[source_id]", yaml_file, errors, "source")

    elif t == "claim":
        check_ref(data.get("investigation_id"), id_index, f"{ctx}[investigation_id]", yaml_file, errors, "investigation")

    elif t == "assessment":
        check_ref(data.get("claim_id"), id_index, f"{ctx}[claim_id]", yaml_file, errors, "claim")
        check_ref_list(data.get("link_ids"), id_index, f"{ctx}[link_ids]", yaml_file, errors, "claim_evidence_link")

    elif t == "finding":
        check_ref(data.get("investigation_id"), id_index, f"{ctx}[investigation_id]", yaml_file, errors, "investigation")
        check_ref_list(data.get("claim_ids"), id_index, f"{ctx}[claim_ids]", yaml_file, errors, "claim")

    elif t == "timeline":
        check_ref(data.get("investigation_id"), id_index, f"{ctx}[investigation_id]", yaml_file, errors, "investigation")
        check_ref_list(data.get("event_ids"), id_index, f"{ctx}[event_ids]", yaml_file, errors, "event")

    elif t == "revision":
        check_ref(data.get("entity_id"), id_index, f"{ctx}[entity_id]", yaml_file, errors)
        check_ref(data.get("triggered_by_review_id"), id_index, f"{ctx}[triggered_by_review_id]", yaml_file, errors, "review")

    elif t == "review":
        check_ref(data.get("subject_id"), id_index, f"{ctx}[subject_id]", yaml_file, errors)
        check_ref(data.get("resolved_by_revision_id"), id_index, f"{ctx}[resolved_by_revision_id]", yaml_file, errors, "revision")
        check_ref_list(data.get("counter_evidence_ids"), id_index, f"{ctx}[counter_evidence_ids]", yaml_file, errors, "evidence")

    elif t == "relationship":
        for end, type_field in (("from_id", "from_type"), ("to_id", "to_type")):
            ref = data.get(end)
            check_ref(ref, id_index, f"{ctx}[{end}]", yaml_file, errors)
            declared = data.get(type_field)
            if ref and declared and expected_type(ref) != declared:
                errors.append(_err(
                    "REF_DECLARED_TYPE_MISMATCH", yaml_file,
                    f"{ctx}[{end}]: ID '{ref}' is a {expected_type(ref)} "
                    f"but {type_field} declares '{declared}'"
                ))
        check_ref(data.get("claim_id"), id_index, f"{ctx}[claim_id]", yaml_file, errors, "claim")
        check_ref_list(data.get("source_ids"), id_index, f"{ctx}[source_ids]", yaml_file, errors, "source")

    elif t == "person":
        check_ref_list(data.get("organisations"), id_index, f"{ctx}[organisations]", yaml_file, errors, "organisation")

    elif t == "organisation":
        check_ref(data.get("parent_organisation_id"), id_index, f"{ctx}[parent_organisation_id]", yaml_file, errors, "organisation")

    elif t == "event":
        check_ref_list(data.get("claim_ids"), id_index, f"{ctx}[claim_ids]", yaml_file, errors, "claim")
        check_ref_list(data.get("source_ids"), id_index, f"{ctx}[source_ids]", yaml_file, errors, "source")
        check_ref_list(data.get("person_ids"), id_index, f"{ctx}[person_ids]", yaml_file, errors, "person")
        check_ref_list(data.get("organisation_ids"), id_index, f"{ctx}[organisation_ids]", yaml_file, errors, "organisation")

    elif t == "source":
        check_ref_list(data.get("related_source_ids"), id_index, f"{ctx}[related_source_ids]", yaml_file, errors, "source")

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
    Two independent checks, both enforced (fourth-pass review M-11 — the
    documented "no symlinks" policy was stricter than the implementation,
    which only rejected the final component):

    1. No path component between the package root and the entity file may
       itself be a symlink — not just the entity file, but every parent
       directory in between. This is the simpler, auditable rule the review
       recommended: a reproducible package contains no symlinks at all.
    2. Resolved containment: the target — after following any symlinks that
       do exist — must still live under the package root. This is a
       defence-in-depth backstop, not a substitute for rule 1.

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
    # under the package root (catches symlinked ancestor directories that
    # exist outside the checkout, e.g. a symlinked package root itself).
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
            f"directory name '{inv_path.name}'"
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
                    f"manifest defines exactly one CURRENT version per entity"
                ))
            seen_entry_ids[eid] = entry
            if vid:
                current_map[eid] = vid
        if vid:
            if vid in seen_entry_versions:
                errors.append(_err(
                    "MANIFEST_DUPLICATE_VERSION_ID", manifest_path,
                    f"{ctx}: version_id '{vid}' listed more than once"
                ))
            seen_entry_versions[vid] = entry
        if path:
            if path in seen_entry_paths:
                errors.append(_err(
                    "MANIFEST_DUPLICATE_PATH", manifest_path, f"{ctx}: Path '{path}' listed more than once"
                ))
            seen_entry_paths[path] = entry

            if not _path_is_contained(path):
                errors.append(_err(
                    "MANIFEST_PATH_NOT_CONTAINED", manifest_path,
                    f"{ctx}: Path '{path}' is not contained in the package "
                    f"(absolute paths and '..' are rejected)"
                ))
                continue

            containment_error = _resolved_containment_error(inv_path, path)
            if containment_error:
                code, message = containment_error
                errors.append(_err(code, manifest_path, f"{ctx}: {message}"))
                continue

            entity_file = inv_path / path
            if not entity_file.exists():
                errors.append(_err(
                    "MANIFEST_PATH_MISSING", manifest_path, f"{ctx}: Listed path '{path}' does not exist"
                ))
                continue
            file_data, ferr = load_yaml(entity_file)
            if ferr or not file_data:
                continue  # Parse errors reported by schema validation
            if eid and file_data.get("id") != eid:
                errors.append(_err(
                    "MANIFEST_ENTRY_ID_MISMATCH", manifest_path,
                    f"{ctx}: Entry id '{eid}' does not match id "
                    f"'{file_data.get('id')}' in {path}"
                ))
            if vid and file_data.get("version_id") != vid:
                errors.append(_err(
                    "MANIFEST_ENTRY_VERSION_MISMATCH", manifest_path,
                    f"{ctx}: Entry version_id '{vid}' does not match version_id "
                    f"'{file_data.get('version_id')}' in {path}"
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
                f"the manifest"
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
    endpoints belong to a DIFFERENT package is likewise meaningless — it
    lets one investigation claim a transition it does not own (fourth-pass
    finding H-02b).

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
                f"any entity version file"
            ))
            continue
        endpoints[field] = info
        if entity_id and info["id"] != entity_id:
            errors.append(_err(
                "REVISION_ENTITY_MISMATCH", yaml_file,
                f"{ctx}[{field}]: version '{vid}' belongs to entity "
                f"'{info['id']}', not the revised entity '{entity_id}' — a "
                f"revision must connect two versions of the same entity"
            ))
        if entity_type and info["type"] != entity_type:
            errors.append(_err(
                "REVISION_TYPE_MISMATCH", yaml_file,
                f"{ctx}[{field}]: version '{vid}' is a '{info['type']}', but "
                f"the revision declares entity_type '{entity_type}'"
            ))
        if info["package"] is not None and info["package"] != inv_path:
            errors.append(_err(
                "REVISION_ENDPOINT_WRONG_PACKAGE", yaml_file,
                f"{ctx}[{field}]: version '{vid}' belongs to package "
                f"'{info['package']}', not this revision's package "
                f"'{inv_path}' — a revision may only connect versions owned "
                f"by its own package"
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
            f"the current version"
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
    # Pass 1: index all defined IDs and versions. The version index is
    # deliberately rich — a lossy version_id -> path map cannot support
    # revision transition validation (third-pass review finding), and it
    # must carry package identity so transitions cannot cross package
    # boundaries unnoticed (fourth-pass review finding H-02b).
    id_index = {}
    version_index = {}
    entities = list(iter_entities(investigation_paths))
    for path, data in entities:
        if "id" in data:
            id_index[data["id"]] = path
        if "version_id" in data:
            version_index[data["version_id"]] = {
                "path": path,
                "id": data.get("id"),
                "type": data.get("type"),
                "package": _owning_package(path, investigation_paths),
            }

    if verbose:
        print(f"    Indexed {len(id_index)} entity IDs, {len(version_index)} versions")

    # Pass 2: cross-entity references
    all_errors = []
    for path, data in entities:
        all_errors.extend(validate_references_in_file(path, data, id_index))

    # Pass 3: per-package — manifests (mandatory, the release authority),
    # then revision transitions against that package's current map
    for inv_path in investigation_paths:
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
