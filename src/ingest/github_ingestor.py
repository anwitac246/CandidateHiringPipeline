from __future__ import annotations

import json
from pathlib import Path

SOURCE_NAME = "github"
TRUST_SCORE = 0.70


def ingest(github_dir: Path) -> list[dict]:
    records = []
    for path in sorted(github_dir.glob("*.json")):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"[github_ingestor] skipping {path.name}: {exc}")
            continue
        records.append(_extract(raw, path.stem))
    return records


def _extract(raw: dict, candidate_id: str) -> dict:
    blog = raw.get("blog") or ""
    links = []
    if raw.get("html_url"):
        links.append(raw["html_url"])
    if blog and blog.startswith("http"):
        links.append(blog)

    return {
        "source": SOURCE_NAME,
        "source_file": f"{candidate_id}.json",
        "candidate_id_hint": candidate_id,
        "trust_score": TRUST_SCORE,
        "full_name": raw.get("name") or None,
        "email": None,
        "phone": None,
        "bio": raw.get("bio") or None,
        "location": raw.get("location") or None,
        "current_company": _clean_company(raw.get("company")),
        "links": links,
        "skills": raw.get("languages") or [],
        "public_repos": raw.get("public_repos"),
        "followers": raw.get("followers"),
        "repo_names": raw.get("repo_names") or [],
    }


def _clean_company(raw: str | None) -> str | None:
    if not raw:
        return None
    return raw.strip().lstrip("@")
