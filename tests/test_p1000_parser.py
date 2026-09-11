import json
from pathlib import Path

from strut_catalog_etl.p1000_parser import normalize_p1000_submittal


GOLDEN = Path("catalog/golden/P1000.normalized.json")


def test_p1000_normalizer_matches_golden_fixture():
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    assert normalize_p1000_submittal() == golden


def test_p1000_normalizer_accepts_acquired_provenance():
    digest = "a" * 64
    data = normalize_p1000_submittal(
        source_file="downloads/P1000.pdf",
        source_sha256=digest,
    )

    provenance = data["profiles"][0]["provenance"]
    assert provenance["source_file"] == "downloads/P1000.pdf"
    assert provenance["source_sha256"] == digest
