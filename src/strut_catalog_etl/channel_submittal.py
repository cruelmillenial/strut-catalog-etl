"""Shared parsing helpers for Unistrut channel submittal text."""
from __future__ import annotations

from fractions import Fraction
import re

_HEADER_RE = re.compile(
    r"(?P<id>P\d+)\s*-\s*(?P<width>[\d\-/]+)\"\s*x\s*"
    r"(?P<height>[\d\-/]+)\"\s*,\s*(?P<gauge>\d+)\s*Gauge\s*"
    r"Channel\s*,\s*(?P<form>[A-Za-z]+)",
    re.IGNORECASE | re.DOTALL,
)
_LENGTH_RE = re.compile(
    r"(?P<ft>\d+)\s*feet\s*:.*?\((?P<m>\d+(?:\.\d+)?)m\)",
    re.IGNORECASE,
)
_FINISH_CODES = ("PG", "DF", "HG", "GR", "ZD", "PL", "SS", "ST", "EA")


def fractional_inches(value: str) -> float:
    if "-" in value:
        whole, frac = value.split("-", 1)
        return float(int(whole) + Fraction(frac))
    return float(Fraction(value))


def page_text(raw: dict) -> str:
    return "\n".join(
        page.get("text", "")
        for page in raw["extraction"]["records"][0]["pages"]
    )


def parse_identity_fields(text: str) -> dict:
    match = _HEADER_RE.search(text)
    if not match:
        raise ValueError("could not parse channel identity header from extracted PDF text")

    return {
        "id": match.group("id").upper(),
        "family": f"{match.group('width')} x {match.group('height')}",
        "gauge": int(match.group("gauge")),
        "width_in": fractional_inches(match.group("width")),
        "height_in": fractional_inches(match.group("height")),
        "form": match.group("form").lower(),
    }


def parse_standard_lengths(text: str) -> dict:
    matches = list(_LENGTH_RE.finditer(text))
    if not matches:
        raise ValueError("could not parse standard lengths from extracted PDF text")
    return {
        "ft": [float(match.group("ft")) for match in matches],
        "m": [float(match.group("m")) for match in matches],
    }


def parse_finish_codes(text: str) -> list[str]:
    return [code for code in _FINISH_CODES if re.search(rf"\({code}\)", text)]
