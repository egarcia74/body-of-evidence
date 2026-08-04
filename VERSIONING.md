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
- New investigations published (investigations are platform content, not schema)

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

Each JSON Schema file includes a `$schema` reference and a `version` field. When a schema changes in a backwards-incompatible way, the schema file version is incremented and the old version is preserved at `schema/v{N}/`.

## Changelog

All version changes are documented in [CHANGELOG.md](CHANGELOG.md).

## Release Tags

Releases are tagged in Git as `v{MAJOR}.{MINOR}.{PATCH}`. Investigations published within a version are part of that version's tag.
