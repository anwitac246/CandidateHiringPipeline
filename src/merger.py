from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from typing import Any

from src.schema import (
    CandidateRecord, LocationRecord, LinksRecord,
    SkillRecord, ExperienceRecord, EducationRecord, ProvenanceEntry,
)
from src.normalizer import (
    normalize_phone, normalize_skill, normalize_date,
    normalize_location_string,
)

TRUST_RANK: dict[str, int] = {
    "ats_json": 5,
    "recruiter_csv": 4,
    "linkedin": 3,
    "github": 3,
    "resume": 2,
    "recruiter_notes": 1,
}


def merge_all(
    all_records: list[dict],
    candidate_index: dict[str, dict],
) -> list[CandidateRecord]:
    groups = _build_groups(all_records, candidate_index)
    results = []
    for key, recs in groups.items():
        try:
            results.append(_merge_group(key, recs))
        except Exception as exc:
            print(f"[merger] error on group {key!r}: {exc}")
    return sorted(results, key=lambda r: r.candidate_id)


# ── GROUPING ──────────────────────────────────────────────────────────────────

def _build_groups(
    records: list[dict],
    index: dict[str, dict],
) -> dict[str, list[dict]]:
    id_to_email: dict[str, str] = {}
    id_to_name: dict[str, str] = {}
    for cid, info in index.items():
        e = _norm_email(info.get("email") or "")
        n = _norm_name(info.get("full_name") or "")
        if e:
            id_to_email[cid] = e
        if n:
            id_to_name[cid] = n

    groups: dict[str, list[dict]] = defaultdict(list)
    email_to_key: dict[str, str] = {}
    name_to_key: dict[str, str] = {}

    normal = [r for r in records if r.get("source") not in ("github", "recruiter_notes")]
    github_recs = [r for r in records if r.get("source") == "github"]
    notes_recs = [r for r in records if r.get("source") == "recruiter_notes"]

    # pass 1: records that have an email → email is the canonical key
    for r in normal:
        email = _norm_email(r.get("email") or "")
        if email:
            key = f"email:{email}"
            groups[key].append(r)
            email_to_key[email] = key

    # pass 2: records without email → match existing group by name+phone, else new name group
    for r in normal:
        if _norm_email(r.get("email") or ""):
            continue
        name = _norm_name(r.get("full_name") or "")
        phone = normalize_phone(r.get("phone") or "")
        key = _find_by_name_phone(groups, name_to_key, name, phone)
        if key is None:
            key = f"name:{name}" if name else f"anon:{_uid(r)}"
            if name:
                name_to_key[name] = key
        groups[key].append(r)

    # pass 3: GitHub records — use candidate_id_hint → index → email/name
    for r in github_recs:
        hint = r.get("candidate_id_hint", "")
        email = id_to_email.get(hint)
        gh_name = _norm_name(r.get("full_name") or "")
        key = None
        if email and email in email_to_key:
            key = email_to_key[email]
        elif gh_name in name_to_key:
            key = name_to_key[gh_name]
        else:
            key = _scan_groups_for_name(groups, gh_name)
        if key is None:
            key = f"name:{gh_name}" if gh_name else f"gh:{hint}"
            if gh_name:
                name_to_key[gh_name] = key
        groups[key].append(r)

    # pass 4: Notes records — use candidate_id_hint → index
    for r in notes_recs:
        hint = r.get("candidate_id_hint", "")
        email = id_to_email.get(hint)
        note_name = id_to_name.get(hint, "")
        key = None
        if email and email in email_to_key:
            key = email_to_key[email]
        elif note_name in name_to_key:
            key = name_to_key[note_name]
        elif note_name:
            key = _scan_groups_for_name(groups, note_name)
        if key is None:
            key = f"name:{note_name}" if note_name else f"notes:{hint}"
            if note_name:
                name_to_key[note_name] = key
        groups[key].append(r)

    return dict(groups)


def _find_by_name_phone(
    groups: dict, name_to_key: dict, name: str, phone: str | None
) -> str | None:
    if name in name_to_key:
        return name_to_key[name]
    for key, recs in groups.items():
        for r in recs:
            if _norm_name(r.get("full_name") or "") == name and name:
                r_phone = normalize_phone(r.get("phone") or "")
                if phone and r_phone and phone == r_phone:
                    return key
                if not phone and not r_phone:
                    return key
    return None


def _scan_groups_for_name(groups: dict, name: str) -> str | None:
    if not name:
        return None
    for key, recs in groups.items():
        for r in recs:
            if _norm_name(r.get("full_name") or "") == name:
                return key
    return None


