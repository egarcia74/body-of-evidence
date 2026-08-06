# Versioning

Body of Evidence uses [Semantic Versioning 2.0.0](https://semver.org/).

## Version Format

`MAJOR.MINOR.PATCH`

## What Each Component Means

### MAJOR

Breaking changes to the schema that are not backwards-compatible. A `MAJOR` bump means:

- An existing valid entity file may no longer validate against the new schema
- Consumers of the data (MCP clients, generated sites, third-party tools) must update to handle the new format
- A migration guide is published

MAJOR version bumps are preceded by a deprecation period of at least one MINOR version, during which both old and new formats are supported.

### MINOR

Backwards-compatible additions to schema or platform capabilities. A `MINOR` bump means:

- New optional fields added to existing entity types
- New entity types added
- New tools, scripts, or platform features
- ~~New investigations published~~ — **no longer a MINOR trigger.** Publishing investigation content does not
  version the platform; a package carries its own `release_version` (see Release Tags below). Coupling them
  would force a platform release for every investigation. Changed 2026-08-06 with D-016; nothing depended on
  the old rule, because no investigations are published yet.

Existing valid entity files continue to validate against the new schema.

### PATCH

Backwards-compatible fixes. A `PATCH` bump means:

- Bug fixes in validation scripts
- Corrections to documentation
- Fixes to broken links or references
- Minor clarifications to schema descriptions that do not change validation behaviour

## Pre-1.0 Stability

During the 0.x series, MINOR version bumps may include breaking schema changes. The schema is not considered stable until v1.0.

## Schema Versioning

Each JSON Schema file includes a `$schema` reference and a `version` field; all schemas in a commit form one coherent bundle version (currently 0.2.0), and package manifests declare which bundle version their entities conform to. Preservation of superseded schema bundles (planned location: `schema/v{N}/`) and a migration policy are pre-1.0 requirements that do NOT exist yet — during 0.x, schema history lives only in Git.

## Changelog

All version changes are documented in [CHANGELOG.md](CHANGELOG.md).

## Release Tags

Releases are tagged in Git as `v{MAJOR}.{MINOR}.{PATCH}`. **This versions the PLATFORM** — the schema, tooling and documentation.

An investigation package carries its own `release_version` in `package.yaml`, which `package.schema.json` defines as "independent of the platform/schema version." Platform version and package release version are therefore two separate axes: a Git tag does not determine which release of an investigation it contains. (An earlier version of this section said investigations published within a version are "part of that version's tag," which contradicted the manifest schema. Corrected 2026-08-06 while designing D-016, which makes the package-release axis explicit as an Edition.)
