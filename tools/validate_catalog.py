#!/usr/bin/env python3
"""Validate raw and normalized catalog records without FreeCAD."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from strut_catalog_etl.validator import Validator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        required=True,
        help="catalog data directory containing profiles.json and raw/",
    )
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    validator = Validator(args.data_dir.resolve())
    findings = validator.validate()
    errors = [item for item in findings if item.level == "error"]
    warnings = [item for item in findings if item.level == "warning"]

    for finding in findings:
        print(finding)

    failed = bool(errors or (args.strict and warnings))
    status = "FAIL" if failed else "PASS"
    print(
        f"{status}: {len(validator.normalized_ids)} normalized profiles, "
        f"{len(validator.raw_source_ids)} raw sources, "
        f"{len(validator.raw_record_ids)} raw records; "
        f"{len(errors)} errors, {len(warnings)} warnings"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
