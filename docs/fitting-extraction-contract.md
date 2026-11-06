# Fitting submittal extraction and geometry contract (draft)

The manufacturer submittals for P1065–P1068 have been inspected (page 1 each), with their SHA-256 digests and visible drawing callouts recorded in `etl/fittings/source_inventory.json`. They are **candidate inventory records**, not fully dimensioned CAD definitions. The PDFs themselves are not committed to this repository. In particular, no manufacturer-exact hole diameter or center array has been established.

## Source records and observations

- `id`, `source_document_url`, `source_manifest_label`: manufacturer and manifest identity.
- `source_sha256`, `source_pages`: observed PDF checksums and inspected pages.
- `geometry_family`: shape classification from the depicted fitting, independent of manufacturer-specific dimensional claims.
- `drawing_callouts`: numbers actually printed in the sheet, with page and units. Manufacturer metric values may be rounded and must not silently replace exact fractional-inch callouts.
- `visible_hole_count`: counted in illustration, not an extracted hole-pattern dimension.
- `dimensions` and `hole_pattern`: remain `null` until complete geometry is established.
- `geometry_gaps`: unresolved inputs blocking promotion.

## Flat splice plate geometry contract (P1065–P1067)

One planar rectangular plate builder accommodates multiple counts of round holes. Proposed normalized coordinates and dimensions are millimeters, with **origin at one outside corner**, **X along overall length**, **Y along plate width**, and **Z through thickness**. An explicit ordered hole list is preferred to assuming equal pitch.

`src/strut_catalog_etl/fitting_geometry.py:validate_flat_plate` is the initial shape-integrity gate. A complete candidate must provide:

- `family = "flat_splice_plate"`
- positive `length_mm`, `width_mm`, `thickness_mm`
- nonempty `holes`, each `{"shape": "round", "x_mm": ..., "y_mm": ..., "diameter_mm": ...}`
- every round hole strictly inside the rectangle; no overlapping holes

The validator verifies geometry feasibility **only**. It does not establish manufacturer authenticity, strength, clearance standards, accuracy, or provenance, nor does it convert an inspected inventory record into a released record. The initial code intentionally rejects slotted holes; those need a separate geometric contract. A test fixture with synthetic dimensions is not a representation of P1065.

## Fastener selection and variation

Separate **nominal fastener diameter**, **hole clearance policy**, and **actual hole diameter**. The first two may determine a custom hole size; manufacturer-observed hole diameter remains authoritative in catalog mode. Custom geometry must not retain an unqualified manufacturer-exact SKU identity. Support both customary and metric nominal bolt selections in the eventual front end.

## Metrology / source gap disposition

Before exact release promotion, acquire manufacturer dimensioned drawings or inspect a **positively identified, authentic part**. For P1065–P1067 obtain plate width, thickness, overall length confirmation, per-hole diameter/shape, center coordinates or end offsets + pitch, and relevant edge/corner details. Record measurement method, instrument, resolution, uncertainty/repeatability where possible, sample count, part identity and finish, units, measurement date and operator. A single physical sample gives *observed sample geometry*, not manufacturer design nominal or tolerance. Do not infer tolerance, exact nominal dimensions or structural rating from samples.

P1068 is a distinct bent/angle family and additionally needs accurate bend/offset and dimension-datum definition.

## Release promotion gate

1. Provenance and part identity established.
2. Fully defined geometry with explicitly documented origins (`manufacturer_print`, `measured_sample`, or separately flagged engineering assumptions/derivations).
3. Semantic geometry validation and provenance checks; complete hole geometry required.
4. Reproducible snapshot, regression tests and downstream FreeCAD comparison.
5. Explicit review decision to promote; **no automatic promotion from the candidate inventory**.

As of this revision **P1065–P1068 remain excluded from release snapshots**, and `dimensions`/`hole_pattern` remain null.
