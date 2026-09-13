"""Load manually reviewed section-property tables for submittals whose PDF text omits them."""
from __future__ import annotations

import json
from pathlib import Path

from .engineering_sections import build_section_properties


DEFAULT_PATH = Path("catalog/reviewed/unistrut_ohio/section_properties.json")


def load_reviewed_section_properties(profile_id: str, path: Path = DEFAULT_PATH) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    try:
        values = data["profiles"][profile_id]
    except KeyError as exc:
        raise KeyError(f"no reviewed section properties for {profile_id}") from exc
    return build_section_properties(**values)
