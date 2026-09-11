"""Extract the checked-in P1000 submittal into a raw catalog record."""
from __future__ import annotations

import json
from pathlib import Path

from strut_catalog_etl.p1000_parser import normalize_p1000_pdf


PDF = Path("sources/unistrut_ohio/pdfs/P1000_Submittal.pdf")
RAW = Path("catalog/raw/unistrut_ohio/P1000.json")
NORMALIZED = Path("generated/P1000.normalized.json")


def main() -> None:
    raw, normalized = normalize_p1000_pdf(PDF)
    RAW.parent.mkdir(parents=True, exist_ok=True)
    NORMALIZED.parent.mkdir(parents=True, exist_ok=True)
    RAW.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")
    NORMALIZED.write_text(json.dumps(normalized, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {RAW}")
    print(f"wrote {NORMALIZED}")


if __name__ == "__main__":
    main()
