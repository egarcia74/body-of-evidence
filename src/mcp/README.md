# MCP Server — Future Implementation

This directory will contain the Body of Evidence MCP (Model Context Protocol) server.

**Status:** Not yet implemented. Planned for v0.3.

## Intended Tool Surface

```
search_claims(query, investigation?, confidence_min?)
    → Returns matching Claim entities with confidence and assessment summary

search_sources(query, type?, date_range?)
    → Returns matching Source entities with provenance

search_people(query)
    → Returns matching Person entities and their investigation connections

search_events(date_range?, query?)
    → Returns matching Event entities ordered chronologically

retrieve_evidence(evidence_id)
    → Returns a specific Evidence entity with source and claim context

compare_claims(claim_id_a, claim_id_b)
    → Returns both claims, their evidence, and any direct relationship between them

get_timeline(investigation_id)
    → Returns the ordered Timeline for an investigation

get_relationship_graph(entity_id, depth?)
    → Returns the relationship graph centred on an entity

confidence_lookup(claim_id)
    → Returns the current Assessment for a claim with full rationale
```

## Design Notes

- The data model is designed from v0.1 to support these tools without schema changes
- All entities are YAML files; the MCP server will index them on startup
- The server will be read-only — it queries the evidence model but does not modify it
- Authentication will be optional; the underlying data is public

## Implementation Language

TBD. Likely Python using the official MCP SDK, or TypeScript.
See DECISIONS.md for the rationale for deferring implementation to v0.3.
