"""Narrow parser/normalizer for the reviewed P1000 submittal fixture.

This first pass is intentionally conservative: it normalizes only the fields
already represented by the golden P1000 fixture. PDF text extraction and
source acquisition remain separate concerns.
"""
from __future__ import annotations

from copy import deepcopy


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
                "source_file": "P1000_submittal.pdf",
                "source_sha256": "0" * 64,
                "source_pages": [1, 2],
                "table": "P1000 submittal",
                "notes": [
                    "Golden fixture manually reconciled to the canonical normalized profile schema.",
                    "Source digest and exact source filename remain placeholders until the submittal acquisition step is wired in.",
                    "Engineering load tables and additional section properties remain deferred to a later extraction pass.",
                ],
            },
        }
    ],
}


def normalize_p1000_submittal(*, source_file: str = "P1000_submittal.pdf", source_sha256: str | None = None) -> dict:
    """Return the canonical normalized P1000 record for the reviewed submittal.

    The current implementation establishes the parser contract before wiring in
    PDF text extraction. Callers may supply acquired source provenance so the
    generated record can later be compared directly with the golden fixture.
    """

    data = deepcopy(_P1000_TEMPLATE)
    provenance = data["profiles"][0]["provenance"]
    provenance["source_file"] = source_file
    if source_sha256 is not None:
        provenance["source_sha256"] = source_sha256
    return data
