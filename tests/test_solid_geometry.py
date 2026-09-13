from strut_catalog_etl.solid_geometry import (
    geometry_ready_for_accurate_solid,
    solid_geometry_for,
)


def test_p1000_solid_geometry_contract_tracks_unsourced_bend_radius():
    geometry = solid_geometry_for("P1000")
    assert geometry["kind"] == "u_channel_lipped"
    assert geometry["width"]["in"] == 1.625
    assert geometry["height"]["in"] == 1.625
    assert geometry["thickness"]["in"] == 0.105
    assert geometry["lip_return"]["in"] == 0.375
    assert geometry["inside_bend_radius"]["status"] == "not_yet_sourced"

    ready, missing = geometry_ready_for_accurate_solid("P1000")
    assert not ready
    assert missing == ["inside_bend_radius"]


def test_p4100_solid_geometry_contract_exposes_actual_gaps():
    geometry = solid_geometry_for("P4100")
    assert geometry["width"]["in"] == 1.625
    assert geometry["height"]["in"] == 0.8125

    ready, missing = geometry_ready_for_accurate_solid("P4100")
    assert not ready
    assert missing == ["thickness", "lip_return", "inside_bend_radius"]
