# Fitting submittal extraction and geometry contract (draft)

The manufacturer submittals for P1065–P1068 have been inspected (page 1 each), with their SHA-256 digests and visible drawing callouts recorded in `etl/fittings/source_inventory.json`. They are **candidate inventory records**, not fully dimensioned CAD definitions. The PDFs themselves are not committed to this repository. A directly inspected manufacturer catalog has subsequently supplied nominal family dimensions for P1065–P1067. Those reference dimensions are represented separately; the inventoried candidates are **not** release records.

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

## Direct manufacturer catalog reference: flat-plate series

The uploaded `unistrut-general-catalog.pdf`, **printed page 81** (PDF page 81), specifies a common rule for the **1-5/8 in width fittings unless otherwise shown**: 9/16 in hole diameter, 13/16 in from free end to center, 1-7/8 in center pitch and 1-5/8 in plate width. Its steel thickness is **conditional**: 1/4 in for steel meeting/exceeding ASTM A1011 SS GR 33, **or** 0.220 in for steel meeting/exceeding ASTM A1011 HSLAS GR 45. The individual illustrations show two, three and four holes with lengths 3-1/2 in (P1065), 5-3/8 in (P1066), 7-1/4 in (P1067). This is a different catalog source/printed pagination from ChannelStrut's secondary citation to General Engineering Catalog No. 17 page 90; do not conflate editions.

The exact longitudinal arithmetic checks all three parts: **length = 2 × (13/16 in) + (hole count − 1) × (1-7/8 in)**. See `etl/fittings/flat_plate_reference.json` for the sourced family rules, and `src/strut_catalog_etl/flat_plate_reference.py` for the explicit, **provisional** CAD geometry derivation. It does not edit release seed or generated snapshots.

Important reservations: the plate-wide hole centerline is visually indicated but not dimensioned, and corner radius is unpublished. The caller must explicitly opt into the transverse-centerline inference; the resulting record is marked `release_eligible: false` regardless of validity. Tolerance and actual steel grade/variant material selection remain unresolved. The catalog offers alternative conditional thicknesses—not an unconditional 1/4 in thickness for every P1065.

The reference JSON was transcribed from the provided manufacturer catalog; the actual PDF is **not committed** to this repository, so its physical checksum/revision should be recorded upon approved acquisition if the repo's source policy later permits. The ChannelStrut reference is secondary corroboration, not the source of authoritative dimensions.