# ── MERGING ───────────────────────────────────────────────────────────────────

def _merge_group(group_key: str, records: list[dict]) -> CandidateRecord:
    records = _dedup_within_source(records)
    sorted_recs = _sort_by_trust(records)

    provenance: list[ProvenanceEntry] = []
    alternatives: dict[str, list[dict[str, Any]]] = {}

    full_name = _pick_scalar(sorted_recs, "full_name", "full_name", provenance, alternatives)
    title = _pick_title(sorted_recs, provenance, alternatives)
    years_exp_raw = _pick_scalar(sorted_recs, "years_experience", "years_experience", provenance, alternatives)
    years_exp = float(years_exp_raw) if years_exp_raw is not None else None
    bio = _pick_scalar(sorted_recs, "bio", "bio", provenance, alternatives)
    raw_notes = next((r.get("raw_notes") for r in records if r.get("raw_notes")), None)

    emails = _collect_emails(sorted_recs, provenance)
    phones = _collect_phones(sorted_recs, provenance, alternatives)
    location = _pick_location(sorted_recs, provenance)
    links = _build_links(sorted_recs, provenance)
    skills = _merge_skills(records, provenance)
    experience = _merge_experience(sorted_recs, provenance)
    education = _merge_education(sorted_recs, provenance)

    candidate_id = _assign_id(group_key, sorted_recs)
    overall_confidence = _score_confidence(
        sorted_recs, full_name, emails, phones, skills, experience, alternatives
    )

    return CandidateRecord(
        candidate_id=candidate_id,
        full_name=full_name,
        emails=emails,
        phones=phones,
        location=location,
        links=links,
        headline=title,
        years_experience=years_exp,
        skills=skills,
        experience=experience,
        education=education,
        provenance=provenance,
        overall_confidence=round(overall_confidence, 3),
        alternatives=alternatives,
        raw_notes=raw_notes,
    )


# ── DEDUPLICATION & SORTING ───────────────────────────────────────────────────

def _dedup_within_source(records: list[dict]) -> list[dict]:
    """
    Within each source, if two records share the same email, keep the most
    recent (by last_updated). The older record's differing fields are logged
    as alternatives on the winner. This handles the C13 duplicate-CSV-row case.
    """
    by_source: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_source[r.get("source", "")].append(r)

    result = []
    for source, recs in by_source.items():
        if len(recs) == 1:
            result.extend(recs)
            continue
        by_email: dict[str, list[dict]] = defaultdict(list)
        no_email = []
        for r in recs:
            email = _norm_email(r.get("email") or "")
            if email:
                by_email[email].append(r)
            else:
                no_email.append(r)
        for email, group in by_email.items():
            if len(group) == 1:
                result.extend(group)
            else:
                group.sort(key=lambda r: r.get("last_updated") or "", reverse=True)
                winner = group[0]
                winner.setdefault("_suppressed_in_source", [])
                for loser in group[1:]:
                    winner["_suppressed_in_source"].append({
                        "source": source,
                        "last_updated": loser.get("last_updated"),
                        "phone": loser.get("phone"),
                    })
                result.append(winner)
        result.extend(no_email)
    return result


def _sort_by_trust(records: list[dict]) -> list[dict]:
    def key(r: dict):
        trust = TRUST_RANK.get(r.get("source", ""), 0)
        date = r.get("last_updated") or "0000-00-00"
        return (trust, date)
    return sorted(records, key=key, reverse=True)


# ── SCALAR FIELD PICKER ───────────────────────────────────────────────────────

def _pick_scalar(
    sorted_recs: list[dict],
    field: str,
    prov_label: str,
    provenance: list[ProvenanceEntry],
    alternatives: dict[str, list],
) -> Any:
    winner_value = None
    winner_source = None
    winner_trust = -1

    for r in sorted_recs:
        val = r.get(field)
        if val is None:
            continue
        trust = TRUST_RANK.get(r.get("source", ""), 0)
        src = r.get("source", "unknown")

        if winner_value is None:
            winner_value = val
            winner_source = src
            winner_trust = trust
            provenance.append(ProvenanceEntry(
                field=prov_label, source=src, method="pick_highest_trust"
            ))
        elif val != winner_value:
            alternatives.setdefault(prov_label, []).append({
                "value": val,
                "source": src,
                "trust": trust,
                "suppressed_reason": "lower_trust" if trust < winner_trust else "lower_recency",
            })

    return winner_value


