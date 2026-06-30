from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.ingest import (
    csv_ingestor, ats_ingestor, resume_ingestor,
    linkedin_ingestor, github_ingestor, notes_ingestor,
)
from src.merger import merge_all
from src.projector import project, DEFAULT_CONFIG
from src.validator import validate


def run_pipeline(sources_dir: Path, config: dict | None = None) -> list[dict[str, Any]]:
    if config is None:
        config = DEFAULT_CONFIG

    # Define paths relative to the input sources directory
    csv_path = sources_dir / "recruiter_csv" / "candidates.csv"
    ats_dir = sources_dir / "ats_json"
    resumes_dir = sources_dir / "resumes"
    linkedin_dir = sources_dir / "linkedin"
    github_dir = sources_dir / "github"
    notes_dir = sources_dir / "recruiter_notes"
    index_path = sources_dir / "candidate_index.json"

    # Ingest records
    records = []
    records.extend(csv_ingestor.ingest(csv_path))
    records.extend(ats_ingestor.ingest(ats_dir))
    records.extend(resume_ingestor.ingest(resumes_dir))
    records.extend(linkedin_ingestor.ingest(linkedin_dir))
    records.extend(github_ingestor.ingest(github_dir))
    records.extend(notes_ingestor.ingest(notes_dir))

    # Load candidate mapping index
    candidate_index = {}
    if index_path.exists():
        try:
            candidate_index = json.loads(index_path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"[pipeline] warning: could not load index {index_path.name}: {exc}")

    # Merge records
    merged_candidates = merge_all(records, candidate_index)

    # Project and validate candidates
    projected_results = []
    for cand in merged_candidates:
        # Check C14 edge case where resume is empty string and there are no other sources
        # If it is a null profile (all fields None except candidate_id), we handle it
        projected = project(cand, config)
        validate(projected, config)
        projected_results.append(projected)

    return projected_results


def get_pipeline_steps(sources_dir: Path, config: dict | None = None) -> list[dict[str, Any]]:
    if config is None:
        config = DEFAULT_CONFIG

    # Define paths
    csv_path = sources_dir / "recruiter_csv" / "candidates.csv"
    ats_dir = sources_dir / "ats_json"
    resumes_dir = sources_dir / "resumes"
    linkedin_dir = sources_dir / "linkedin"
    github_dir = sources_dir / "github"
    notes_dir = sources_dir / "recruiter_notes"
    index_path = sources_dir / "candidate_index.json"

    # Ingest records
    raw_records = []
    raw_records.extend(csv_ingestor.ingest(csv_path))
    raw_records.extend(ats_ingestor.ingest(ats_dir))
    raw_records.extend(resume_ingestor.ingest(resumes_dir))
    raw_records.extend(linkedin_ingestor.ingest(linkedin_dir))
    raw_records.extend(github_ingestor.ingest(github_dir))
    raw_records.extend(notes_ingestor.ingest(notes_dir))

    # Load candidate mapping index
    candidate_index = {}
    if index_path.exists():
        try:
            candidate_index = json.loads(index_path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"[pipeline] warning: could not load index {index_path.name}: {exc}")

    # Access the grouping logic from merger module
    import src.merger as merger
    from src.normalizer import normalize_phone, normalize_date, normalize_skill

    groups = merger._build_groups(raw_records, candidate_index)
    steps_results = []

    for group_key, records in groups.items():
        # Step 1: Raw Records (deep copy to avoid mutation side-effects)
        import copy
        candidate_raw = copy.deepcopy(records)

        # Step 2: Normalized Records
        candidate_norm = []
        for r in candidate_raw:
            norm_rec = copy.deepcopy(r)
            if r.get("phone"):
                norm_rec["phone"] = normalize_phone(r["phone"])
            if r.get("last_updated"):
                norm_rec["last_updated"] = normalize_date(r["last_updated"])
            if r.get("skills"):
                norm_rec["skills"] = [normalize_skill(str(s)) for s in r["skills"]]
            if r.get("experience"):
                norm_exp = []
                for exp in r["experience"]:
                    ne = copy.deepcopy(exp)
                    ne["start"] = normalize_date(exp.get("start"))
                    ne["end"] = normalize_date(exp.get("end"))
                    norm_exp.append(ne)
                norm_rec["experience"] = norm_exp
            candidate_norm.append(norm_rec)

        # Step 3: Merged Canonical Record
        merged_cand = merger._merge_group(group_key, records)

        # Step 4: Projected Record
        projected = project(merged_cand, config)

        # Step 5: Validation
        validation_status = "PASSED"
        try:
            validate(projected, config)
        except Exception as e:
            validation_status = f"FAILED: {e}"

        steps_results.append({
            "candidate_id": merged_cand.candidate_id,
            "full_name": merged_cand.full_name or "Unknown Candidate",
            "headline": merged_cand.headline or "No Headline",
            "overall_confidence": merged_cand.overall_confidence,
            "has_conflicts": bool(merged_cand.alternatives and any(merged_cand.alternatives.values())),
            "raw_records": candidate_raw,
            "normalized_records": candidate_norm,
            "canonical_record": merged_cand.model_dump(),
            "projected_record": projected,
            "validation_status": validation_status
        })

    return sorted(steps_results, key=lambda x: x["candidate_id"])
