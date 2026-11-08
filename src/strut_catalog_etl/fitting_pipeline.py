"""Controlled fitting preview and release ingestion contracts.

Preview geometry is not automatically eligible for manufacturer-catalog release.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from strut_catalog_etl.fitting_geometry import validate_flat_plate
from strut_catalog_etl.flat_plate_reference import derive_flat_plate_reference

ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "etl" / "fittings" / "flat_plate_reference.json"
PREVIEW_OUTPUT = ROOT / "generated" / "preview" / "flat_plate_fittings.json"
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def validate_fitting_record(record: dict[str, Any], *, for_release: bool = False) -> None:
    """Validate the shared ETL/Workbench record, with an additional release gate."""
    if not isinstance(record, dict):
        raise ValueError("fitting record must be an object")
    if not isinstance(record.get("id"), str) or not record["id"].strip():
        raise ValueError("fitting id required")
    if not isinstance(record.get("manufacturer_part_id"), str) or not record["manufacturer_part_id"]:
        raise ValueError("manufacturer_part_id required")
    if record.get("family_id") != "flat_splice_plate":
        raise ValueError("unsupported fitting family")
    if record.get("geometry_type") != "splice_plate":
        raise ValueError("unsupported fitting geometry_type")
    if not isinstance(record.get("geometry"), dict):
        raise ValueError("geometry is required")
    validate_flat_plate(record["geometry"])
    if not SHA256.fullmatch(str(record.get("source_sha256", ""))):
        raise ValueError("source_sha256 required")
    if not isinstance(record.get("source_page"), int) or record["source_page"] < 1:
        raise ValueError("positive source_page required")
    if record.get("accuracy_class") not in {"reference_inferred", "manufacturer_nominal", "measured_sample"}:
        raise ValueError("accuracy_class required")
    if not isinstance(record.get("assumptions"), list):
        raise ValueError("assumptions list required")

    if for_release:
        if record.get("record_status") != "release_approved":
            raise ValueError("record is not release_approved")
        review = record.get("release_review")
        if not isinstance(review, dict) or review.get("decision") != "approved":
            raise ValueError("explicit approved release_review required")
        for field in ("reviewer", "review_date", "approved_scope"):
            if not isinstance(review.get(field), str) or not review[field].strip():
                raise ValueError(f"release_review.{field} required")
        if record["accuracy_class"] == "reference_inferred" and not record["assumptions"]:
            raise ValueError("inferred reference geometry must disclose assumptions")
    elif record.get("record_status") not in {"preview_only", "release_approved"}:
        raise ValueError("unknown record_status")


def build_reference_preview(reference: dict[str, Any]) -> dict[str, Any]:
    """Produce review-only catalog variants; never silently promote them."""
    results = []
    options = reference["standard_dimensions"]["thickness_options"]
    labels = ("SS33", "HSLAS45")
    if len(options) != len(labels):
        raise ValueError("reference material options changed; update variant naming")
    for part in reference["parts"]:
        for index, label in enumerate(labels):
            model = derive_flat_plate_reference(
                reference, part["id"], thickness_option=index,
                infer_transverse_centerline=True,
            )
            diameter = model["geometry"]["holes"][0]["diameter_mm"] / 25.4
            record = {
                "id": f"REF_{part['id']}_{label}",
                "manufacturer_part_id": part["id"],
                "name": f"{part['id']} flat plate — unverified reference ({label})",
                "category": "splice_plates",
                "display_group": "Reference Plates (Provisional)",
                "variant_label": f"{part['id']} / {options[index]['thickness_in']} in / {label} [REFERENCE]",
                "family_id": "flat_splice_plate",
                "geometry_type": "splice_plate",
                "geometry": model["geometry"],
                "hole_count": len(model["geometry"]["holes"]),
                "hole_diameter_options_in": [diameter],
                "default_hole_diameter_in": diameter,
                "material_requirement": model["material_requirement"],
                "record_status": "preview_only",
                "accuracy_class": "reference_inferred",
                "source_sha256": model["source"]["sha256"],
                "source_page": model["source"]["pdf_page"],
                "assumptions": [
                    "transverse centers inferred from undimensioned centerline illustration",
                    "sharp rectangular corners approximated; manufacturer corner radius unknown",
                    "steel grade is a selectable catalog condition, not confirmed for a specific shipped SKU",
                ],
                "provenance": model["provenance"],
                "placement": {
                    "supported_modes": ["face_mount"],
                    "allowed_face_classes": ["open_face"],
                    "slot_policy": "nearest_slot_center",
                },
                "mate_frames": [],
            }
            validate_fitting_record(record)
            results.append(record)
    return {
        "schema_version": 1,
        "catalog_status": "preview_only",
        "source_id": "unistrut-flat-plates-catalog-page-81",
        "fittings": sorted(results, key=lambda x: x["id"]),
    }


def merge_approved_fittings(seed: dict[str, Any], approved: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a new seed dict only after all proposed release records pass gates."""
    if not isinstance(approved, list):
        raise ValueError("approved fittings must be a list")
    result = dict(seed)
    existing = list(result.get("fittings", []))
    ids = {row["id"] for row in existing}
    for row in approved:
        validate_fitting_record(row, for_release=True)
        if row["id"] in ids:
            raise ValueError(f"duplicate fitting id: {row['id']}")
        ids.add(row["id"])
        existing.append(row)
    result["fittings"] = existing
    return result


def write_reference_preview(output: Path = PREVIEW_OUTPUT, reference_path: Path = REFERENCE) -> Path:
    reference = json.loads(reference_path.read_text(encoding="utf-8"))
    payload = build_reference_preview(reference)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate non-release flat-plate preview catalog")
    parser.add_argument("--reference", type=Path, default=REFERENCE)
    parser.add_argument("--output", type=Path, default=PREVIEW_OUTPUT)
    args = parser.parse_args()
    print(write_reference_preview(args.output, args.reference))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
