"""Extract the checked-in P4100 submittal for parser comparison."""
from __future__ import annotations

import json
from pathlib import Path

from strut_catalog_etl.p4100_parser import extract_p4100_pdf

PDF = Path("sources/unistrut_ohio/pdfs/P4100_Submittal.pdf")
RAW = Path("catalog/raw/unistrut_ohio/P4100.json")
PARSED = Path("generated/P4100.parsed.json")


def main() -> None:
    raw, parsed = extract_p4100_pdf(PDF)
    RAW.parent.mkdir(parents=True, exist_ok=True)
    PARSED.parent.mkdir(parents=True, exist_ok=True)
    RAW.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")
    PARSED.write_text(json.dumps(parsed, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {RAW}")
    print(f"wrote {PARSED}")


if __name__ == "__main__":
    main()
