"""Extract the checked-in P4100 submittal into raw and normalized catalog records."""
from __future__ import annotations

import json
from pathlib import Path

from strut_catalog_etl.p4100_parser import extract_p4100_pdf

PDF = Path("sources/unistrut_ohio/pdfs/P4100_Submittal.pdf")
RAW = Path("catalog/raw/unistrut_ohio/P4100.json")
NORMALIZED = Path("generated/P4100.normalized.json")


def main() -> None:
    raw, normalized = extract_p4100_pdf(PDF)
    RAW.parent.mkdir(parents=True, exist_ok=True)
    NORMALIZED.parent.mkdir(parents=True, exist_ok=True)
    RAW.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")
    NORMALIZED.write_text(json.dumps(normalized, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {RAW}")
    print(f"wrote {NORMALIZED}")


if __name__ == "__main__":
    main()
