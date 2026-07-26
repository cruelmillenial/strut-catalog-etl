# Architecture

## Responsibility boundary

`strut-catalog-etl` owns source acquisition metadata, extraction, normalization, validation, correction overlays, and publication of deterministic catalog snapshots.

Downstream applications such as `UnistrutWB` consume generated snapshots only. They do not parse vendor PDFs, scrape websites, or depend on this repository at runtime.

## Initial pipeline

1. Register a source document and checksum.
2. Extract candidate records from the source.
3. Normalize vendor fields into canonical profile and fitting records.
4. Apply explicit correction overlays where automation is insufficient.
5. Validate records against schemas and cross-record invariants.
6. Emit stable, sorted JSON plus a catalog manifest.
7. Test the generated snapshot against representative downstream expectations.

## Non-goals for the scaffold phase

- finalizing the canonical schema;
- committing redistribution-restricted vendor documents;
- adding web scraping;
- coupling publication directly to `UnistrutWB` releases.
