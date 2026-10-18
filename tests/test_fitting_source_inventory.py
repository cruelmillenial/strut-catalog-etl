import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_fitting_source_inventory_resolves_to_manifest():
    manifest = json.loads((ROOT / "sources/unistrut_ohio/submittals.json").read_text())
    inventory = json.loads((ROOT / "etl/fittings/source_inventory.json").read_text())
    source_by_label = {entry["label"]: entry for entry in manifest["documents"]}
    assert inventory["record_status"] == "source_inventory_only"
    assert [record["id"] for record in inventory["records"]] == [
        "P1065", "P1066", "P1067", "P1068",
    ]
    for record in inventory["records"]:
        source = source_by_label[record["source_manifest_label"]]
        assert source["category"] == "Fittings"
        assert record["source_document_url"] == source["document_url"]
        assert record["extraction_status"] == "pending"
        assert record["verification_status"] == "unverified"
        assert record["geometry_family"] is None
        assert record["dimensions"] is None
        assert record["hole_pattern"] is None
