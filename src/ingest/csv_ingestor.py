from __future__ import annotations

import csv
from pathlib import Path

SOURCE_NAME = "recruiter_csv"
TRUST_SCORE = 0.80


def ingest(csv_path: Path) -> list[dict]:
    """
    Read the recruiter CSV and return one dict per row.
    Rows with the same email are kept separate here; merging happens
    in the merger stage. Blank strings are normalised to None so
    downstream code never has to distinguish '' from None.
    """
    records = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            records.append({
                "source": SOURCE_NAME,
                "trust_score": TRUST_SCORE,
                "full_name": row.get("full_name") or None,
                "email": row.get("email") or None,
                "phone": row.get("phone") or None,
                "current_company": row.get("current_company") or None,
                "title": row.get("title") or None,
                "location": row.get("location") or None,
                "years_experience": _to_float(row.get("years_experience")),
                "last_updated": row.get("last_updated") or None,
            })
    return records


def _to_float(value: str | None) -> float | None:
    try:
        return float(value) if value else None
    except ValueError:
        return None
