"""Build the first deterministic catalog snapshot from migrated seed records."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SEED = ROOT / "etl" / "seed" / "unistrut_seed.json"
DEFAULT_OUTPUT = ROOT / "generated" / "unistrut" / "catalog.v0.1.0.json"


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise TypeError(f"Expected JSON object in {path}")
    return value


def _index(records: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        identifier = record.get(key)
        if not identifier or not isinstance(identifier, str):
            raise ValueError(f"Record missing string {key!r}: {record!r}")
        if identifier in result:
            raise ValueError(f"Duplicate {key} {identifier!r}")
        result[identifier] = record
    return dict(sorted(result.items()))


def build_snapshot(seed: dict[str, Any]) -> dict[str, Any]:
    meta = dict(seed.get("meta", {}))
    return {
        "schema_version": meta.get("schema_version", "0.1.0"),
        "meta": meta,
        "profiles": _index(seed.get("profiles", []), "id"),
        "fittings": _index(seed.get("fittings", []), "id"),
        "finishes": _index(seed.get("finishes", []), "code"),
        "hardware": _index(seed.get("hardware", []), "id"),
        "pierced_variants": seed.get("pierced_variants", []),
        "load_tables": seed.get("load_tables", []),
    }


def write_snapshot(
    seed_path: Path = DEFAULT_SEED,
    output_path: Path = DEFAULT_OUTPUT,
    approved_fittings_path: Path | None = None,
) -> Path:
    seed = _load(seed_path)
    if approved_fittings_path is not None:
        from strut_catalog_etl.fitting_pipeline import merge_approved_fittings

        approved = json.loads(approved_fittings_path.read_text(encoding="utf-8"))
        if not isinstance(approved, dict) or not isinstance(approved.get("fittings"), list):
            raise ValueError("approved fittings file must contain a fittings array")
        seed = merge_approved_fittings(seed, approved["fittings"])
    snapshot = build_snapshot(seed)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(snapshot, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--approved-fittings", type=Path, default=None,
        help="explicitly reviewed fitting records; preview records are rejected",
    )
    args = parser.parse_args()
    print(write_snapshot(args.seed, args.output, args.approved_fittings))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
