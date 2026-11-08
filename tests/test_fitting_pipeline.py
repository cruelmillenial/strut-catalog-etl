import copy
import json
from pathlib import Path

import pytest

from strut_catalog_etl.fitting_pipeline import (
    build_reference_preview, merge_approved_fittings, validate_fitting_record,
    write_reference_preview,
)

ROOT = Path(__file__).resolve().parents[1]
REF = json.loads((ROOT / "etl/fittings/flat_plate_reference.json").read_text())


def test_preview_emits_all_three_parts_and_both_conditional_materials():
    preview = build_reference_preview(REF)
    assert preview["catalog_status"] == "preview_only"
    assert len(preview["fittings"]) == 6
    assert {p["manufacturer_part_id"] for p in preview["fittings"]} == {
        "P1065", "P1066", "P1067",
    }
    assert {p["material_requirement"] for p in preview["fittings"]} == {
        "meeting or exceeding ASTM A1011 SS GR 33",
        "meeting or exceeding ASTM A1011 HSLAS GR 45",
    }
    for p in preview["fittings"]:
        validate_fitting_record(p)
        assert p["record_status"] == "preview_only"
        assert p["accuracy_class"] == "reference_inferred"
        assert p["assumptions"]
        assert p["id"] != p["manufacturer_part_id"]
        assert len(p["geometry"]["holes"]) == p["hole_count"]


def test_preview_is_deterministic_and_writable(tmp_path):
    a = write_reference_preview(tmp_path / "a.json")
    b = write_reference_preview(tmp_path / "b.json")
    assert a.read_bytes() == b.read_bytes()
    assert json.loads(a.read_text())["catalog_status"] == "preview_only"


def test_committed_preview_is_exact_output_of_upstream_generator(tmp_path):
    expected = ROOT / "generated/preview/flat_plate_fittings.json"
    actual = write_reference_preview(tmp_path / "snapshot.json")
    assert actual.read_bytes() == expected.read_bytes()


def test_snapshot_writer_rejects_preview_but_accepts_deliberately_approved_fitting(tmp_path):
    from strut_catalog_etl.build_snapshot import write_snapshot

    preview = build_reference_preview(REF)["fittings"][0]
    source = tmp_path / "approved.json"
    source.write_text(json.dumps({"fittings": [preview]}))
    with pytest.raises(ValueError, match="not release_approved"):
        write_snapshot(output_path=tmp_path / "blocked.json", approved_fittings_path=source)
    assert not (tmp_path / "blocked.json").exists()

    record = copy.deepcopy(preview)
    record["record_status"] = "release_approved"
    record["release_review"] = {
        "decision": "approved",
        "reviewer": "synthetic-test-reviewer",
        "review_date": "2026-11-08",
        "approved_scope": "reference approximation test fixture only",
    }
    source.write_text(json.dumps({"fittings": [record]}))
    destination = write_snapshot(
        output_path=tmp_path / "approved-snapshot.json", approved_fittings_path=source
    )
    assert record["id"] in json.loads(destination.read_text())["fittings"]


def test_preview_cannot_be_promoted():
    row = build_reference_preview(REF)["fittings"][0]
    with pytest.raises(ValueError, match="not release_approved"):
        merge_approved_fittings({"fittings": []}, [row])


def test_approval_requires_explicit_review_and_named_scope():
    row = copy.deepcopy(build_reference_preview(REF)["fittings"][0])
    row["record_status"] = "release_approved"
    with pytest.raises(ValueError, match="release_review"):
        merge_approved_fittings({"fittings": []}, [row])
    row["release_review"] = {
        "decision": "approved",
        "reviewer": "test reviewer",
        "review_date": "2026-11-08",
        "approved_scope": "reference geometry preview accuracy only",
    }
    new_seed = merge_approved_fittings({"fittings": []}, [row])
    assert len(new_seed["fittings"]) == 1
    assert new_seed["fittings"][0]["accuracy_class"] == "reference_inferred"


def test_approved_fittings_detect_duplicates():
    row = copy.deepcopy(build_reference_preview(REF)["fittings"][0])
    row["record_status"] = "release_approved"
    row["release_review"] = {
        "decision": "approved", "reviewer": "test", "review_date": "2026-11-08",
        "approved_scope": "reference approximation",
    }
    with pytest.raises(ValueError, match="duplicate fitting id"):
        merge_approved_fittings({"fittings": [{"id": row["id"]}]}, [row])


def test_bad_geometry_or_source_digest_fails_while_still_a_preview():
    row = copy.deepcopy(build_reference_preview(REF)["fittings"][0])
    row["source_sha256"] = ""
    with pytest.raises(ValueError, match="source_sha256"):
        validate_fitting_record(row)
    row["source_sha256"] = "a" * 64
    row["geometry"]["holes"][0]["diameter_mm"] = 999
    with pytest.raises(ValueError, match="boundary"):
        validate_fitting_record(row)
