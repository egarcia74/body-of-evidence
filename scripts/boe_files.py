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


def _walk_package(inv_path: Path) -> tuple[list[Path], list[Path], list[OSError]]:
    """
    Walk one package tree with os.walk(followlinks=False), returning
    (files, symlinks, errors):
      files    -- non-symlink file Paths
      symlinks -- symlink Paths, file or directory (never descended into)
      errors   -- one OSError per subdirectory os.walk could not list

    Shared by find_entity_files and find_all_symlinks so both see exactly
    the same tree and the same failures.

    Without an `onerror` callback, os.walk SILENTLY skips any subdirectory
    it cannot list (e.g. permission denied) — the caller gets an empty
    result for that subtree with no indication anything was skipped
    (eighth-pass review M-22). `pathlib.rglob`, previously used here, has
    the identical silent-skip behaviour for the same reason (it also just
    calls os.scandir per directory and swallows OSError). Collecting
    errors explicitly lets a validator fail closed — see
    find_traversal_errors — instead of certifying a package it did not
    completely inspect.
    """
    files: list[Path] = []
    symlinks: list[Path] = []
    errors: list[OSError] = []

    for dirpath, dirnames, filenames in os.walk(inv_path, onerror=errors.append, followlinks=False):
        base = Path(dirpath)
        for name in dirnames:
            candidate = base / name
            if candidate.is_symlink():
                symlinks.append(candidate)
        for name in filenames:
            candidate = base / name
            if candidate.is_symlink():
                symlinks.append(candidate)
            else:
                files.append(candidate)
    return files, symlinks, errors


@dataclass(frozen=True)
class PackageDiscovery:
    """
    Every filesystem-integrity fact about ONE package root, from exactly one
    walk (tenth-pass review M-24: `find_entity_files`, `find_all_symlinks`,
    and `find_traversal_errors` previously each walked the same tree
    independently — three passes of I/O, and a time-of-check/time-of-use gap
    between the "is this safe" pass and the "read these files" pass).

    `root_is_symlink=True` means the walk never happened at all (a symlinked
    root is rejected before descending into it — see find_entity_files); the
    other three fields are then always empty, not merely unpopulated.
    """

    root: Path
    entity_files: list[Path]
    root_is_symlink: bool
    internal_symlinks: list[Path]
    traversal_errors: list[OSError]


def discover_package(inv_path: Path) -> PackageDiscovery:
    """One walk of one package root, producing every fact a validator's
    preflight and entity-iteration steps need."""
    if inv_path.is_symlink():
        return PackageDiscovery(
            root=inv_path, entity_files=[], root_is_symlink=True,
            internal_symlinks=[], traversal_errors=[],
        )
    files, symlinks, errors = _walk_package(inv_path)
    entity_files = sorted(
        p for p in files if p.suffix in (".yaml", ".yml") and p.name != MANIFEST_NAME
    )
    return PackageDiscovery(
        root=inv_path, entity_files=entity_files, root_is_symlink=False,
        internal_symlinks=sorted(symlinks), traversal_errors=errors,
    )


def discover_packages(investigation_paths: list[Path]) -> list[PackageDiscovery]:
    """One PackageDiscovery per requested root, each from its own single
    walk. CALL THIS ONCE per CLI run and pass the SAME result to every
    `run_*_validation(..., discoveries=...)` call — every validator accepts
    that parameter and falls back to calling this itself only when omitted
    (see validate.py's `run_all_checks`, the actual entry point for a
    `--check all` run and for `--self-test`). Calling this separately per
    validator, rather than once and threading the result through, re-walks
    the same tree once per validator — the tenth-pass review's own
    CodeRabbit pass caught exactly that gap in this function's first
    version."""
    return [discover_package(p) for p in investigation_paths]


