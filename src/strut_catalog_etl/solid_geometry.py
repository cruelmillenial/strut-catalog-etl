"""Reviewed solid-channel geometry contract for FreeCAD-facing normalization."""
from __future__ import annotations

import json
from pathlib import Path


DEFAULT_PATH = Path("catalog/reviewed/unistrut_ohio/solid_geometry.json")
_REQUIRED_KEYS = ("kind", "width", "height", "thickness", "lip_return", "inside_bend_radius")


def load_solid_geometry(path: Path = DEFAULT_PATH) -> dict:
    """Load reviewed solid-channel geometry records keyed by profile id."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("unsupported solid geometry schema_version")
    profiles = data.get("profiles")
    if not isinstance(profiles, dict):
        raise ValueError("solid geometry profiles must be an object")
    for profile_id, record in profiles.items():
        missing = [key for key in _REQUIRED_KEYS if key not in record]
        if missing:
            raise ValueError(f"{profile_id} missing solid geometry keys: {', '.join(missing)}")
    return profiles


def solid_geometry_for(profile_id: str, path: Path = DEFAULT_PATH) -> dict:
    profiles = load_solid_geometry(path)
    try:
        return profiles[profile_id]
    except KeyError as exc:
        raise KeyError(f"no reviewed solid geometry for {profile_id}") from exc


def geometry_ready_for_accurate_solid(profile_id: str, path: Path = DEFAULT_PATH) -> tuple[bool, list[str]]:
    """Return whether all dimensions required for an accurate solid are sourced."""
    record = solid_geometry_for(profile_id, path)
    missing: list[str] = []
    for key in ("thickness", "lip_return", "inside_bend_radius"):
        value = record[key]
        if value.get("in") is None or value.get("mm") is None:
            missing.append(key)
    return (not missing, missing)
