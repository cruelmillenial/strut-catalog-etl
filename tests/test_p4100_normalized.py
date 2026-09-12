from strut_catalog_etl.p4100_parser import normalize_p4100_raw


def _raw_fixture() -> dict:
    return {
        "source": {
            "id": "P4100_SUBMITTAL",
            "file": "P4100_Submittal.pdf",
            "sha256": "a" * 64,
            "pages_used": [1, 2],
        },
        "extraction": {
            "records": [
                {
                    "id": "P4100",
                    "pages": [
                        {
                            "page": 1,
                            "text": (
                                'P4100 - 1-5/8" x 13/16", 14 Gauge, Solid P4100\n'
                                'Special Lengths: 10 feet: 10\' or 10’ 1 /8” (3.05m) ± 1 /8" (3 mm) '
                                '20 feet: 20\' or 20’ 3 /8” (6.11m) ± 1 /8" (3 mm)\n'
                                'Available in Pre-Galvanized (PG), Atkore Defender (DF), '
                                'Hot-Dip Galvanized (HG), Plain (PL), Green (GR), '
                                'Zinc Dichromate (ZD), and Stainless Steel (SS).'
                            ),
                        },
                        {"page": 2, "text": ""},
                    ],
                }
            ]
        },
    }


def test_p4100_normalized_shape_and_provenance():
    data = normalize_p4100_raw(_raw_fixture())
    assert data["schema_version"] == 1
    assert len(data["profiles"]) == 1

    profile = data["profiles"][0]
    assert profile["id"] == "P4100"
    assert profile["family"] == "1-5/8 x 13/16"
    assert profile["gauge"] == 14
    assert profile["geometry"]["width"] == {"in": 1.625, "mm": 41.3}
    assert profile["geometry"]["height"] == {"in": 0.8125, "mm": 20.6}
    assert profile["geometry"]["profile_spec"]["kind"] == "u_channel_lipped"
    assert profile["standard_lengths"] == {"ft": [10.0, 20.0], "m": [3.05, 6.11]}
    assert profile["finishes"] == ["PG", "DF", "HG", "GR", "ZD", "PL", "SS"]

    provenance = profile["provenance"]
    assert provenance["source_id"] == "P4100_SUBMITTAL"
    assert provenance["source_file"] == "P4100_Submittal.pdf"
    assert provenance["source_sha256"] == "a" * 64
    assert provenance["source_pages"] == [1, 2]
