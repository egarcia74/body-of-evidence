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


def validate_manifest(inv_path: Path, id_index: dict, version_index: dict) -> list[str]:
    """Check the package manifest is consistent with the entity files it lists."""
    errors = []
    manifest_path = find_manifest(inv_path)
    if manifest_path is None:
        return errors
    data, error = load_yaml(manifest_path)
    if error:
        return [error]
    if not data:
        return errors

    ctx = str(manifest_path)
    for entry in data.get("entities", []):
        eid, vid, path = entry.get("id"), entry.get("version_id"), entry.get("path")
        if path:
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

    # Pass 3: manifests
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
