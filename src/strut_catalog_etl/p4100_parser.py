"""Extract and normalize the P4100 submittal using shared channel parsing."""
from __future__ import annotations

from pathlib import Path

from .channel_submittal import page_text, parse_finish_codes, parse_identity_fields, parse_standard_lengths
from .pdf_source import build_raw_pdf_record


def inspect_p4100_raw(raw: dict) -> dict:
    """Return the reusable fields parsed from a raw P4100 submittal record.

    This intentionally stops before fabricating engineering properties. It is the
    anti-overfitting check for the shared channel parser established with P1000.
    """
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


def extract_p4100_pdf(path: Path) -> tuple[dict, dict]:
    """Extract P4100 and return ``(raw, parsed_fields)`` for parser comparison."""
    raw = build_raw_pdf_record(
        Path(path),
        source_id="P4100_SUBMITTAL",
        title="P4100 Submittal",
        record_id="P4100",
        pages_used=[1, 2],
    )
    return raw, inspect_p4100_raw(raw)
