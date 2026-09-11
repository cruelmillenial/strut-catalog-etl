"""Utilities for turning catalog PDFs into reproducible raw source records."""
from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_file(path: Path) -> str:
    """Return the lowercase SHA-256 digest for *path*."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_pdf_text(path: Path) -> list[str]:
    """Extract one text string per page using the optional pypdf dependency."""
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError(
            "PDF extraction requires the optional dependency; install with `pip install -e '.[pdf]'`."
        ) from exc

    reader = PdfReader(str(path))
    return [(page.extract_text() or "").strip() for page in reader.pages]


def build_raw_pdf_record(
    path: Path,
    *,
    source_id: str,
    title: str,
    record_id: str,
    pages_used: list[int] | None = None,
) -> dict:
    """Build a validator-compatible raw source record from a local PDF."""
    path = Path(path)
    page_text = extract_pdf_text(path)
    if pages_used is None:
        pages_used = list(range(1, len(page_text) + 1))

    selected = []
    for page_number in pages_used:
        if page_number < 1 or page_number > len(page_text):
            raise ValueError(f"page {page_number} is outside PDF page range 1..{len(page_text)}")
        selected.append({"page": page_number, "text": page_text[page_number - 1]})

    return {
        "schema_version": 1,
        "source": {
            "id": source_id,
            "file": path.name,
            "title": title,
            "sha256": sha256_file(path),
            "pages_used": pages_used,
        },
        "extraction": {
            "method": "pypdf_text",
            "status": "draft",
            "records": [
                {
                    "id": record_id,
                    "page": pages_used[0],
                    "pages": selected,
                }
            ],
        },
    }
