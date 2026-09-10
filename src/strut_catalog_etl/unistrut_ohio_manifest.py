"""Build a deterministic manifest from the Unistrut Service Company submittal archive."""

from __future__ import annotations

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
    records_by_url: dict[str, dict] = {}
    current_category: str | None = None

    for node in soup.find_all(["h2", "a"]):
        if node.name == "h2":
            heading = " ".join(node.stripped_strings)
            if heading and heading not in {
                "Submittal Categories:",
                "Unistrut Submittal Data Sheet Archive",
            }:
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

        existing = records_by_url.get(absolute_url)
        if existing is None:
            records_by_url[absolute_url] = {
                "category": current_category,
                "label": label,
                "document_url": absolute_url,
                "alternate_labels": [],
            }
        elif label != existing["label"] and label not in existing["alternate_labels"]:
            existing["alternate_labels"].append(label)

    records = list(records_by_url.values())
    for record in records:
        record["alternate_labels"].sort(key=str.casefold)
    records.sort(
        key=lambda r: (
            r["category"].casefold(),
            r["label"].casefold(),
            r["document_url"],
        )
    )

    return {
        "schema_version": 1,
        "source": {
            "name": "Unistrut Service Company Submittal Data Sheet Archive",
            "url": source_url,
        },
        "documents": records,
    }
