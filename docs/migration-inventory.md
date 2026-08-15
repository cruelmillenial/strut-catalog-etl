# UnistrutWB data migration inventory

## Migrated into this repository

- Source identity and SHA-256 for `unistrut-general-catalog.pdf`.
- Existing seed datastore records for P1000, P4100, finishes, and the generic fitting placeholder.
- Hole-series mapping notes and provisional beam-capacity factors.
- Catalog interpretation notes concerning dimensions and bolt torque.
- A deterministic builder that converts list-oriented seed data into the indexed snapshot shape currently expected by UnistrutWB's loader.

## Deliberately not migrated

The following remain application concerns and stay in `UnistrutWB`:

- FreeCAD imports and object creation.
- Channel and fitting geometry builders.
- commands, dialogs, workbench registration, and icons.
- BOM aggregation from FreeCAD document objects.
- runtime path discovery and snapshot loading.

## Source files requiring later classification

| Existing asset | Classification | Planned disposition |
|---|---|---|
| `unistrut-general-catalog.pdf` | copyrighted vendor source | retain outside Git until redistribution policy is settled |
| `unistrut.json` | mixed seed/extracted datastore | imported as `etl/seed/unistrut_seed.json` |
| `mapping_hole_series.json` | provisional normalization mapping | imported as unverified seed |
| `notes_derating.json` | extracted interpretation notes | imported as unverified seed |
| `loader.py` | downstream consumer adapter | remains in UnistrutWB; later simplify to one snapshot contract |
| `profiles.py` | CAD geometry implementation | remains in UnistrutWB |
| `fittings.py` | CAD geometry implementation | remains in UnistrutWB |
| `bom.py` | application export logic | remains in UnistrutWB |
| `smoke_profiles.FC.py` | FreeCAD integration test | remains in UnistrutWB |

## Verification rule

No seed record is authoritative merely because it has been migrated. A record may be promoted to generated release data only after:

1. page or table provenance is populated;
2. units and conversions are checked;
3. placeholders and `null` values are explicitly accepted or replaced;
4. schema validation passes;
5. deterministic regeneration produces no unexplained diff.

## Immediate next milestone

Produce a schema-validated P1000/P4100 snapshot with page-level provenance, then have UnistrutWB consume that snapshot without changing its geometry behavior.
