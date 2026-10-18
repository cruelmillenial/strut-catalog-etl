# Fitting submittal extraction contract (draft)

This stage inventories manufacturer documents without promoting placeholder fitting geometry.
The next stage reads each linked PDF and records a traceable candidate geometry **before** any normalized fitting is added to a released catalog snapshot.

## Source fields

- `id`: exact manufacturer part identifier, matched to the source manifest.
- `source_document_url`, `source_manifest_label`: stable manifest reference.
- `source_sha256`, `source_pages`: populated only after retrieving and inspecting the PDF.
- `geometry_family`: based on the depicted manufactured geometry, not assumptions from adjacent part numbers.
- `dimensions`: measured/catalog dimension declarations with units and cited pages.
- `hole_pattern`: counts, diameters, centers or center-to-center spacing, and orientation as explicitly shown.
- `verification_status`: `unverified`, `reviewed`, or `verified`.

## Family normalization guidelines

A fitting *family* describes a geometric construction method (flat plate, bent angle, shaped planar plate, etc.); a fitting *variant* identifies a manufacturer SKU. Hole count and diameter are variant properties and are not assumed to imply dimensions. If the vendor does not provide coordinates needed for exact geometry, retain a documented inference or mark geometry incomplete. Do not silently substitute the Workbench's pre-ETL placeholder dimensions.

## Promotion gates

1. PDF acquired with checksum and page-level provenance.
2. Drawing reviewed for outline, material thickness, hole count, hole diameter/slot geometry and placement.
3. Every dimension marked source-specified or inferred, with unit checks.
4. Structural validation of the normalized record and its hole array.
5. Reproducible snapshot build and downstream FreeCAD comparison.

As of this draft, manufacturer PDF downloads are **not** included in the repository and all four records remain unverified. This intentionally blocks claims of manufacturer-exact geometry.