def _pick_title(
    sorted_recs: list[dict],
    provenance: list[ProvenanceEntry],
    alternatives: dict[str, list],
) -> str | None:
    candidates: list[tuple[int, str, str]] = []
    for r in sorted_recs:
        src = r.get("source", "")
        trust = TRUST_RANK.get(src, 0)
        title = r.get("title") or r.get("headline")
        if title:
            candidates.append((trust, title, src))

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[0], reverse=True)
    winner_trust, winner_title, winner_src = candidates[0]
    provenance.append(ProvenanceEntry(field="headline", source=winner_src, method="pick_highest_trust"))

    for trust, title, src in candidates[1:]:
        if title != winner_title:
            alternatives.setdefault("headline", []).append({
                "value": title,
                "source": src,
                "trust": trust,
                "suppressed_reason": "lower_trust" if trust < winner_trust else "lower_recency",
            })

    return winner_title


# ── EMAILS ────────────────────────────────────────────────────────────────────

def _collect_emails(
    sorted_recs: list[dict],
    provenance: list[ProvenanceEntry],
) -> list[str]:
    seen: list[str] = []
    for r in sorted_recs:
        raw = r.get("email") or ""
        email = raw.strip().lower()
        if email and email not in seen:
            seen.append(email)
            provenance.append(ProvenanceEntry(
                field="emails", source=r.get("source", "unknown"), method="collect_unique"
            ))
    return seen


# ── PHONES ────────────────────────────────────────────────────────────────────

def _collect_phones(
    sorted_recs: list[dict],
    provenance: list[ProvenanceEntry],
    alternatives: dict[str, list],
) -> list[str]:
    seen: list[str] = []
    first_source: str | None = None

    for r in sorted_recs:
        raw = r.get("phone") or ""
        normalized = normalize_phone(raw)
        if not normalized:
            continue
        src = r.get("source", "unknown")
        if normalized not in seen:
            if not seen:
                first_source = src
                provenance.append(ProvenanceEntry(
                    field="phones", source=src, method="normalize_e164"
                ))
            else:
                trust = TRUST_RANK.get(src, 0)
                first_trust = TRUST_RANK.get(first_source or "", 0)
                alternatives.setdefault("phones", []).append({
                    "value": normalized,
                    "source": src,
                    "trust": trust,
                    "suppressed_reason": "conflict_different_number",
                    "note": f"primary from {first_source} (trust={first_trust})",
                })
            seen.append(normalized)

    return seen


# ── LOCATION ──────────────────────────────────────────────────────────────────

def _pick_location(
    sorted_recs: list[dict],
    provenance: list[ProvenanceEntry],
) -> LocationRecord:
    for r in sorted_recs:
        raw = r.get("location") or ""
        if raw.strip():
            parts = normalize_location_string(raw)
            provenance.append(ProvenanceEntry(
                field="location", source=r.get("source", "unknown"), method="normalize_location"
            ))
            return LocationRecord(**parts)
    return LocationRecord()


# ── LINKS ─────────────────────────────────────────────────────────────────────

def _build_links(
    sorted_recs: list[dict],
    provenance: list[ProvenanceEntry],
) -> LinksRecord:
    linkedin_url = None
    github_url = None
    portfolio_url = None
    other: list[str] = []

    for r in sorted_recs:
        links = r.get("links") or []
        if isinstance(links, str):
            links = [links]
        for url in links:
            url = url.strip()
            if not url:
                continue
            if "linkedin.com" in url and not linkedin_url:
                linkedin_url = url
                provenance.append(ProvenanceEntry(field="links.linkedin", source=r.get("source",""), method="extract_url"))
            elif "github.com" in url and not github_url:
                github_url = url
                provenance.append(ProvenanceEntry(field="links.github", source=r.get("source",""), method="extract_url"))
            elif url not in other and url != github_url and url != linkedin_url:
                if not portfolio_url and not url.startswith("https://github"):
                    portfolio_url = url
                elif url not in other:
                    other.append(url)

    return LinksRecord(linkedin=linkedin_url, github=github_url, portfolio=portfolio_url, other=other)


# ── SKILLS ────────────────────────────────────────────────────────────────────

