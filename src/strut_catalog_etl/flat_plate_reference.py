"""Derive provisional flat-plate reference geometry from catalog family rules.

Only dimensions with an established source or explicitly declared inferences
are represented. This is NOT a manufacturer-exact released fitting model.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Any

from strut_catalog_etl.fitting_geometry import validate_flat_plate


def inch_fraction(value: str) -> Fraction:
    """Parse an integer, fraction, or mixed number in inches exactly."""
    parts = value.strip().split()
    if not 1 <= len(parts) <= 2:
        raise ValueError("invalid inch fraction")
    return sum((Fraction(part) for part in parts), Fraction(0))


def derive_flat_plate_reference(
    reference: dict[str, Any],
    part_id: str,
    thickness_option: int = 0,
    *,
    infer_transverse_centerline: bool = False,
) -> dict[str, Any]:
    """Construct explicit-hole geometry; requires opting into inferred Y centers.

    Returns a geometry candidate with provenance and assumptions. It is not a
    promotion operation and must not be used as manufacturer certified data.
    """
    if not infer_transverse_centerline:
        raise ValueError("transverse hole centerline is undimensioned; opt into inference")
    rule = reference["standard_dimensions"]
    part = next((p for p in reference["parts"] if p["id"] == part_id), None)
    if part is None:
        raise ValueError("unknown flat-plate part")
    thickness_options = rule["thickness_options"]
    if isinstance(thickness_option, bool) or not isinstance(thickness_option, int):
        raise ValueError("thickness_option must be an integer index")
    selected = thickness_options[thickness_option]
    end = inch_fraction(rule["end_center_in"])
    pitch = inch_fraction(rule["pitch_in"])
    length = inch_fraction(part["length_in"])
    width = inch_fraction(rule["width_in"])
    dia = inch_fraction(rule["hole_diameter_in"])
    count = part["hole_count"]
    if count < 1 or 2 * end + (count - 1) * pitch != length:
        raise ValueError("part length contradicts family hole pattern")
    to_mm = lambda v: float(v * Fraction(254, 10))
    spec = {
        "family": "flat_splice_plate",
        "length_mm": to_mm(length),
        "width_mm": to_mm(width),
        "thickness_mm": to_mm(inch_fraction(selected["thickness_in"])),
        "holes": [
            {
                "shape": "round",
                "x_mm": to_mm(end + i * pitch),
                "y_mm": to_mm(width / 2),
                "diameter_mm": to_mm(dia),
            }
            for i in range(count)
        ],
    }
    validate_flat_plate(spec)
    return {
        "id": part_id,
        "status": "provisional_reference_geometry",
        "source": reference["source"],
        "geometry": spec,
        "material_requirement": selected["steel_requirement"],
        "provenance": {
            "length_and_hole_count": "manufacturer_part_drawing",
            "width_hole_diameter_pitch_end_offset": "manufacturer_family_note",
            "thickness": "manufacturer_family_note_conditional_on_material",
            "longitudinal_centers": "derived_exact_from_family_pitch_and_offset",
            "transverse_centers": "inferred_from_undimensioned_illustration",
            "corner_radius": "unresolved",
        },
        "release_eligible": False,
    }
