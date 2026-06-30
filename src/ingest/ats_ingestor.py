from __future__ import annotations

import json
from pathlib import Path

SOURCE_NAME = "ats_json"
TRUST_SCORE = 0.90


def ingest(ats_dir: Path) -> list[dict]:
    """
    Read all JSON files in the ATS directory.
    The main candidates.json is a well-formed array.
    Any other .json files are treated as individual blobs (e.g. C09_malformed.json).
    Malformed JSON is caught, logged, and skipped without crashing.
    """
    records = []
    if not ats_dir.exists():
        print(f"[ats_ingestor] warning: ATS directory {ats_dir} does not exist. Skipping.")
        return []

    main_file = ats_dir / "candidates.json"
    if main_file.exists():
        records.extend(_parse_main(main_file))

    for path in sorted(ats_dir.glob("*.json")):
        if path.name == "candidates.json":
            continue
        records.extend(_parse_blob(path))

    return records


def _parse_main(path: Path) -> list[dict]:
    try:
        raw_list = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[ats_ingestor] skipping {path.name}: {exc}")
        return []

    results = []
    for raw in raw_list:
        results.append(_extract(raw, path.name))
    return results


def _parse_blob(path: Path) -> list[dict]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[ats_ingestor] skipping {path.name} (malformed): {exc}")
        return []
    return [_extract(raw, path.name)]


def _extract(raw: dict, source_file: str) -> dict:
    return {
        "source": SOURCE_NAME,
        "source_file": source_file,
        "trust_score": TRUST_SCORE,
        "full_name": raw.get("name") or None,
        "email": raw.get("email") or None,
        "phone": raw.get("phone") or None,
        "title": raw.get("role_title") or None,
        "current_company": raw.get("company") or None,
        "bio": raw.get("bio") or None,
        "location": raw.get("location") or None,
        "years_experience": _to_float(raw.get("years_experience")),
        "skills": raw.get("skills") or [],
        "experience": raw.get("experience") or [],
        "education": raw.get("education") or None,
        "last_updated": raw.get("last_updated") or None,
    }


def _to_float(value) -> float | None:
    try:
        return float(value) if value is not None else None
    except (ValueError, TypeError):
        return None