def preflight_diagnostics(discoveries: list[PackageDiscovery], validator: str) -> list[Diagnostic]:
    """
    Every filesystem-integrity diagnostic (symlinked root, internal symlink,
    unreadable subtree) a validator must report BEFORE its own domain checks
    run, for the given discoveries.

    Every validator that consumes entity files via `discoveries` must call
    this too (tenth-pass review M-27: only `run_reference_validation` used
    to reject internal symlinks — `find_entity_files` silently excludes a
    symlinked entity file either way, so the other four standalone checks
    passed vacuously on a package they had not actually fully inspected,
    same failure class as the eighth-pass M-22/H-22 root and traversal gaps).
    """
    diagnostics = []
    for d in discoveries:
        if d.root_is_symlink:
            diagnostics.append(Diagnostic(
                "INVESTIGATION_ROOT_SYMLINK", validator, str(d.root),
                f"{d.root}: package root is a symlink — symlinked package "
                f"roots are prohibited (they can point anywhere on disk, "
                f"bypassing every per-path containment check)",
            ))
            continue
        for symlinked in d.internal_symlinks:
            diagnostics.append(Diagnostic(
                "PACKAGE_SYMLINK", validator, str(symlinked),
                f"{symlinked}: symlink found inside a package — symlinks "
                f"are prohibited anywhere in a package, including "
                f"unmanifested historical versions, subdirectories, and "
                f"non-YAML files (they can indirect to content outside the "
                f"package, or crash validation if broken)",
            ))
        for exc in d.traversal_errors:
            failed_dir = getattr(exc, "filename", None) or d.root
            diagnostics.append(Diagnostic(
                "PACKAGE_SUBTREE_UNREADABLE", validator, str(failed_dir),
                f"{failed_dir}: could not list directory contents ({exc}) — "
                f"a package cannot be certified when part of it was not "
                f"inspectable",
            ))
    return diagnostics


def entity_files_from(discoveries: list[PackageDiscovery]) -> list[Path]:
    """All entity files across every discovery, globally sorted — matches
    find_entity_files's ordering for callers that iterate multiple packages."""
    return sorted(p for d in discoveries for p in d.entity_files)


def entities_from(discoveries: list[PackageDiscovery]) -> Iterator[Tuple[Path, dict]]:
    """Yield (path, data) for every parseable entity file across every
    discovery, without re-walking the filesystem."""
    for path in entity_files_from(discoveries):
        data, error = load_yaml(path)
        if data is not None and error is None:
            yield path, data


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
    this silent exclusion into an explicit diagnostic, and
    find_traversal_errors, which surfaces unreadable subtrees the same way.
    """
    files = []
    for inv_path in investigation_paths:
        if inv_path.is_symlink():
            continue
        pkg_files, _, _ = _walk_package(inv_path)
        files.extend(
            p for p in pkg_files
            if p.suffix in (".yaml", ".yml") and p.name != MANIFEST_NAME
        )
    return sorted(files)


def find_traversal_errors(investigation_paths: list[Path]) -> list[tuple[Path, OSError]]:
    """
    Every package subtree that could not be fully enumerated — paired with
    the package root it occurred under. A validator MUST turn each of
    these into a failing diagnostic rather than silently certifying a
    package part of which was never actually inspected (eighth-pass review
    M-22): an unreadable directory could just as easily be hiding a
    prohibited symlink or an entity file with a policy violation.
    """
    result = []
    for inv_path in investigation_paths:
        if inv_path.is_symlink():
            continue
        _, _, errors = _walk_package(inv_path)
        result.extend((inv_path, exc) for exc in errors)
    return result


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
    Unreadable subtrees are ALSO not included here — a directory os.walk
    could not list contains, by definition, no symlinks this function can
    see; see find_traversal_errors for surfacing that failure itself.
    """
    found = []
    for inv_path in investigation_paths:
        if inv_path.is_symlink():
            continue
        _, symlinks, _ = _walk_package(inv_path)
        found.extend(symlinks)
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
