#!/usr/bin/env python3
"""
Body of Evidence — Shared file discovery for validators.

All validators must use these helpers so that .yaml and .yml files are
treated identically everywhere. (A .yml file that bypasses semantic
validation is a validation hole.)
"""

import hashlib
import os
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Iterator

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

    Shared by discover_package and the retained find_* primitives so all
    of them see exactly the same tree and the same failures. This is the
    only function that TRAVERSES a package tree, which is what makes "each
    package is walked exactly once per run" a testable claim rather than a
    convention (eleventh-pass review L-12) — it is deliberately not a claim
    that no other code touches the filesystem at all: find_manifest still
    stats one known path, and validate_references stats manifest-listed
    ones. Those are single-path checks, not enumeration, and cannot hide a
    file the way a second traversal could.

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
class DiscoveredDocument:
    """
    One document's RAW BYTES, read exactly once per validation run, with a
    SHA-256 digest of what was read.

    What this guarantees, precisely (H-24 — an earlier version of this class
    held a single parsed `dict` shared by every validator and claimed they
    "necessarily inspect the same bytes"; a reviewer mutated one validator's
    view of that dict and turned a failing package into a passing one, which
    made the shared object WORSE than re-reading, not better):

      - ONE filesystem read per document per run. Five validators cannot
        observe five different versions of a file mid-run.
      - Every validator parses THE SAME BYTES, and `digest` makes that
        checkable rather than merely asserted.
      - `parse()` builds a FRESH object graph on every call, so one
        validator mutating what it got back cannot corrupt another's view.
        Isolation is by construction; it does not depend on validators
        promising not to mutate.

    What it does NOT guarantee: that `raw` still matches the file on disk.
    The read already happened; a later write is invisible here. `digest`
    exists so that D-016's Edition work can eventually verify that what was
    published is what was validated — the honest place to close that.
    """

    path: Path
    raw: bytes | None
    digest: str | None
    read_error: str | None

    def parse(self) -> tuple[dict | None, str | None]:
        """(data, error) parsed fresh from the captured bytes. Returns a NEW
        object graph each call — callers may mutate what they receive without
        affecting any other caller."""
        if self.read_error is not None:
            return None, self.read_error
        return parse_yaml_bytes(self.raw, self.path)


@dataclass(frozen=True, kw_only=True)
class PackageDiscovery:
    """
    Every filesystem-integrity fact about ONE package root, plus the parsed
    content of every document in it, from exactly one walk (tenth-pass
    review M-24: `find_entity_files`, `find_all_symlinks`, and
    `find_traversal_errors` previously each walked the same tree
    independently — three passes of I/O over the same directories).

    This is an ENUMERATION-AND-READ snapshot of one package, NOT a guarantee
    about the filesystem: the walk and the reads are separate syscalls, so a
    file can change between being enumerated and being read, and can change
    again afterwards (eleventh-pass review M-29 — an earlier version of this
    docstring claimed collapsing the walks closed the time-of-check/
    time-of-use gap, which it did not). What it guarantees is one walk and
    one read per document per run, and that every validator parses identical
    bytes. Closing the gap against the filesystem needs the captured digests
    re-checked at publication — deferred to D-016's Edition work, which has
    to define what a released package's authoritative bytes ARE first.

    **This type is INTERNAL** (H-24). It is not an access-control boundary
    and must not be described as one: any in-process caller can construct
    one, and Python offers no way to prevent that. An earlier version tried,
    via a module-private "proof-of-walk" token; a reviewer imported
    `boe_files._WALK_TOKEN` — underscores are a convention, not enforcement
    — built an empty discovery for a known-invalid package and got a clean
    pass. The supported entry point is `validate.validate_paths(paths)`,
    which constructs its own context; everything here is implementation
    detail behind it, and the integrity guarantees this project makes are
    about THAT surface, not about resisting an adversary already executing
    in the same interpreter.

    `root_is_symlink=True` means the walk never happened at all (a symlinked
    root is rejected before descending into it); the other fields are then
    always empty/None, not merely unpopulated.

    The remaining __post_init__ checks are self-consistency guards against
    programming error — a future factory bug producing a discovery whose
    contents don't belong to its root, or reintroducing mutable lists — not
    security controls.
    """

    root: Path
    documents: tuple[DiscoveredDocument, ...]
    manifest: DiscoveredDocument | None
    root_is_symlink: bool
    internal_symlinks: tuple[Path, ...]
    traversal_errors: tuple[OSError, ...]

    def __post_init__(self):
        for name in ("documents", "internal_symlinks", "traversal_errors"):
            value = getattr(self, name)
            if not isinstance(value, tuple):
                raise TypeError(
                    f"PackageDiscovery.{name} must be a tuple, not "
                    f"{type(value).__name__} — mutable collections in a "
                    f"frozen dataclass are not immutable (M-29)"
                )
        # A discovery whose contents don't belong to its own root is
        # self-inconsistent. This catches a factory bug, not an adversary
        # (see the class docstring on why no in-process check could).
        for path in tuple(d.path for d in self.documents) + self.internal_symlinks:
            if not path.is_relative_to(self.root):
                raise ValueError(
                    f"PackageDiscovery for root {self.root} contains {path}, "
                    f"which is outside that root"
                )
        if self.root_is_symlink and (self.documents or self.internal_symlinks
                                     or self.traversal_errors or self.manifest):
            raise ValueError(
                f"PackageDiscovery for symlinked root {self.root} must be "
                f"empty — a symlinked root is never walked"
            )

    @property
    def entity_files(self) -> tuple[Path, ...]:
        """Paths of every discovered entity document, in discovery order."""
        return tuple(d.path for d in self.documents)


