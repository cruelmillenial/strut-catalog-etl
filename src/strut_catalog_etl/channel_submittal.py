"""Shared parsing helpers for Unistrut channel submittal text."""
from __future__ import annotations

from fractions import Fraction
import re

# Atkore/Unistrut submittals are not perfectly uniform. P1000 places the form
# after "Channel" ("12 Gauge Channel, Solid") while P4100 places it before the
# next product token ("14 Gauge, Solid P4100"). Keep this tolerant while still
# requiring part number, two dimensions, and gauge.
_HEADER_RE = re.compile(
    r"(?P<id>P\d+)\s*[-–—:]?\s*"
    r"(?P<width>\d+(?:[-\s]\d+/\d+)?|\d+/\d+)\s*(?:\"|in\.?|inch(?:es)?)\s*"
    r"[x×X]\s*"
    r"(?P<height>\d+(?:[-\s]\d+/\d+)?|\d+/\d+)\s*(?:\"|in\.?|inch(?:es)?)\s*"
    r"[,;:]?\s*(?P<gauge>\d+)\s*(?:ga\.?|gauge)\b"
    r"(?:\s*[,;:-]?\s*(?P<form_before>Solid|Slotted|Punched|Knockout|KO))?",
    re.IGNORECASE | re.DOTALL,
)
_CHANNEL_FORM_RE = re.compile(
    r"\bChannel\b\s*[,;:-]?\s*(?P<form>Solid|Slotted|Punched|Knockout|KO)\b",
    re.IGNORECASE,
)
# Anchor on the nominal source label ("10 feet:", "20 feet:") and then capture
# the first meter value that follows it. The bounded lookahead prevents the
# later tolerance value "(3 mm)" from being mistaken for the metric length.
_LENGTH_RE = re.compile(
    r"(?P<ft>\d+)\s*(?:feet|foot|ft\.?)\s*:"
    r"(?:(?!\b\d+\s*(?:feet|foot|ft\.?)\s*:).){0,180}?"
    r"\(\s*(?P<m>\d+(?:\.\d+)?)\s*m\s*\)",
    re.IGNORECASE | re.DOTALL,
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

    form = match.group("form_before")
    if form is None:
        # P1000-style layout: the form follows "Channel" after the gauge.
        # Search only a short tail after the matched header so a later mention
        # elsewhere in the document cannot overwrite the product header.
        tail = text[match.end():match.end() + 120]
        channel_form = _CHANNEL_FORM_RE.search(tail)
        if channel_form:
            form = channel_form.group("form")

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
        compact = re.sub(r"\s+", " ", text)
        marker = re.search(r"Standard Lengths|Special Lengths|\b10\s*(?:feet|ft\.?|'|’)\b", compact, re.IGNORECASE)
        if marker:
            start = max(0, marker.start() - 120)
            excerpt = compact[start:start + 520]
            raise ValueError(
                "could not parse standard lengths from extracted PDF text; "
                f"near length section: {excerpt!r}"
            )
        raise ValueError("could not parse standard lengths from extracted PDF text")
    return {
        "ft": [float(match.group("ft")) for match in matches],
        "m": [float(match.group("m")) for match in matches],
    }


def parse_finish_codes(text: str) -> list[str]:
    return [code for code in _FINISH_CODES if re.search(rf"\({code}\)", text)]
