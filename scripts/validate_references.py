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

from boe_files import iter_entities, find_manifest, load_yaml


def expected_type(ref_id: str) -> str:
    """Extract the type prefix from a boe ID."""
    parts = ref_id.split(":")
    return parts[1] if len(parts) == 3 else ""


def check_ref(ref_id, id_index: dict, context: str, errors: list,
              want_type: str | None = None):
    if not ref_id:
        return
    if ref_id not in id_index:
        errors.append(f"{context}: Referenced ID '{ref_id}' not found")
        return
    if want_type and expected_type(ref_id) != want_type:
        errors.append(
            f"{context}: Expected a {want_type} reference but got '{ref_id}'"
        )


def check_ref_list(ref_ids, id_index, context, errors, want_type=None):
    for ref_id in ref_ids or []:
        check_ref(ref_id, id_index, context, errors, want_type)


def validate_references_in_file(yaml_file: Path, data: dict, id_index: dict) -> list[str]:
    errors = []
    t = data.get("type", "unknown")
    ctx = str(yaml_file)

    if t == "claim_evidence_link":
        check_ref(data.get("claim_id"), id_index, f"{ctx}[claim_id]", errors, "claim")
        check_ref(data.get("evidence_id"), id_index, f"{ctx}[evidence_id]", errors, "evidence")

    elif t == "evidence":
        check_ref(data.get("source_id"), id_index, f"{ctx}[source_id]", errors, "source")

    elif t == "claim":
        check_ref(data.get("investigation_id"), id_index, f"{ctx}[investigation_id]", errors, "investigation")

    elif t == "assessment":
        check_ref(data.get("claim_id"), id_index, f"{ctx}[claim_id]", errors, "claim")
        check_ref_list(data.get("link_ids"), id_index, f"{ctx}[link_ids]", errors, "claim_evidence_link")

    elif t == "finding":
        check_ref(data.get("investigation_id"), id_index, f"{ctx}[investigation_id]", errors, "investigation")
        check_ref_list(data.get("claim_ids"), id_index, f"{ctx}[claim_ids]", errors, "claim")

    elif t == "timeline":
        check_ref(data.get("investigation_id"), id_index, f"{ctx}[investigation_id]", errors, "investigation")
        check_ref_list(data.get("event_ids"), id_index, f"{ctx}[event_ids]", errors, "event")

    elif t == "revision":
        check_ref(data.get("entity_id"), id_index, f"{ctx}[entity_id]", errors)
        check_ref(data.get("triggered_by_review_id"), id_index, f"{ctx}[triggered_by_review_id]", errors, "review")

    elif t == "review":
        check_ref(data.get("subject_id"), id_index, f"{ctx}[subject_id]", errors)
        check_ref(data.get("resolved_by_revision_id"), id_index, f"{ctx}[resolved_by_revision_id]", errors, "revision")
        check_ref_list(data.get("counter_evidence_ids"), id_index, f"{ctx}[counter_evidence_ids]", errors, "evidence")

    elif t == "relationship":
        for end, type_field in (("from_id", "from_type"), ("to_id", "to_type")):
            ref = data.get(end)
            check_ref(ref, id_index, f"{ctx}[{end}]", errors)
            declared = data.get(type_field)
            if ref and declared and expected_type(ref) != declared:
                errors.append(
                    f"{ctx}[{end}]: ID '{ref}' is a {expected_type(ref)} "
                    f"but {type_field} declares '{declared}'"
                )
        check_ref(data.get("claim_id"), id_index, f"{ctx}[claim_id]", errors, "claim")
        check_ref_list(data.get("source_ids"), id_index, f"{ctx}[source_ids]", errors, "source")

    elif t == "person":
        check_ref_list(data.get("organisations"), id_index, f"{ctx}[organisations]", errors, "organisation")

    elif t == "organisation":
        check_ref(data.get("parent_organisation_id"), id_index, f"{ctx}[parent_organisation_id]", errors, "organisation")

    elif t == "event":
        check_ref_list(data.get("claim_ids"), id_index, f"{ctx}[claim_ids]", errors, "claim")
        check_ref_list(data.get("source_ids"), id_index, f"{ctx}[source_ids]", errors, "source")
        check_ref_list(data.get("person_ids"), id_index, f"{ctx}[person_ids]", errors, "person")
        check_ref_list(data.get("organisation_ids"), id_index, f"{ctx}[organisation_ids]", errors, "organisation")

    elif t == "source":
        check_ref_list(data.get("related_source_ids"), id_index, f"{ctx}[related_source_ids]", errors, "source")

    return errors


def _path_is_contained(path_str: str) -> bool:
    """A manifest path must be relative and stay inside the package."""
    if not path_str:
        return False
    p = Path(path_str)
    if p.is_absolute():
        return False
    if ".." in p.parts:
        return False
    return True


