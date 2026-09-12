from strut_catalog_etl.channel_submittal import parse_identity_fields, parse_standard_lengths


def test_parse_p1000_header_layout():
    text = 'P1000 - 1-5/8" x 1-5/8", 12 Gauge Channel, Solid'
    parsed = parse_identity_fields(text)
    assert parsed == {
        "id": "P1000",
        "family": "1-5/8 x 1-5/8",
        "gauge": 12,
        "width_in": 1.625,
        "height_in": 1.625,
        "form": "solid",
    }


def test_parse_p4100_header_layout():
    text = 'P4100 - 1-5/8" x 13/16", 14 Gauge, Solid P4100'
    parsed = parse_identity_fields(text)
    assert parsed == {
        "id": "P4100",
        "family": "1-5/8 x 13/16",
        "gauge": 14,
        "width_in": 1.625,
        "height_in": 0.8125,
        "form": "solid",
    }


def test_parse_standard_lengths_with_tolerance_noise():
    text = (
        'Special Lengths: 10 feet: 10\' or 10’ 1 /8” (3.05m) ± 1 /8" (3 mm) '
        '20 feet: 20\' or 20’ 3 /8” (6.11m) ± 1 /8" (3 mm) Standard Lengths:'
    )
    assert parse_standard_lengths(text) == {
        "ft": [10.0, 20.0],
        "m": [3.05, 6.11],
    }
