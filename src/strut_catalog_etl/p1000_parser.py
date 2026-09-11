"""Normalize the reviewed P1000 submittal into the canonical profile schema."""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import re

from .pdf_source import build_raw_pdf_record


_P1000_TEMPLATE = {
    "schema_version": 1,
    "profiles": [
        {
            "id": "P1000",
            "family": "1-5/8 x 1-5/8",
            "gauge": 12,
            "geometry": {
                "width": {"in": 1.625, "mm": 41.3},
                "height": {"in": 1.625, "mm": 41.3},
                "thickness": {"in": 0.105, "mm": 2.7},
                "piercing": {"series": None, "template": None, "overrides": {}},
                "profile_spec": {
                    "kind": "u_channel_lipped",
                    "t": {"in": 0.105, "mm": 2.7},
                    "lip_return": {"in": 0.375, "mm": 9.5},
                },
            },
            "mass": {"lb_per_ft": 1.9, "kg_per_m": 2.8},
            "finishes": ["PL", "GR", "HG", "PG"],
            "standard_lengths": {"ft": [10.0, 20.0], "m": [3.05, 6.1]},
            "properties": {
                "section": {
                    "allowable_moment": {"in_lb": 5080, "N_m": 570}
                }
            },
            "provenance": {
                "source_id": "P1000_SUBMITTAL",
                "source_file": "P1000_Submittal.pdf",
                "source_sha256": "0" * 64,
                "source_pages": [1, 2],
                "table": "P1000 submittal",
                "notes": [
                    "Golden fixture manually reconciled to the canonical normalized profile schema.",
                    "Engineering load tables and additional section properties remain deferred to a later extraction pass.",
                ],
            },
        }
    ],
}

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


def _fractional_inches(value: str) -> float:
    if "-" in value:
        whole, frac = value.split("-", 1)
        return float(int(whole) + Fraction(frac))
    return float(Fraction(value))


def _page_text(raw: dict) -> str:
    return "\n".join(page.get("text", "") for page in raw["extraction"]["records"][0]["pages"])


def _parse_identity_fields(text: str) -> dict:
    match = _HEADER_RE.search(text)
    if not match:
        raise ValueError("could not parse P1000 identity header from extracted PDF text")

    width = _fractional_inches(match.group("width"))
    height = _fractional_inches(match.group("height"))
    return {
        "id": match.group("id").upper(),
        "family": f"{match.group('width')} x {match.group('height')}",
        "gauge": int(match.group("gauge")),
        "width_in": width,
        "height_in": height,
        "form": match.group("form").lower(),
    }


def _parse_standard_lengths(text: str) -> dict:
    matches = list(_LENGTH_RE.finditer(text))
    if not matches:
        raise ValueError("could not parse standard lengths from extracted PDF text")
    return {
        "ft": [float(match.group("ft")) for match in matches],
        "m": [float(match.group("m")) for match in matches],
    }


def _parse_finish_codes(text: str) -> list[str]:
    return [code for code in _FINISH_CODES if re.search(rf"\({code}\)", text)]


def normalize_p1000_raw(raw: dict) -> dict:
    """Normalize a raw P1000 PDF record into the canonical profile shape.

    Identity, nominal dimensions, gauge, standard lengths, and advertised finish
    codes are parsed from the extracted source text. Engineering values that need
    table-specific extraction remain reviewed constants for now.
    """
    source = raw["source"]
    record = raw["extraction"]["records"][0]
    if record["id"] != "P1000":
        raise ValueError(f"expected raw record id 'P1000', got {record['id']!r}")

    text = _page_text(raw)
    identity = _parse_identity_fields(text)
    lengths = _parse_standard_lengths(text)
    finishes = _parse_finish_codes(text)

    data = deepcopy(_P1000_TEMPLATE)
    profile = data["profiles"][0]
    profile["id"] = identity["id"]
    profile["family"] = identity["family"]
    profile["gauge"] = identity["gauge"]
    profile["geometry"]["width"]["in"] = identity["width_in"]
    profile["geometry"]["height"]["in"] = identity["height_in"]
    profile["standard_lengths"] = lengths
    if finishes:
        profile["finishes"] = finishes

    provenance = profile["provenance"]
    provenance["source_id"] = source["id"]
    provenance["source_file"] = source["file"]
    provenance["source_sha256"] = source["sha256"]
    provenance["source_pages"] = source["pages_used"]
    provenance["notes"] = [
        "Identity, nominal dimensions, gauge, standard lengths, and finish codes parsed from extracted submittal text.",
        "Thickness, lip return, mass, allowable moment, and additional engineering table values remain reviewed constants pending table extraction.",
    ]
    return data


def normalize_p1000_pdf(path: Path) -> tuple[dict, dict]:
    """Extract the local P1000 PDF and return ``(raw, normalized)`` records."""
    raw = build_raw_pdf_record(
        Path(path),
        source_id="P1000_SUBMITTAL",
        title="P1000 Submittal",
        record_id="P1000",
        pages_used=[1, 2],
    )
    return raw, normalize_p1000_raw(raw)


def normalize_p1000_submittal(*, source_file: str = "P1000_Submittal.pdf", source_sha256: str | None = None) -> dict:
    """Backward-compatible helper retained for existing tests/callers."""
    data = deepcopy(_P1000_TEMPLATE)
    provenance = data["profiles"][0]["provenance"]
    provenance["source_file"] = source_file
    if source_sha256 is not None:
        provenance["source_sha256"] = source_sha256
    return data
