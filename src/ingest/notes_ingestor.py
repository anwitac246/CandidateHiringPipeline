from __future__ import annotations

from pathlib import Path

SOURCE_NAME = "recruiter_notes"
TRUST_SCORE = 0.50


def ingest(notes_dir: Path) -> list[dict]:
    records = []
    for path in sorted(notes_dir.glob("*.txt")):
        try:
            text = path.read_text(encoding="utf-8").strip()
        except Exception as exc:
            print(f"[notes_ingestor] could not read {path.name}: {exc}")
            continue

        records.append({
            "source": SOURCE_NAME,
            "source_file": path.name,
            "candidate_id_hint": path.stem,
            "trust_score": TRUST_SCORE,
            "full_name": None,
            "email": None,
            "phone": None,
            "raw_notes": text,
        })
    return records
