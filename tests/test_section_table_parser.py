import pytest

from strut_catalog_etl.section_table_parser import parse_section_properties_text


P1000_STYLE = """
Elements of Section
Area 0.420
Ix 0.183
Iy 0.185
Sx 0.224
Sy 0.227
rx 0.660
ry 0.664
"""

P4100_STYLE = """
Elements   of   Section
Area: 0.289   Ix: 0.023   Iy: 0.104
Sx: 0.057   Sy: 0.128   rx: 0.282   ry: 0.600
"""


def test_parse_p1000_style_section_table():
    assert parse_section_properties_text(P1000_STYLE) == {
        "area": {"in2": 0.42},
        "ix": {"in4": 0.183},
        "iy": {"in4": 0.185},
        "sx": {"in3": 0.224},
        "sy": {"in3": 0.227},
        "rx": {"in": 0.66},
        "ry": {"in": 0.664},
    }


def test_parse_p4100_style_section_table():
    assert parse_section_properties_text(P4100_STYLE) == {
        "area": {"in2": 0.289},
        "ix": {"in4": 0.023},
        "iy": {"in4": 0.104},
        "sx": {"in3": 0.057},
        "sy": {"in3": 0.128},
        "rx": {"in": 0.282},
        "ry": {"in": 0.6},
    }


def test_section_table_requires_marker():
    with pytest.raises(ValueError, match="Elements of Section"):
        parse_section_properties_text("Area 0.42 Ix 0.18")


def test_section_table_rejects_marker_without_values():
    with pytest.raises(ValueError, match="no section properties"):
        parse_section_properties_text("Elements of Section")
