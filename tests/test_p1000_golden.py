import json
from pathlib import Path


GOLDEN = Path("catalog/golden/P1000.normalized.json")


def test_p1000_golden_fixture_has_expected_core_shape():
    data = json.loads(GOLDEN.read_text(encoding="utf-8"))

    assert data["profile_id"] == "P1000"
    assert data["family"] == "P1000"
    assert data["geometry"]["width_in"] == 1.625
    assert data["geometry"]["height_in"] == 1.625
    assert data["geometry"]["gauge"] == 12
    assert data["geometry"]["piercing"] == "solid"

    assert data["standard_lengths_ft"] == [10, 20]
    assert "PG" in data["finishes"]
    assert "HG" in data["finishes"]
    assert data["provenance"]["source_kind"] == "manufacturer_submittal"
    assert data["provenance"]["source_label"] == "P1000"
