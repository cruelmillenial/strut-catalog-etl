"""Reviewed solid-channel geometry contract for FreeCAD-facing normalization."""
from __future__ import annotations

import json
from pathlib import Path


DEFAULT_PATH = Path("catalog/reviewed/unistrut_ohio/solid_geometry.json")
_REQUIRED_KEYS = (
    "kind",
    "width",
    "height",
    "thickness",
    "lip_return",
    "mouth_opening",
    "lip_tip_gap",
    "inside_bend_radius",
)
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
    """Return whether all source-required MVP section dimensions are present."""
    record = solid_geometry_for(profile_id, path)
    missing: list[str] = []
    for key in _SOURCE_REQUIRED_KEYS:
        value = record[key]
        if value.get("in") is None or value.get("mm") is None:
            missing.append(key)
    return (not missing, missing)


def derive_symmetric_lip_geometry(profile_id: str, path: Path = DEFAULT_PATH) -> dict:
    """Derive symmetric lip dimensions from source-backed drawing dimensions.

    This derivation is intentionally separate from manufacturer data. Under a
    symmetric-lip model:

      side_projection = (width - mouth_opening) / 2
      tip_projection  = (mouth_opening - lip_tip_gap) / 2

    If the curled lip is modeled as a semicircle whose horizontal span equals
    ``tip_projection``, the candidate nominal curl radius is
    ``tip_projection / 2``. That radius is a modeling hypothesis, not a
    manufacturer-specified bend radius.
    """
    record = solid_geometry_for(profile_id, path)
    missing = [
        key
        for key in ("width", "mouth_opening", "lip_tip_gap")
        if record[key].get("in") is None
    ]
    if missing:
        raise ValueError(
            f"{profile_id} cannot derive lip geometry; missing source dimensions: {', '.join(missing)}"
        )

    width = float(record["width"]["in"])
    opening = float(record["mouth_opening"]["in"])
    gap = float(record["lip_tip_gap"]["in"])
    side_projection = (width - opening) / 2.0
    tip_projection = (opening - gap) / 2.0
    candidate_radius = tip_projection / 2.0

    return {
        "side_projection_in": side_projection,
        "tip_projection_in": tip_projection,
        "candidate_semicircular_lip_radius_in": candidate_radius,
        "model": "symmetric_semicircular_lip",
        "status": "derived_model_hypothesis",
    }


def model_geometry_ready(
    profile_id: str,
    *,
    bend_policy_available: bool,
    path: Path = DEFAULT_PATH,
) -> tuple[bool, list[str]]:
    """Return whether FreeCAD has enough information to build the MVP solid."""
    ready, missing = source_geometry_complete(profile_id, path)
    if not bend_policy_available:
        missing = [*missing, "bend_policy"]
    return (ready and bend_policy_available, missing)


def geometry_ready_for_accurate_solid(profile_id: str, path: Path = DEFAULT_PATH) -> tuple[bool, list[str]]:
    """Backward-compatible strict provenance check.

    Every geometric dimension, including bend radius, must be explicitly present
    in the reviewed source record.
    """
    record = solid_geometry_for(profile_id, path)
    missing: list[str] = []
    for key in ("thickness", "lip_return", "inside_bend_radius"):
        value = record[key]
        if value.get("in") is None or value.get("mm") is None:
            missing.append(key)
    return (not missing, missing)
