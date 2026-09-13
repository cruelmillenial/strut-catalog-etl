"""Reviewed solid-channel geometry contract for FreeCAD-facing normalization."""
from __future__ import annotations

import json
from pathlib import Path


DEFAULT_PATH = Path("catalog/reviewed/unistrut_ohio/solid_geometry.json")
_REQUIRED_KEYS = ("kind", "width", "height", "thickness", "lip_return", "inside_bend_radius")
_SOURCE_REQUIRED_KEYS = ("thickness", "lip_return")


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


def source_geometry_complete(profile_id: str, path: Path = DEFAULT_PATH) -> tuple[bool, list[str]]:
    """Return whether all manufacturer/source-required section dimensions are present.

    Bend radius is intentionally excluded. The reviewed Unistrut sources do not
    specify it, so the generator must supply an explicit modeling policy rather
    than treating an assumed radius as manufacturer data.
    """
    record = solid_geometry_for(profile_id, path)
    missing: list[str] = []
    for key in _SOURCE_REQUIRED_KEYS:
        value = record[key]
        if value.get("in") is None or value.get("mm") is None:
            missing.append(key)
    return (not missing, missing)


def model_geometry_ready(
    profile_id: str,
    *,
    bend_policy_available: bool,
    path: Path = DEFAULT_PATH,
) -> tuple[bool, list[str]]:
    """Return whether FreeCAD has enough information to build the MVP solid.

    Source geometry must be complete, and the generator must explicitly provide
    a bend-radius policy. The policy is deliberately kept outside the reviewed
    manufacturer data because the reviewed sources do not specify bend radius.
    """
    ready, missing = source_geometry_complete(profile_id, path)
    if not bend_policy_available:
        missing = [*missing, "bend_policy"]
    return (ready and bend_policy_available, missing)


def geometry_ready_for_accurate_solid(profile_id: str, path: Path = DEFAULT_PATH) -> tuple[bool, list[str]]:
    """Backward-compatible strict provenance check.

    This retains the old meaning: every geometric dimension, including bend
    radius, must be explicitly present in the reviewed source record.
    """
    record = solid_geometry_for(profile_id, path)
    missing: list[str] = []
    for key in ("thickness", "lip_return", "inside_bend_radius"):
        value = record[key]
        if value.get("in") is None or value.get("mm") is None:
            missing.append(key)
    return (not missing, missing)
