"""Parse section-property tables from extracted Unistrut submittal text.

This module keeps table parsing separate from load-table parsing. It accepts a
compact text representation of the "Elements of Section" table and returns only
values explicitly proven by the source text.
"""
from __future__ import annotations

import re

from .engineering_sections import build_section_properties


def _normalize(text: str) -> str:
    text = text.replace("²", "2").replace("⁴", "4")
    return re.sub(r"\s+", " ", text).strip()


def _metric_number_after_customary(text: str, customary_value: float, unit: str) -> float | None:
    pattern = re.compile(
        rf"{re.escape(str(customary_value))}\s*in{unit}\s*\(\s*(?P<metric>\d+(?:\.\d+)?)\s*cm{unit}\s*\)",
        re.IGNORECASE,
    )
    match = pattern.search(text)
    return float(match.group("metric")) if match else None


def _pair_for_row(text: str, row_label: str, customary_unit: str, metric_unit: str) -> tuple[dict, dict] | None:
    pattern = re.compile(
        rf"{row_label}\s*"
        rf"(?P<x>\d+(?:\.\d+)?)\s*in{customary_unit}\s*\(\s*(?P<xm>\d+(?:\.\d+)?)\s*cm{metric_unit}\s*\)\s*"
        rf"(?P<y>\d+(?:\.\d+)?)\s*in{customary_unit}\s*\(\s*(?P<ym>\d+(?:\.\d+)?)\s*cm{metric_unit}\s*\)",
        re.IGNORECASE,
    )
    match = pattern.search(text)
    if not match:
        return None
    if customary_unit == "4":
        return (
            {"in4": float(match.group("x")), "cm4": float(match.group("xm"))},
            {"in4": float(match.group("y")), "cm4": float(match.group("ym"))},
        )
    if customary_unit == "3":
        return (
            {"in3": float(match.group("x")), "cm3": float(match.group("xm"))},
            {"in3": float(match.group("y")), "cm3": float(match.group("ym"))},
        )
    raise ValueError(f"unsupported section row unit in^{customary_unit}")


def parse_section_properties_text(text: str) -> dict:
    """Parse an Atkore/Unistrut ``Elements of Section`` table.

    The current submittals label the two table columns ``Axis 1-1`` and
    ``Axis 2-2`` rather than using x/y symbols. The normalized mapping is:
    Axis 1-1 -> x properties and Axis 2-2 -> y properties.

    Both US customary and metric values are retained where the source table
    explicitly provides them.
    """
    compact = _normalize(text)
    if not re.search(r"Elements\s+of\s+Section", compact, re.IGNORECASE):
        raise ValueError("section-property table marker 'Elements of Section' not found")

    values: dict[str, dict] = {}

    area_match = re.search(
        r"Area\s+of\s+Section\s+(?P<area>\d+(?:\.\d+)?)\s*in2\s*\(\s*(?P<metric>\d+(?:\.\d+)?)\s*cm2\s*\)",
        compact,
        re.IGNORECASE,
    )
    if area_match:
        values["area"] = {
            "in2": float(area_match.group("area")),
            "cm2": float(area_match.group("metric")),
        }

    inertia = _pair_for_row(compact, r"Moment\s+of\s+Inertia\s*\(I\)", "4", "4")
    if inertia:
        values["ix"], values["iy"] = inertia

    modulus = _pair_for_row(compact, r"Section\s+Modulus\s*\(S\)", "3", "3")
    if modulus:
        values["sx"], values["sy"] = modulus

    radius_match = re.search(
        r"Radius\s+of\s+Gyration\s*\(r\)\s*"
        r"(?P<x>\d+(?:\.\d+)?)\s*in\s*\(\s*(?P<xm>\d+(?:\.\d+)?)\s*cm\s*\)\s*"
        r"(?P<y>\d+(?:\.\d+)?)\s*in\s*\(\s*(?P<ym>\d+(?:\.\d+)?)\s*cm\s*\)",
        compact,
        re.IGNORECASE,
    )
    if radius_match:
        values["rx"] = {
            "in": float(radius_match.group("x")),
            "cm": float(radius_match.group("xm")),
        }
        values["ry"] = {
            "in": float(radius_match.group("y")),
            "cm": float(radius_match.group("ym")),
        }

    if not values:
        raise ValueError("no section properties could be parsed from table text")
    return build_section_properties(**values)
