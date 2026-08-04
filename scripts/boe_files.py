#!/usr/bin/env python3
"""
Body of Evidence — Shared file discovery for validators.

All validators must use these helpers so that .yaml and .yml files are
treated identically everywhere. (A .yml file that bypasses semantic
validation is a validation hole.)
"""

from pathlib import Path
from typing import Iterator, Tuple, Optional

import yaml

MANIFEST_NAME = "package.yaml"


def find_entity_files(investigation_paths: list[Path]) -> list[Path]:
    """All entity YAML files (both .yaml and .yml), excluding package manifests."""
    files = []
    for inv_path in investigation_paths:
        for pattern in ("*.yaml", "*.yml"):
            files.extend(
                p for p in inv_path.rglob(pattern)
                if p.name != MANIFEST_NAME
            )
    return sorted(files)


def find_manifest(investigation_path: Path) -> Optional[Path]:
    """The package manifest for an investigation, if present."""
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
