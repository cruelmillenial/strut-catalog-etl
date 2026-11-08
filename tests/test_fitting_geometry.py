import pytest

from strut_catalog_etl.fitting_geometry import validate_flat_plate


def fixture_plate():
    # Synthetic geometry for contract testing, NOT a manufacturer-derived SKU.
    return {
        "family": "flat_splice_plate",
        "length_mm": 100.0,
        "width_mm": 40.0,
        "thickness_mm": 3.0,
        "holes": [
            {"shape": "round", "x_mm": 25.0, "y_mm": 20.0, "diameter_mm": 12.0},
            {"shape": "round", "x_mm": 75.0, "y_mm": 20.0, "diameter_mm": 12.0},
        ],
    }


def test_flat_plate_accepts_complete_synthetic_geometry():
    spec = fixture_plate()
    assert validate_flat_plate(spec) == spec


@pytest.mark.parametrize("field", ["length_mm", "width_mm", "thickness_mm"])
def test_flat_plate_rejects_invalid_body_dimensions(field):
    spec = fixture_plate()
    spec[field] = None
    with pytest.raises(ValueError, match=field):
        validate_flat_plate(spec)


def test_flat_plate_rejects_hole_outside_boundary():
    spec = fixture_plate()
    spec["holes"][0]["x_mm"] = 5.0
    with pytest.raises(ValueError, match="boundary"):
        validate_flat_plate(spec)


def test_flat_plate_rejects_overlapping_holes():
    spec = fixture_plate()
    spec["holes"][1]["x_mm"] = 34.0
    with pytest.raises(ValueError, match="overlaps"):
        validate_flat_plate(spec)


def test_flat_plate_requires_explicit_hole_diameter():
    spec = fixture_plate()
    spec["holes"][0].pop("diameter_mm")
    with pytest.raises(ValueError, match="diameter_mm"):
        validate_flat_plate(spec)


def test_flat_plate_rejects_slots_until_slot_contract_exists():
    spec = fixture_plate()
    spec["holes"][0]["shape"] = "slot"
    with pytest.raises(ValueError, match="shape"):
        validate_flat_plate(spec)