def discover_package(inv_path: Path) -> PackageDiscovery:
    """One walk of one package root, followed by one read of each document
    it found, producing every fact a validator's preflight, entity-iteration
    and manifest steps need. This and _walk_package are the only places
    package content enters validation."""
    if inv_path.is_symlink():
        return PackageDiscovery(
            root=inv_path, documents=(), manifest=None, root_is_symlink=True,
            internal_symlinks=(), traversal_errors=(),
        )
    files, symlinks, errors = _walk_package(inv_path)
    entity_files = sorted(
        p for p in files if p.suffix in (".yaml", ".yml") and p.name != MANIFEST_NAME
    )
    documents = tuple(_read_document(p) for p in entity_files)
    manifest_path = find_manifest(inv_path)
    manifest = _read_document(manifest_path) if manifest_path is not None else None
    return PackageDiscovery(
        root=inv_path, documents=documents, manifest=manifest, root_is_symlink=False,
        internal_symlinks=tuple(sorted(symlinks)), traversal_errors=tuple(errors),
    )


def _read_document(path: Path) -> DiscoveredDocument:
    """Read one document's bytes once and digest them. Parsing is deferred
    to DiscoveredDocument.parse(), which builds a fresh object graph per
    call so validators cannot corrupt each other's view (H-24)."""
    try:
        raw = path.read_bytes()
    except OSError as e:
        # A broken symlink or permissions failure must become a diagnostic,
        # not an uncaught crash of the whole run (see load_yaml).
        return DiscoveredDocument(
            path=path, raw=None, digest=None,
            read_error=f"{path}: Could not read file: {e}",
        )
    return DiscoveredDocument(
        path=path, raw=raw, digest=hashlib.sha256(raw).hexdigest(), read_error=None,
    )


@dataclass(frozen=True)
class ValidationContext:
    """
    The single, self-consistent input to every `run_*_validation` function
    (eleventh-pass review H-23).

    Validators previously took BOTH `investigation_paths` and an optional
    `discoveries` list, with nothing checking that the two described the
    same packages. The review passed an EMPTY discovery alongside the
    known-invalid `fixtures/invalid/duplicate-version-id` root and got
    `passed=True, errors=[]` — a vacuous pass, which invariant 10 exists
    specifically to prohibit. The production CLI happened to construct
    matching inputs, so this was never a CLI bypass; it was a hole in the
    reusable Python API, which is the surface a future MCP server would
    build on.

    The fix is not to cross-check two inputs but to have only one: roots
    are DERIVED from the discoveries, so a context whose roots and
    discoveries disagree is unrepresentable rather than merely rejected.
    Build one with `ValidationContext.for_paths(paths)` — the single
    controlled factory — and pass the same context to every validator in a
    run so each package is walked and read exactly once for the whole run.
    """

    discoveries: tuple[PackageDiscovery, ...]

    def __post_init__(self):
        if not isinstance(self.discoveries, tuple):
            raise TypeError(
                f"ValidationContext.discoveries must be a tuple, not "
                f"{type(self.discoveries).__name__} (M-29)"
            )
        for d in self.discoveries:
            if not isinstance(d, PackageDiscovery):
                raise TypeError(
                    f"ValidationContext.discoveries must contain "
                    f"PackageDiscovery objects, found {type(d).__name__}"
                )
        roots = [d.root for d in self.discoveries]
        if len(set(roots)) != len(roots):
            raise ValueError(
                f"ValidationContext has duplicate package roots: {roots} — "
                f"a package would be validated, and its diagnostics "
                f"reported, more than once"
            )

    @classmethod
    def for_paths(cls, investigation_paths) -> "ValidationContext":
        """The one controlled way to build a context: walk and read each
        requested root exactly once. CALL THIS ONCE per validation run and
        pass the result to every validator (see validate.py's
        `run_all_checks`) — building a separate context per validator
        re-walks and re-reads every package once per validator, which is
        both wasted I/O and the divergence DiscoveredDocument exists to
        prevent."""
        return cls(discoveries=tuple(discover_package(p) for p in investigation_paths))

    @property
    def roots(self) -> tuple[Path, ...]:
        """The package roots this context covers. Derived from the
        discoveries, never stored alongside them — that split was H-23."""
        return tuple(d.root for d in self.discoveries)

    @property
    def real_roots(self) -> tuple[Path, ...]:
        """Roots that were actually walked, i.e. excluding symlinked roots
        (which are rejected by preflight and never inspected). This is the
        set a validator should use for package-ownership questions."""
        return tuple(d.root for d in self.discoveries if not d.root_is_symlink)

    def entity_files(self) -> list[Path]:
        """Every discovered entity path across every package, globally
        sorted so multi-package runs report in a stable order."""
        return sorted(p for d in self.discoveries for p in d.entity_files)

    def documents(self) -> list[DiscoveredDocument]:
        """Every discovered document across every package, globally sorted
        by path — including ones that failed to parse, which only
        validate_schema reports on."""
        return sorted(
            (doc for d in self.discoveries for doc in d.documents),
            key=lambda doc: doc.path,
        )

    def entities(self) -> Iterator[tuple[Path, dict]]:
        """(path, data) for every parseable, non-empty entity document —
        the iteration path for validators that only inspect well-formed
        entities. No filesystem access: the bytes were read once at
        discovery. Each call re-parses those bytes, so the mapping a caller
        receives is its own and mutating it cannot affect any other
        validator (H-24)."""
        for doc in self.documents():
            data, error = doc.parse()
            if data is not None and error is None:
                yield doc.path, data

    @cached_property
    def _documents_by_path(self) -> dict[Path, DiscoveredDocument]:
        """Path -> document index, built once on first lookup. Manifest
        validation looks up one document per manifest entry, so a linear
        scan would make that pass quadratic in package size — the same
        repeated-work shape the tenth-pass review flagged for walks
        (M-24) and the eleventh for reads (M-29). `cached_property` writes
        straight into __dict__, which is why it works on a frozen
        dataclass."""
        return {doc.path: doc for d in self.discoveries for doc in d.documents}

    def document_for(self, path: Path) -> DiscoveredDocument | None:
        """The already-read document at `path`, or None if this context
        never discovered it. Used by manifest validation to check
        manifest-listed files against the SAME bytes the other validators
        saw, instead of re-opening them."""
        return self._documents_by_path.get(path)


