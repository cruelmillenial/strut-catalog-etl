import json
from pathlib import Path

import pytest

from strut_catalog_etl.flat_plate_reference import (
    derive_flat_plate_reference,
    inch_fraction,
)

REFERENCE = json.loads(
    (Path(__file__).resolve().parents[1] / "etl/fittings/flat_plate_reference.json").read_text()
)


def test_fractional_inch_parse_is_exact():
    assert inch_fraction("1 7/8") * 8 == 15
    assert inch_fraction("13/16") * 16 == 13


@pytest.mark.parametrize(
    ("part_id", "length_mm", "count"),
    [
        ("P1065", 88.9, 2),
        ("P1066", 136.525, 3),
        ("P1067", 184.15, 4),
    ],
)
def test_reference_series_positions_and_provenance(part_id, length_mm, count):
    record = derive_flat_plate_reference(
        REFERENCE, part_id, infer_transverse_centerline=True
    )
    g = record["geometry"]
    assert g["length_mm"] == pytest.approx(length_mm)
    assert g["width_mm"] == pytest.approx(41.275)
    assert g["thickness_mm"] == pytest.approx(6.35)
    assert len(g["holes"]) == count
    assert g["holes"][0]["x_mm"] == pytest.approx(20.6375)
    assert g["holes"][-1]["x_mm"] == pytest.approx(length_mm - 20.6375)
    assert g["holes"][0]["y_mm"] == pytest.approx(20.6375)
    assert g["holes"][0]["diameter_mm"] == pytest.approx(14.2875)
    assert record["release_eligible"] is False
    assert record["provenance"]["transverse_centers"].startswith("inferred")


def test_transverse_inference_must_be_explicit():
    with pytest.raises(ValueError, match="undimensioned"):
        derive_flat_plate_reference(REFERENCE, "P1065")


def test_material_grade_can_change_reference_thickness():
    result = derive_flat_plate_reference(
        REFERENCE, "P1065", thickness_option=1, infer_transverse_centerline=True
    )
    assert result["geometry"]["thickness_mm"] == pytest.approx(5.588)
    assert "HSLAS GR 45" in result["material_requirement"]


def test_length_pitch_conflict_rejected():
    altered = json.loads(json.dumps(REFERENCE))
    altered["parts"][0]["length_in"] = "4"
    with pytest.raises(ValueError, match="contradicts"):
        derive_flat_plate_reference(
            altered, "P1065", infer_transverse_centerline=True
        )


def test_reference_source_is_direct_manufacturer_catalog():
    assert REFERENCE["source"]["printed_page"] == 81
    assert REFERENCE["source"]["type"] == "manufacturer_catalog"
    assert REFERENCE["derived"]["corner_radius"].startswith("unpublished")
