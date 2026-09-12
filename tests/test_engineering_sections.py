from strut_catalog_etl.engineering_sections import (
    SECTION_PROPERTY_KEYS,
    build_section_properties,
    empty_section_properties,
)


def test_empty_section_properties_contract():
    assert tuple(empty_section_properties()) == SECTION_PROPERTY_KEYS
    assert all(value is None for value in empty_section_properties().values())


def test_build_section_properties_accepts_partial_known_fields():
    props = build_section_properties(
        area={"in2": 0.42, "cm2": 2.71},
        ix={"in4": 0.18, "cm4": 7.49},
        rx={"in": 0.65, "mm": 16.5},
    )
    assert props == {
        "area": {"in2": 0.42, "cm2": 2.71},
        "ix": {"in4": 0.18, "cm4": 7.49},
        "rx": {"in": 0.65, "mm": 16.5},
    }


def test_build_section_properties_rejects_unknown_fields():
    try:
        build_section_properties(j={"in4": 0.1})
    except ValueError as exc:
        assert "unknown section property keys" in str(exc)
    else:
        raise AssertionError("expected unknown section property key to fail")