def preflight_diagnostics(context: ValidationContext, validator: str) -> list[Diagnostic]:
    """
    Every filesystem-integrity diagnostic (symlinked root, internal symlink,
    unreadable subtree) a validator must report BEFORE its own domain checks
    run, for the given context.

    Every validator must call this (tenth-pass review M-27: only
    `run_reference_validation` used to reject internal symlinks — discovery
    silently excludes a symlinked entity file either way, so the other four
    standalone checks passed vacuously on a package they had not actually
    fully inspected, same failure class as the eighth-pass M-22/H-22 root
    and traversal gaps).
    """
    diagnostics = []
    for d in context.discoveries:
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


def find_manifest(investigation_path: Path) -> Path | None:
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


def _strict_loader():
    """A SafeLoader that rejects duplicate keys — silent duplicate-key
    overwrites are a data integrity hazard in hand-authored evidence files.
    Built per call so the constructor registration cannot leak into
    yaml.SafeLoader itself."""

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
    return StrictLoader


def load_yaml(path: Path) -> tuple[dict | None, str | None]:
    """
    Load a YAML file directly from disk. Returns (data, error).

    Retained for the find_* primitives and for direct callers; the
    validation pipeline goes through DiscoveredDocument.parse() instead, so
    that a document is READ once per run even though it is parsed per
    validator.
    """
    try:
        with open(path) as f:
            source = f.read()
    except OSError as e:
        # A broken symlink (or a permissions/IO failure) must become a
        # diagnostic, not an uncaught crash of the whole validation run
        # (sixth-pass review H-19).
        return None, f"{path}: Could not read file: {e}"
    return _parse_yaml(source, path)


def parse_yaml_bytes(raw: bytes, path: Path) -> tuple[dict | None, str | None]:
    """Parse already-read bytes, with identical semantics to load_yaml —
    the entry point DiscoveredDocument.parse() uses, so bytes captured once
    at discovery and a direct file read cannot diverge in how they are
    interpreted (H-24)."""
    try:
        source = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        return None, f"{path}: Could not decode file as UTF-8: {e}"
    return _parse_yaml(source, path)


def _parse_yaml(source: str, path: Path) -> tuple[dict | None, str | None]:
    """The single YAML parsing implementation. Returns a NEW object graph
    on every call — never a cached or shared one."""
    try:
        data = yaml.load(source, Loader=_strict_loader())
    except yaml.YAMLError as e:
        return None, f"{path}: YAML error: {e}"
    if data is not None and not isinstance(data, dict):
        return None, f"{path}: Expected a mapping at the root level"
    return data, None


def iter_entities(investigation_paths: list[Path]) -> Iterator[tuple[Path, dict]]:
    """Yield (path, data) for every parseable entity file."""
    for path in find_entity_files(investigation_paths):
        data, error = load_yaml(path)
        if data is not None and error is None:
            yield path, data
