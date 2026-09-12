import pytest

from strut_catalog_etl.section_table_parser import parse_section_properties_text


P1000_STYLE = """
Elements of Section - P1000
Area of Section 0.555 in2 (3.6 cm2)
Axis 1-1 Axis 2-2
Moment of Inertia (I) 0.185 in4 (7.7 cm4) 0.236 in4 (9.8 cm4)
Section Modulus (S) 0.202 in3 (3.3 cm3) 0.290 in3 (4.8 cm3)
Radius of Gyration (r) 0.577 in (1.5 cm) 0.651 in (1.7 cm)
"""

P4100_STYLE = """
Elements of Section - P4100
Area of Section 0.290 in2 (1.9 cm2)
Axis 1-1 Axis 2-2
Moment of Inertia (I) 0.026 in4 (1.1 cm4) 0.107 in4 (4.5 cm4)
Section Modulus (S) 0.054 in3 (0.9 cm3) 0.132 in3 (2.2 cm3)
Radius of Gyration (r) 0.298 in (0.8 cm) 0.609 in (1.5 cm)
"""


def test_parse_p1000_style_section_table():
    assert parse_section_properties_text(P1000_STYLE) == {
        "area": {"in2": 0.555, "cm2": 3.6},
        "ix": {"in4": 0.185, "cm4": 7.7},
        "iy": {"in4": 0.236, "cm4": 9.8},
        "sx": {"in3": 0.202, "cm3": 3.3},
        "sy": {"in3": 0.29, "cm3": 4.8},
        "rx": {"in": 0.577, "cm": 1.5},
        "ry": {"in": 0.651, "cm": 1.7},
    }


def test_parse_p4100_style_section_table():
    assert parse_section_properties_text(P4100_STYLE) == {
        "area": {"in2": 0.29, "cm2": 1.9},
        "ix": {"in4": 0.026, "cm4": 1.1},
        "iy": {"in4": 0.107, "cm4": 4.5},
        "sx": {"in3": 0.054, "cm3": 0.9},
        "sy": {"in3": 0.132, "cm3": 2.2},
        "rx": {"in": 0.298, "cm": 0.8},
        "ry": {"in": 0.609, "cm": 1.5},
    }


def test_section_table_requires_marker():
    with pytest.raises(ValueError, match="Elements of Section"):
        parse_section_properties_text("Area of Section 0.42 in2 (2.7 cm2)")


def test_section_table_rejects_marker_without_values():
    with pytest.raises(ValueError, match="no section properties"):
        parse_section_properties_text("Elements of Section")
