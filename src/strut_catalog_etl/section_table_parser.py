"""Parse section-property tables from extracted Unistrut submittal text.

This module keeps table parsing separate from load-table parsing. It accepts a
compact text representation of the "Elements of Section" table and returns only
values explicitly proven by the source text.
"""
from __future__ import annotations

import re

from .engineering_sections import build_section_properties


_LABELS = {
    "area": ("area",),
    "ix": ("ix", "i x"),
    "iy": ("iy", "i y"),
    "sx": ("sx", "s x"),
    "sy": ("sy", "s y"),
    "rx": ("rx", "r x"),
    "ry": ("ry", "r y"),
}


def _normalize(text: str) -> str:
    text = text.replace("²", "2").replace("⁴", "4")
    return re.sub(r"\s+", " ", text).strip()


def _first_number_after_label(text: str, labels: tuple[str, ...]) -> float | None:
    for label in labels:
        pattern = re.compile(
            rf"\b{re.escape(label)}\b\s*[:=]?\s*(?P<value>\d+(?:\.\d+)?)",
            re.IGNORECASE,
        )
        match = pattern.search(text)
        if match:
            return float(match.group("value"))
    return None


def parse_section_properties_text(text: str) -> dict:
    """Parse source-declared US customary section properties from table text.

    Expected source labels are Area, Ix, Iy, Sx, Sy, rx, and ry. This first pass
    intentionally captures only the source-side customary values; metric values
    can be added later once their table ordering/labels are proven independently.
    """
    compact = _normalize(text)
    if not re.search(r"Elements\s+of\s+Section", compact, re.IGNORECASE):
        raise ValueError("section-property table marker 'Elements of Section' not found")

    values: dict[str, dict] = {}
    for key, labels in _LABELS.items():
        value = _first_number_after_label(compact, labels)
        if value is None:
            continue
        if key == "area":
            values[key] = {"in2": value}
        elif key in {"ix", "iy"}:
            values[key] = {"in4": value}
        elif key in {"sx", "sy"}:
            values[key] = {"in3": value}
        else:
            values[key] = {"in": value}

    if not values:
        raise ValueError("no section properties could be parsed from table text")
    return build_section_properties(**values)
