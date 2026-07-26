from strut_catalog_etl.build_snapshot import build_snapshot


def test_build_snapshot_indexes_and_sorts_records() -> None:
    seed = {
        "meta": {"schema_version": "0.1.0"},
        "profiles": [{"id": "P4100"}, {"id": "P1000"}],
        "fittings": [{"id": "B"}, {"id": "A"}],
        "finishes": [{"code": "HG"}, {"code": "EG"}],
        "hardware": [],
    }

    snapshot = build_snapshot(seed)

    assert list(snapshot["profiles"]) == ["P1000", "P4100"]
    assert list(snapshot["fittings"]) == ["A", "B"]
    assert list(snapshot["finishes"]) == ["EG", "HG"]
    assert snapshot["schema_version"] == "0.1.0"


def test_build_snapshot_rejects_duplicate_ids() -> None:
    seed = {
        "profiles": [{"id": "P1000"}, {"id": "P1000"}],
        "fittings": [],
        "finishes": [],
        "hardware": [],
    }

    try:
        build_snapshot(seed)
    except ValueError as exc:
        assert "Duplicate id" in str(exc)
    else:
        raise AssertionError("duplicate profile IDs must fail")
