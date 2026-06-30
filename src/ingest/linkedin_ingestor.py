from __future__ import annotations

import json
from pathlib import Path

SOURCE_NAME = "linkedin"
TRUST_SCORE = 0.70


def ingest(linkedin_dir: Path) -> list[dict]:
    path = linkedin_dir / "candidates.json"
    if not path.exists():
        return []
    try:
        raw_list = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[linkedin_ingestor] skipping {path.name}: {exc}")
        return []

    return [_extract(r) for r in raw_list]


def _extract(raw: dict) -> dict:
    return {
        "source": SOURCE_NAME,
        "trust_score": TRUST_SCORE,
        "full_name": raw.get("full_name") or None,
        "email": raw.get("email") or None,
        "phone": None,
        "headline": raw.get("headline") or None,
        "current_company": raw.get("company") or None,
        "location": raw.get("location") or None,
        "connections": raw.get("connections"),
        "skills": raw.get("skills") or [],
        "experience": raw.get("experience") or [],
        "education": raw.get("education") or [],
        "last_updated": raw.get("last_updated") or None,
    }