def validate_manifest(inv_path: Path, id_index: dict, version_index: dict) -> list[str]:
    """
    The manifest is the release authority — validate it hard:
    - it must exist (a package without a manifest has no defined current state)
    - listed paths are contained within the package (no absolute, no '..')
    - listed files exist and their id/version_id match the entry
    - exactly one current entry per stable entity id
    - no duplicate version_ids or paths among entries
    - the manifest slug matches the package directory name
    - the manifest investigation_id matches the Investigation entity it lists
    """
    manifest_path = find_manifest(inv_path)
    if manifest_path is None:
        return [
            f"{inv_path}: Missing package.yaml manifest — a package without a "
            f"manifest has no defined current state (see D-012)"
        ]
    data, error = load_yaml(manifest_path)
    if error:
        return [error]
    if not data:
        return [f"{manifest_path}: Manifest is empty"]

    errors = []
    ctx = str(manifest_path)

    if data.get("slug") and data["slug"] != inv_path.name:
        errors.append(
            f"{ctx}: Manifest slug '{data['slug']}' does not match package "
            f"directory name '{inv_path.name}'"
        )

    seen_entry_ids = {}
    seen_entry_versions = {}
    seen_entry_paths = {}

    for entry in data.get("entities", []):
        eid, vid, path = entry.get("id"), entry.get("version_id"), entry.get("path")

        if eid:
            if eid in seen_entry_ids:
                errors.append(
                    f"{ctx}: Entity id '{eid}' listed more than once — the "
                    f"manifest defines exactly one CURRENT version per entity"
                )
            seen_entry_ids[eid] = entry
        if vid:
            if vid in seen_entry_versions:
                errors.append(f"{ctx}: version_id '{vid}' listed more than once")
            seen_entry_versions[vid] = entry
        if path:
            if path in seen_entry_paths:
                errors.append(f"{ctx}: Path '{path}' listed more than once")
            seen_entry_paths[path] = entry

            if not _path_is_contained(path):
                errors.append(
                    f"{ctx}: Path '{path}' is not contained in the package "
                    f"(absolute paths and '..' are rejected)"
                )
                continue

            entity_file = inv_path / path
            if not entity_file.exists():
                errors.append(f"{ctx}: Listed path '{path}' does not exist")
                continue
            file_data, ferr = load_yaml(entity_file)
            if ferr or not file_data:
                continue  # Parse errors reported by schema validation
            if eid and file_data.get("id") != eid:
                errors.append(
                    f"{ctx}: Entry id '{eid}' does not match id "
                    f"'{file_data.get('id')}' in {path}"
                )
            if vid and file_data.get("version_id") != vid:
                errors.append(
                    f"{ctx}: Entry version_id '{vid}' does not match version_id "
                    f"'{file_data.get('version_id')}' in {path}"
                )

    # Manifest investigation_id must match the Investigation entity it lists
    manifest_inv_id = data.get("investigation_id")
    if manifest_inv_id:
        for entry in data.get("entities", []):
            path = entry.get("path")
            if not path or not _path_is_contained(path):
                continue
            entity_file = inv_path / path
            if not entity_file.exists():
                continue
            file_data, ferr = load_yaml(entity_file)
            if ferr or not file_data:
                continue
            if file_data.get("type") == "investigation":
                if file_data.get("id") != manifest_inv_id:
                    errors.append(
                        f"{ctx}: investigation_id '{manifest_inv_id}' does not "
                        f"match the Investigation entity '{file_data.get('id')}' "
                        f"listed in the manifest"
                    )
                break

    return errors


def validate_revision_versions(yaml_file: Path, data: dict, version_index: dict) -> list[str]:
    """Revision old/new version_ids must reference version files that exist."""
    errors = []
    ctx = str(yaml_file)
    for field in ("old_version_id", "new_version_id"):
        vid = data.get(field)
        if vid and vid not in version_index:
            errors.append(
                f"{ctx}[{field}]: version_id '{vid}' does not correspond to "
                f"any entity version file"
            )
    old, new = data.get("old_version_id"), data.get("new_version_id")
    if old and new and old == new:
        errors.append(f"{ctx}: old_version_id and new_version_id are identical")
    return errors


def run_reference_validation(
    investigation_paths: list[Path],
    schema_dir: Path,
    verbose: bool = False,
) -> Tuple[bool, List[str]]:
    # Pass 1: index all defined IDs and versions
    id_index = {}
    version_index = {}
    entities = list(iter_entities(investigation_paths))
    for path, data in entities:
        if "id" in data:
            id_index[data["id"]] = path
        if "version_id" in data:
            version_index[data["version_id"]] = path

    if verbose:
        print(f"    Indexed {len(id_index)} entity IDs")

    # Pass 2: validate references
    all_errors = []
    for path, data in entities:
        all_errors.extend(validate_references_in_file(path, data, id_index))
        if data.get("type") == "revision":
            all_errors.extend(validate_revision_versions(path, data, version_index))

    # Pass 3: manifests (mandatory — the release authority)
    for inv_path in investigation_paths:
        all_errors.extend(validate_manifest(inv_path, id_index, version_index))

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
