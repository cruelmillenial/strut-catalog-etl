"""Validation and normalization contract for planar, round-hole fitting variants.

This module describes geometry data only. It does not infer dimensions
from drawing proportions or declare a manufacturer's SKU verified.
"""
from __future__ import annotations

import math
from typing import Any


def _positive(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric")
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise ValueError(f"{field} must be finite and positive")
    return number


def validate_flat_plate(spec: dict[str, Any]) -> dict[str, Any]:
    """Validate a flat rectangular plate with explicitly located round holes.

    Coordinate frame: origin at a plate corner; x along length, y along width;
    units millimeters. Catalog authenticity is NOT implied by passing this check.
    """
    if not isinstance(spec, dict):
        raise ValueError("flat plate specification must be an object")
    if spec.get("family") != "flat_splice_plate":
        raise ValueError("family must equal flat_splice_plate")
    length = _positive(spec.get("length_mm"), "length_mm")
    width = _positive(spec.get("width_mm"), "width_mm")
    thickness = _positive(spec.get("thickness_mm"), "thickness_mm")
    holes = spec.get("holes")
    if not isinstance(holes, list) or not holes:
        raise ValueError("holes must be a nonempty list")
    checked: list[tuple[float, float, float]] = []
    for index, hole in enumerate(holes):
        if not isinstance(hole, dict) or hole.get("shape") != "round":
            raise ValueError(f"holes[{index}].shape must equal round")
        x = _positive(hole.get("x_mm"), f"holes[{index}].x_mm")
        y = _positive(hole.get("y_mm"), f"holes[{index}].y_mm")
        diameter = _positive(hole.get("diameter_mm"), f"holes[{index}].diameter_mm")
        radius = diameter / 2
        if x - radius <= 0 or x + radius >= length or y - radius <= 0 or y + radius >= width:
            raise ValueError(f"holes[{index}] does not fit strictly inside plate boundary")
        for prev_x, prev_y, prev_radius in checked:
            if math.hypot(x - prev_x, y - prev_y) <= radius + prev_radius:
                raise ValueError(f"holes[{index}] overlaps another hole")
        checked.append((x, y, radius))
    return spec
