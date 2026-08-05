#!/usr/bin/env python3
"""
Body of Evidence — Shared file discovery for validators.

All validators must use these helpers so that .yaml and .yml files are
treated identically everywhere. (A .yml file that bypasses semantic
validation is a validation hole.)
"""

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
    manifests. An investigation root that is itself a symlink is skipped
    entirely — not just flagged — so no validator ever reads or parses
    content that lives outside the checkout (fifth-pass review finding
    H-15; `p.is_dir()` in package discovery is true for a symlink to a
    directory, so this cannot rely on discovery having filtered it out).
    """
    files = []
    for inv_path in investigation_paths:
        if inv_path.is_symlink():
            continue
        for pattern in ("*.yaml", "*.yml"):
            files.extend(
                p for p in inv_path.rglob(pattern)
                if p.name != MANIFEST_NAME
            )
    return sorted(files)


def find_manifest(investigation_path: Path) -> Optional[Path]:
    """The package manifest for an investigation, if present. A symlinked
    investigation root has no manifest by definition (see find_entity_files)."""
    if investigation_path.is_symlink():
        return None
    manifest = investigation_path / MANIFEST_NAME
    return manifest if manifest.exists() else None


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
    if data is not None and not isinstance(data, dict):
        return None, f"{path}: Expected a mapping at the root level"
    return data, None


def iter_entities(investigation_paths: list[Path]) -> Iterator[Tuple[Path, dict]]:
    """Yield (path, data) for every parseable entity file."""
    for path in find_entity_files(investigation_paths):
        data, error = load_yaml(path)
        if data is not None and error is None:
            yield path, data
