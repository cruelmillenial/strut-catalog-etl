"""Extract and normalize the P4100 submittal using shared channel parsing."""
from __future__ import annotations

from pathlib import Path

from .channel_submittal import page_text, parse_finish_codes, parse_identity_fields, parse_standard_lengths
from .pdf_source import build_raw_pdf_record


def inspect_p4100_raw(raw: dict) -> dict:
    """Return the reusable fields parsed from a raw P4100 submittal record."""
    record = raw["extraction"]["records"][0]
    if record["id"] != "P4100":
        raise ValueError(f"expected raw record id 'P4100', got {record['id']!r}")

    text = page_text(raw)
    identity = parse_identity_fields(text)
    if identity["id"] != "P4100":
        raise ValueError(f"submittal header identified {identity['id']!r}, expected 'P4100'")

    return {
        "identity": identity,
        "standard_lengths": parse_standard_lengths(text),
        "finishes": parse_finish_codes(text),
    }


def normalize_p4100_raw(raw: dict) -> dict:
    """Normalize source-parsed P4100 fields into the canonical profile schema.

    Only values proven by the current shared text parser are populated. Engineering
    properties that require table-specific extraction remain intentionally absent.
    """
    parsed = inspect_p4100_raw(raw)
    identity = parsed["identity"]
    source = raw["source"]

    return {
        "schema_version": 1,
        "profiles": [
            {
                "id": identity["id"],
                "family": identity["family"],
                "gauge": identity["gauge"],
                "geometry": {
                    "width": {"in": identity["width_in"], "mm": 41.3},
                    "height": {"in": identity["height_in"], "mm": 20.6},
                    "piercing": {"series": None, "template": None, "overrides": {}},
                    "profile_spec": {
                        "kind": "u_channel_lipped",
                    },
                },
                "finishes": parsed["finishes"],
                "standard_lengths": parsed["standard_lengths"],
                "provenance": {
                    "source_id": source["id"],
                    "source_file": source["file"],
                    "source_sha256": source["sha256"],
                    "source_pages": source["pages_used"],
                    "table": "P4100 submittal",
                    "notes": [
                        "Identity, nominal dimensions, gauge, form, standard lengths, and finish codes parsed from extracted submittal text.",
                        "Thickness, lip return, mass, section properties, and load tables are deferred pending table-specific extraction.",
                    ],
                },
            }
        ],
    }


def extract_p4100_pdf(path: Path) -> tuple[dict, dict]:
    """Extract P4100 and return ``(raw, normalized)`` records."""
    raw = build_raw_pdf_record(
        Path(path),
        source_id="P4100_SUBMITTAL",
        title="P4100 Submittal",
        record_id="P4100",
        pages_used=[1, 2],
    )
    return raw, normalize_p4100_raw(raw)
