#!/usr/bin/env python3
"""Build a deterministic manifest from the Unistrut Service Company submittal archive."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

ARCHIVE_URL = "https://unistrutohio.com/pages/submittal-data-sheets"
USER_AGENT = "strut-catalog-etl/0.1 (+https://github.com/cruelmillenial/strut-catalog-etl)"


def fetch_html(url: str) -> str:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def build_manifest(html: str, source_url: str = ARCHIVE_URL) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    records: list[dict] = []
    current_category: str | None = None

    for node in soup.find_all(["h2", "a"]):
        if node.name == "h2":
            heading = " ".join(node.stripped_strings)
            if heading and heading not in {"Submittal Categories:", "Unistrut Submittal Data Sheet Archive"}:
                current_category = heading
            continue

        if current_category is None:
            continue

        href = node.get("href")
        label = " ".join(node.stripped_strings)
        if not href or not label:
            continue

        absolute_url = urljoin(source_url, href)
        if "cdn.shopify.com" not in absolute_url:
            continue

        records.append(
            {
                "category": current_category,
                "label": label,
                "document_url": absolute_url,
            }
        )

    records.sort(key=lambda r: (r["category"].casefold(), r["label"].casefold(), r["document_url"]))

    return {
        "schema_version": 1,
        "source": {
            "name": "Unistrut Service Company Submittal Data Sheet Archive",
            "url": source_url,
        },
        "documents": records,
    }


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