def _merge_skills(
    records: list[dict],
    provenance: list[ProvenanceEntry],
) -> list[SkillRecord]:
    skill_map: dict[str, SkillRecord] = {}

    for r in records:
        raw_skills = r.get("skills") or []
        src = r.get("source", "unknown")
        trust = TRUST_RANK.get(src, 0) / 5.0

        for raw in raw_skills:
            if not raw:
                continue
            canonical = normalize_skill(str(raw))
            if canonical in skill_map:
                existing = skill_map[canonical]
                if src not in existing.sources:
                    existing.sources.append(src)
                    existing.confidence = min(1.0, existing.confidence + 0.1)
            else:
                skill_map[canonical] = SkillRecord(
                    name=canonical,
                    confidence=round(trust, 2),
                    sources=[src],
                )

    if skill_map:
        provenance.append(ProvenanceEntry(
            field="skills", source="all_sources", method="union_normalized"
        ))

    return sorted(skill_map.values(), key=lambda s: (-s.confidence, s.name))


# ── EXPERIENCE ────────────────────────────────────────────────────────────────

def _merge_experience(
    sorted_recs: list[dict],
    provenance: list[ProvenanceEntry],
) -> list[ExperienceRecord]:
    for r in sorted_recs:
        raw_exp = r.get("experience") or []
        if not raw_exp:
            continue
        src = r.get("source", "unknown")
        provenance.append(ProvenanceEntry(field="experience", source=src, method="take_highest_trust"))
        result = []
        for e in raw_exp:
            result.append(ExperienceRecord(
                company=e.get("company"),
                title=e.get("title"),
                start=normalize_date(e.get("start")),
                end=normalize_date(e.get("end")),
                summary=e.get("summary"),
            ))
        return result
    return []


# ── EDUCATION ─────────────────────────────────────────────────────────────────

def _merge_education(
    sorted_recs: list[dict],
    provenance: list[ProvenanceEntry],
) -> list[EducationRecord]:
    for r in sorted_recs:
        raw_edu = r.get("education")
        if not raw_edu:
            continue
        src = r.get("source", "unknown")
        provenance.append(ProvenanceEntry(field="education", source=src, method="take_highest_trust"))

        if isinstance(raw_edu, dict):
            return [EducationRecord(
                institution=raw_edu.get("institution"),
                degree=raw_edu.get("degree"),
                field=raw_edu.get("field"),
                end_year=str(raw_edu["end_year"]) if raw_edu.get("end_year") else None,
            )]

        if isinstance(raw_edu, list):
            result = []
            for e in raw_edu:
                if isinstance(e, dict):
                    result.append(EducationRecord(
                        institution=e.get("institution"),
                        degree=e.get("degree"),
                        field=e.get("field"),
                        end_year=str(e["end_year"]) if e.get("end_year") else None,
                    ))
            if result:
                return result
    return []


# ── CONFIDENCE ────────────────────────────────────────────────────────────────

def _score_confidence(
    records: list[dict],
    full_name: Any,
    emails: list,
    phones: list,
    skills: list,
    experience: list,
    alternatives: dict,
) -> float:
    score = 1.0
    source_count = len({r.get("source") for r in records})
    score += min(0.1 * (source_count - 1), 0.3)

    if not full_name:
        score -= 0.2
    if not emails:
        score -= 0.15
    if not phones:
        score -= 0.05
    if not skills:
        score -= 0.1
    if not experience:
        score -= 0.1

    conflict_count = sum(len(v) for v in alternatives.values())
    score -= 0.05 * conflict_count

    avg_trust = sum(TRUST_RANK.get(r.get("source", ""), 0) for r in records) / max(len(records), 1)
    score *= avg_trust / 5.0

    return max(0.0, min(1.0, score))


# ── CANDIDATE ID ──────────────────────────────────────────────────────────────

def _assign_id(group_key: str, sorted_recs: list[dict]) -> str:
    for r in sorted_recs:
        hint = r.get("candidate_id_hint")
        if hint:
            return hint
    if group_key.startswith("email:"):
        raw = group_key[6:]
        return "C_" + hashlib.md5(raw.encode()).hexdigest()[:6].upper()
    if group_key.startswith("name:"):
        raw = group_key[5:]
        return "C_" + hashlib.md5(raw.encode()).hexdigest()[:6].upper()
    return "C_" + hashlib.md5(group_key.encode()).hexdigest()[:6].upper()


# ── UTILITIES ─────────────────────────────────────────────────────────────────

def _norm_email(raw: str) -> str:
    return raw.strip().lower()


def _norm_name(raw: str) -> str:
    return re.sub(r"\s+", " ", raw.strip().lower())


def _uid(r: dict) -> str:
    return hashlib.md5(str(r).encode()).hexdigest()[:8]
