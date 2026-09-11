import json
from pathlib import Path


GOLDEN = Path("catalog/golden/P1000.normalized.json")


def test_p1000_golden_fixture_has_expected_core_shape():
    data = json.loads(GOLDEN.read_text(encoding="utf-8"))

    assert data["schema_version"] == 1
    assert len(data["profiles"]) == 1

    profile = data["profiles"][0]
    assert profile["id"] == "P1000"
    assert profile["family"] == "1-5/8 x 1-5/8"
    assert profile["gauge"] == 12

    assert profile["geometry"]["width"]["in"] == 1.625
    assert profile["geometry"]["height"]["in"] == 1.625
    assert profile["geometry"]["thickness"]["in"] == 0.105
    assert profile["geometry"]["piercing"]["series"] is None

    assert profile["standard_lengths"]["ft"] == [10.0, 20.0]
    assert "PG" in profile["finishes"]
    assert "HG" in profile["finishes"]

    provenance = profile["provenance"]
    assert provenance["source_id"] == "P1000_SUBMITTAL"
    assert provenance["source_pages"] == [1, 2]
