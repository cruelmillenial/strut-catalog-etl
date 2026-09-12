"""Shared parsing helpers for Unistrut channel submittal text."""
from __future__ import annotations

from fractions import Fraction
import re

# Atkore/Unistrut submittals are not perfectly uniform.  P1000 currently emits
# e.g. ``P1000 - 1-5/8\" x 1-5/8\", 12 Gauge Channel, Solid`` while other
# families may omit punctuation, wrap differently, or spell the form on a
# following line.  Keep this deliberately tolerant while still requiring the
# identifying part number, two dimensions, gauge, and the word "Channel".
_HEADER_RE = re.compile(
    r"(?P<id>P\d+)\s*[-–—:]?\s*"
    r"(?P<width>\d+(?:[-\s]\d+/\d+)?|\d+/\d+)\s*(?:\"|in\.?|inch(?:es)?)\s*"
    r"[x×X]\s*"
    r"(?P<height>\d+(?:[-\s]\d+/\d+)?|\d+/\d+)\s*(?:\"|in\.?|inch(?:es)?)\s*"
    r"[,;:]?\s*(?P<gauge>\d+)\s*(?:ga\.?|gauge)\b"
    r"(?:(?!P\d+).){0,120}?\bChannel\b"
    r"(?:\s*[,;:-]?\s*(?P<form>Solid|Slotted|Punched|Knockout|KO))?",
    re.IGNORECASE | re.DOTALL,
)
_LENGTH_RE = re.compile(
    r"(?P<ft>\d+)\s*feet\s*:.*?\((?P<m>\d+(?:\.\d+)?)m\)",
    re.IGNORECASE,
)
_FINISH_CODES = ("PG", "DF", "HG", "GR", "ZD", "PL", "SS", "ST", "EA")


def fractional_inches(value: str) -> float:
    value = value.strip().replace(" ", "-")
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
        # Keep the failure useful: pypdf line wrapping/layout is the variable
        # here, so include a compact P-series excerpt for the next specimen.
        compact = re.sub(r"\s+", " ", text)
        marker = re.search(r"P\d+", compact, re.IGNORECASE)
        if marker:
            start = max(0, marker.start() - 80)
            excerpt = compact[start:start + 420]
            raise ValueError(
                "could not parse channel identity header from extracted PDF text; "
                f"near first P-series token: {excerpt!r}"
            )
        raise ValueError("could not parse channel identity header from extracted PDF text")

    form = match.group("form")
    return {
        "id": match.group("id").upper(),
        "family": f"{match.group('width').replace(' ', '-')} x {match.group('height').replace(' ', '-')}",
        "gauge": int(match.group("gauge")),
        "width_in": fractional_inches(match.group("width")),
        "height_in": fractional_inches(match.group("height")),
        "form": form.lower() if form else None,
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
