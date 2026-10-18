import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_unverified_fittings_cannot_be_mistaken_for_release_records():
    inventory = json.loads((ROOT / "etl/fittings/source_inventory.json").read_text())
    seed = json.loads((ROOT / "etl/seed/unistrut_seed.json").read_text())
    release_ids = {record["id"] for record in seed["fittings"]}
    for record in inventory["records"]:
        assert record["id"] not in release_ids
        if record["verification_status"] != "verified":
            assert record["geometry_family"] is None
            assert record["dimensions"] is None
            assert record["hole_pattern"] is None
