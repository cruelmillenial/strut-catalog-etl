"""Shared schema helpers for channel engineering section properties.

This module intentionally defines the normalized contract before table extraction.
Values are populated only when a parser proves them from source text/tables.
"""
from __future__ import annotations

SECTION_PROPERTY_KEYS = (
    "area",
    "ix",
    "iy",
    "sx",
    "sy",
    "rx",
    "ry",
)


def empty_section_properties() -> dict:
    """Return the canonical placeholder shape for deferred section properties."""
    return {key: None for key in SECTION_PROPERTY_KEYS}


def build_section_properties(**values: dict) -> dict:
    """Build a section-property mapping, rejecting unknown engineering keys.

    The parser can provide any subset of the canonical keys. Missing values remain
    absent rather than being silently synthesized.
    """
    unknown = sorted(set(values) - set(SECTION_PROPERTY_KEYS))
    if unknown:
        raise ValueError(f"unknown section property keys: {', '.join(unknown)}")
    return {key: values[key] for key in SECTION_PROPERTY_KEYS if key in values}
