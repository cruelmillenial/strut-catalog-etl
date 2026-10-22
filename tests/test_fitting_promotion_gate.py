import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_incomplete_fittings_cannot_be_mistaken_for_release_records():
    inventory = json.loads((ROOT / "etl/fittings/source_inventory.json").read_text())
    seed = json.loads((ROOT / "etl/seed/unistrut_seed.json").read_text())
    release_ids = {record["id"] for record in seed["fittings"]}
    for record in inventory["records"]:
        assert record["id"] not in release_ids
        assert record["verification_status"] in {"unverified", "reviewed"}
        assert record["dimensions"] is None
        assert record["hole_pattern"] is None


def test_uploaded_submittal_observations_are_traceable():
    inventory = json.loads((ROOT / "etl/fittings/source_inventory.json").read_text())
    expected = {
        "P1065": ("flat_splice_plate", 2, 0.38),
        "P1066": ("flat_splice_plate", 3, 0.56),
        "P1067": ("flat_splice_plate", 4, 0.78),
        "P1068": ("right_angle_connection_fitting", 2, 0.38),
    }
    assert set(expected) == {r["id"] for r in inventory["records"]}
    for record in inventory["records"]:
        family, visible_holes, eg_weight = expected[record["id"]]
        assert record["source_pages"] == [1]
        assert len(record["source_sha256"]) == 64
        assert record["geometry_family"] == family
        assert record["visible_hole_count"] == visible_holes
        assert record["catalog_weight_lb_per_piece_eg"] == eg_weight
