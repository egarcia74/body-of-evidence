#!/usr/bin/env python3
"""
Body of Evidence — Shared file discovery for validators.

All validators must use these helpers so that .yaml and .yml files are
treated identically everywhere. (A .yml file that bypasses semantic
validation is a validation hole.)
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Tuple, Optional

import yaml

MANIFEST_NAME = "package.yaml"


@dataclass(frozen=True)
class Diagnostic:
    """
    A structured validation failure — fourth-pass review finding M-10.
    Free-form error strings cannot be asserted exactly in tests (a wording
    change can accidentally satisfy a substring match) and cannot be
    consumed reliably by editors, AI agents, or MCP clients. `code` is the
    stable, machine-checkable identity of a diagnostic; `message` remains
    for humans. `location` (fifth-pass review finding M-07b) is the
    field name, JSON pointer segment, or manifest entry identifier the
    diagnostic is about, when it is about one — empty string for
    diagnostics that are not field-specific (e.g. a whole-package defect).
    It exists so tests can assert on WHICH occurrence failed, not just
    that a (validator, code) pair occurred somewhere.
    """

    code: str
    validator: str
    path: str
    message: str
    location: str = ""

    def __str__(self) -> str:
        return self.message


def find_entity_files(investigation_paths: list[Path]) -> list[Path]:
    """
    All entity YAML files (both .yaml and .yml), excluding package
    manifests and excluding any file — or package root — that is itself a
    symlink.

    An investigation root that is a symlink is skipped entirely (fifth-pass
    review H-15; `p.is_dir()` in package discovery is true for a symlink to
    a directory, so this cannot rely on discovery having filtered it out).

    An individual entity file that is a symlink is ALSO skipped, even when
    it isn't listed in the manifest (sixth-pass review H-19). Historical/
    superseded version files are legitimately unmanifested by design
    (D-009) — that's exactly why they can't rely on the manifest-path
    containment check, which only inspects listed paths. A symlinked
    unmanifested file would otherwise let validation silently read content
    from outside the package (or crash on a broken symlink; see
    load_yaml's OSError handling). See also find_all_symlinks, which turns
    this silent exclusion into an explicit diagnostic.
    """
    files = []
    for inv_path in investigation_paths:
        if inv_path.is_symlink():
            continue
        for pattern in ("*.yaml", "*.yml"):
            files.extend(
                p for p in inv_path.rglob(pattern)
                if p.name != MANIFEST_NAME and not p.is_symlink()
            )
    return sorted(files)


def find_manifest(investigation_path: Path) -> Optional[Path]:
    """The package manifest for an investigation, if present. A symlinked
    investigation root has no manifest by definition (see find_entity_files).
    A manifest FILE that is itself a symlink is also refused — it would
    otherwise let arbitrary external content be read and trusted as the
    package's release authority (sixth-pass review H-19's principle applied
    to package.yaml, not just entity files)."""
    if investigation_path.is_symlink():
        return None
    manifest = investigation_path / MANIFEST_NAME
    if manifest.is_symlink():
        return None
    return manifest if manifest.exists() else None


def find_all_symlinks(investigation_paths: list[Path]) -> list[Path]:
    """
    Every symlink anywhere inside a package — any file, any directory, any
    extension, manifested or not. Surfaced separately so a validator can
    turn silent exclusion into an explicit diagnostic instead of the
    package simply appearing to have fewer files than it does.

    This supersedes an earlier version that only scanned *.yaml/*.yml files
    (sixth-pass review H-19); the seventh-pass review found that a
    symlinked SUBDIRECTORY, or a symlink to a non-YAML file, was invisible
    to that narrower scan — `find_entity_files`'s rglob doesn't currently
    follow a symlinked directory in this pathlib version (so nothing
    inside one is actually READ), but the symlink itself went completely
    undetected, which is still a policy violation: a future tool with
    different traversal behaviour (a generator, an MCP server) could read
    through it, and "the validator happens not to look" is not the same
    guarantee as "the package contains no symlinks" (seventh-pass M-20).

    Uses os.walk(followlinks=False) rather than pathlib globbing so
    detection does not depend on a particular pathlib version's symlink
    traversal behaviour: os.walk lists a symlinked directory in `dirnames`
    (so it's still detected) but never descends into it.

    Symlinked package ROOTS are not included here; those are reported
    separately (see run_reference_validation's INVESTIGATION_ROOT_SYMLINK).
    """
    found = []
    for inv_path in investigation_paths:
        if inv_path.is_symlink():
            continue
        for dirpath, dirnames, filenames in os.walk(inv_path, followlinks=False):
            base = Path(dirpath)
            for name in (*dirnames, *filenames):
                candidate = base / name
                if candidate.is_symlink():
                    found.append(candidate)
    return sorted(found)


def load_yaml(path: Path) -> Tuple[Optional[dict], Optional[str]]:
    """
    Load a YAML file. Returns (data, error).
    Rejects duplicate keys — silent duplicate-key overwrites are a data
    integrity hazard in hand-authored evidence files.
    """

    class StrictLoader(yaml.SafeLoader):
        pass

    def _no_duplicates(loader, node, deep=False):
        mapping = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            if key in mapping:
                raise yaml.YAMLError(f"Duplicate key: {key!r}")
            mapping[key] = loader.construct_object(value_node, deep=deep)
        return mapping

    StrictLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_duplicates
    )

    try:
        with open(path) as f:
            data = yaml.load(f, Loader=StrictLoader)
    except yaml.YAMLError as e:
        return None, f"{path}: YAML error: {e}"
    except OSError as e:
        # A broken symlink (or a permissions/IO failure) must become a
        # diagnostic, not an uncaught crash of the whole validation run
        # (sixth-pass review H-19).
        return None, f"{path}: Could not read file: {e}"
    if data is not None and not isinstance(data, dict):
        return None, f"{path}: Expected a mapping at the root level"
    return data, None


def iter_entities(investigation_paths: list[Path]) -> Iterator[Tuple[Path, dict]]:
    """Yield (path, data) for every parseable entity file."""
    for path in find_entity_files(investigation_paths):
        data, error = load_yaml(path)
        if data is not None and error is None:
            yield path, data
