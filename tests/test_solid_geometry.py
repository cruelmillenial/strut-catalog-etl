from strut_catalog_etl.solid_geometry import (
    geometry_ready_for_accurate_solid,
    model_geometry_ready,
    solid_geometry_for,
    source_geometry_complete,
)


def test_p1000_solid_geometry_contract_tracks_unspecified_bend_radius():
    geometry = solid_geometry_for("P1000")
    assert geometry["kind"] == "u_channel_lipped"
    assert geometry["width"]["in"] == 1.625
    assert geometry["height"]["in"] == 1.625
    assert geometry["thickness"]["in"] == 0.105
    assert geometry["lip_return"]["in"] == 0.375
    assert geometry["inside_bend_radius"]["status"] == "not_specified_in_reviewed_sources"

    source_ready, source_missing = source_geometry_complete("P1000")
    assert source_ready
    assert source_missing == []

    model_ready, model_missing = model_geometry_ready("P1000", bend_policy_available=False)
    assert not model_ready
    assert model_missing == ["bend_policy"]

    model_ready, model_missing = model_geometry_ready("P1000", bend_policy_available=True)
    assert model_ready
    assert model_missing == []

    strict_ready, strict_missing = geometry_ready_for_accurate_solid("P1000")
    assert not strict_ready
    assert strict_missing == ["inside_bend_radius"]


def test_p4100_solid_geometry_contract_tracks_only_bend_radius_gap():
    geometry = solid_geometry_for("P4100")
    assert geometry["width"]["in"] == 1.625
    assert geometry["height"]["in"] == 0.8125
    assert geometry["thickness"]["in"] == 0.075
    assert geometry["lip_return"]["in"] == 0.375
    assert geometry["inside_bend_radius"]["status"] == "not_specified_in_reviewed_sources"

    source_ready, source_missing = source_geometry_complete("P4100")
    assert source_ready
    assert source_missing == []

    model_ready, model_missing = model_geometry_ready("P4100", bend_policy_available=True)
    assert model_ready
    assert model_missing == []

    strict_ready, strict_missing = geometry_ready_for_accurate_solid("P4100")
    assert not strict_ready
    assert strict_missing == ["inside_bend_radius"]
