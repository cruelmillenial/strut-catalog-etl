#!/usr/bin/env python3
"""CLI wrapper for the Unistrut Service Company submittal manifest builder."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from strut_catalog_etl.unistrut_ohio_manifest import ARCHIVE_URL, build_manifest, fetch_html


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=ARCHIVE_URL)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("sources/unistrut_ohio/submittals.json"),
    )
    args = parser.parse_args()

    manifest = build_manifest(fetch_html(args.url), args.url)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {len(manifest['documents'])} records to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
