from __future__ import annotations

import re
from pathlib import Path

SOURCE_NAME = "resume"
TRUST_SCORE = 0.60

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
_PHONE_RE = re.compile(r"[\+\d][\d\s\-\(\)\.]{7,}[\d]")
_URL_RE = re.compile(r"https?://[^\s]+|(?:www\.|github\.com/|linkedin\.com/)[^\s]+")

_SECTION_HEADERS = re.compile(
    r"^(SUMMARY|PROFILE|OBJECTIVE|EXPERIENCE|EDUCATION|SKILLS|NOTE|ABOUT)\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def ingest(resumes_dir: Path) -> list[dict]:
    records = []
    for path in sorted(resumes_dir.glob("*.txt")):
        record = _parse_resume(path)
        if record is not None:
            records.append(record)
    return records


def _parse_resume(path: Path) -> dict | None:
    try:
        text = path.read_text(encoding="utf-8").strip()
    except Exception as exc:
        print(f"[resume_ingestor] could not read {path.name}: {exc}")
        return None

    if not text:
        print(f"[resume_ingestor] {path.name} is empty, returning null record")
        return {
            "source": SOURCE_NAME,
            "source_file": path.name,
            "trust_score": TRUST_SCORE,
            "full_name": None,
            "email": None,
            "phone": None,
            "location": None,
            "links": [],
            "title": None,
            "current_company": None,
            "skills": [],
            "experience": [],
            "education": [],
            "raw_text": "",
        }

    sections = _split_sections(text)
    header_block = sections.get("_header", "")

    emails = _EMAIL_RE.findall(header_block + "\n" + text)
    phones = _PHONE_RE.findall(header_block)
    urls = _URL_RE.findall(header_block)

    return {
        "source": SOURCE_NAME,
        "source_file": path.name,
        "trust_score": TRUST_SCORE,
        "full_name": _extract_name(header_block),
        "email": emails[0] if emails else None,
        "phone": phones[0].strip() if phones else None,
        "location": _extract_location(header_block),
        "links": urls,
        "title": _extract_title(sections),
        "current_company": _extract_company(sections),
        "skills": _extract_skills(sections),
        "experience": _extract_experience(sections),
        "education": _extract_education(sections),
        "raw_text": text,
    }


def _split_sections(text: str) -> dict[str, str]:
    lines = text.splitlines()
    sections: dict[str, list[str]] = {"_header": []}
    current = "_header"
    for line in lines:
        if _SECTION_HEADERS.match(line.strip()):
            current = line.strip().upper()
            sections[current] = []
        else:
            sections.setdefault(current, []).append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items()}


def _extract_name(header: str) -> str | None:
    lines = [l.strip() for l in header.splitlines() if l.strip()]
    if not lines:
        return None
    first = lines[0]
    if "@" in first or re.search(r"\d{5,}", first):
        return None
    if len(first.split()) <= 5:
        return first.title() if first.isupper() else first
    return None


def _extract_location(header: str) -> str | None:
    for line in header.splitlines():
        line = line.strip()
        parts = [p.strip() for p in line.split("|")]
        for part in parts:
            if re.search(r"\b(IN|US|CA|UK|NO|DE|AU)\b", part) or \
               re.search(r"\b(India|USA|Canada|Norway|Germany)\b", part, re.IGNORECASE) or \
               re.search(r",\s*[A-Z]{2}$", part):
                cleaned = re.sub(_EMAIL_RE, "", part)
                cleaned = re.sub(_PHONE_RE, "", cleaned)
                cleaned = cleaned.strip(" |,")
                if cleaned:
                    return cleaned
    return None


def _extract_title(sections: dict) -> str | None:
    header = sections.get("_header", "")
    exp = sections.get("EXPERIENCE", "")

    for line in header.splitlines():
        line = line.strip()
        if not line or "@" in line or re.search(r"\d{7,}", line):
            continue
        if re.search(r"—|Engineer|Developer|Architect|Lead|Manager|Founder|Advocate|Educator|Maintainer|Scientist|Analyst|SRE|SDE", line, re.IGNORECASE):
            parts = re.split(r"[|,—]", line)
            return parts[0].strip() if parts else line

    for line in exp.splitlines():
        line = line.strip()
        if re.search(r"—", line) and not re.search(r"\d{4}", line):
            parts = line.split("—")
            if len(parts) >= 2:
                return parts[1].strip()
    return None


def _extract_company(sections: dict) -> str | None:
    exp = sections.get("EXPERIENCE", "")
    for line in exp.splitlines():
        line = line.strip()
        if line and not re.search(r"\d{4}|Present|—", line):
            return line
        if "—" in line:
            return line.split("—")[0].strip()
    return None


def _extract_skills(sections: dict) -> list[str]:
    raw = sections.get("SKILLS", "")
    if not raw:
        return []
    skills = []
    for part in re.split(r"[,\n]", raw):
        part = part.strip().lstrip("-").strip()
        if part and len(part) < 40:
            skills.append(part)
    return skills


def _extract_experience(sections: dict) -> list[dict]:
    raw = sections.get("EXPERIENCE", "")
    if not raw:
        return []

    # detect format: dash-separated (Company — Title) vs stacked-line (Company\nTitle\nDate)
    if "\u2014" in raw or " — " in raw:
        return _parse_experience_dash(raw)
    return _parse_experience_stacked(raw)


def _parse_experience_dash(raw: str) -> list[dict]:
    entries = []
    current: dict | None = None

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue

        date_match = re.search(
            r"(\d{4}[-/]\d{2}|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|\d{2}/\d{4}|\b(19|20)\d{2}\b)",
            line, re.IGNORECASE,
        )

        if "\u2014" in line and not date_match:
            if current:
                entries.append(current)
            parts = line.split("\u2014")
            current = {
                "company": parts[0].strip(),
                "title": parts[1].strip() if len(parts) > 1 else None,
                "start": None, "end": None, "summary": [],
            }
        elif date_match and current:
            s, e = _parse_date_range(line)
            current["start"] = s
            current["end"] = e
        elif current and line.startswith("-"):
            current["summary"].append(line.lstrip("- ").strip())
        elif current and not date_match and len(line) > 10:
            current["summary"].append(line)

    if current:
        entries.append(current)

    return _finalise_entries(entries)


def _parse_experience_stacked(raw: str) -> list[dict]:
    """
    Handles format where each entry is:
        Company, Location          <- blank line separates entries
        Title
        Date range
        Bullet / description lines
    """
    entries = []
    blocks = re.split(r"\n{2,}", raw.strip())

    for block in blocks:
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if not lines:
            continue

        company_line = lines[0]
        # strip trailing city from "Razorpay, Pune" → keep full string as company
        company = company_line

        title = None
        start = None
        end = None
        summary_lines = []

        date_re = re.compile(
            r"(\d{4}[-/]\d{2}|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|\d{2}/\d{4}|\b(19|20)\d{2}\b)",
            re.IGNORECASE,
        )

        for line in lines[1:]:
            if date_re.search(line):
                start, end = _parse_date_range(line)
            elif title is None and not date_re.search(line):
                title = line
            else:
                summary_lines.append(line.lstrip("- ").strip())

        entries.append({
            "company": company,
            "title": title,
            "start": start,
            "end": end,
            "summary": summary_lines,
        })

    return _finalise_entries(entries)


def _finalise_entries(entries: list[dict]) -> list[dict]:
    cleaned = []
    for e in entries:
        summary_parts = e.get("summary", [])
        cleaned.append({
            "company": e.get("company"),
            "title": e.get("title"),
            "start": e.get("start"),
            "end": e.get("end"),
            "summary": " ".join(summary_parts) if summary_parts else None,
        })
    return cleaned


def _parse_date_range(text: str) -> tuple[str | None, str | None]:
    pattern = re.compile(
        r"(\d{4}[-/]\d{2}|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|\d{2}/\d{4}|\b(19|20)\d{2}\b)",
        re.IGNORECASE,
    )
    matches = [m[0] for m in pattern.finditer(text)]
    start = matches[0] if matches else None
    end_raw = matches[1] if len(matches) > 1 else None
    if re.search(r"present", text, re.IGNORECASE):
        end_raw = None
    return start, end_raw


def _extract_education(sections: dict) -> list[dict]:
    raw = sections.get("EDUCATION", "")
    if not raw:
        return []

    # if section has blank-line separated blocks, parse each block as one entry
    blocks = re.split(r"\n{2,}", raw.strip())
    if len(blocks) > 1:
        return [_education_block(b) for b in blocks if b.strip()]

    # single-block: each line is one entry
    entries = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(_education_block(line))
    return entries


def _education_block(block: str) -> dict:
    lines = [l.strip() for l in block.splitlines() if l.strip()]
    text = " ".join(lines)
    year_match = re.search(r"\b((?:19|20)\d{2})\b", text)
    end_year = year_match.group(1) if year_match else None
    clean = re.sub(r"\b(?:19|20)\d{2}\b", "", text)
    clean = re.sub(r"CGPA[^,]*", "", clean, flags=re.IGNORECASE)
    clean = clean.strip(" ,.-/")
    parts = [p.strip() for p in re.split(r"[,\u2014\-]", clean) if p.strip()]
    return {
        "institution": parts[-1] if parts else None,
        "degree": parts[0] if len(parts) > 1 else None,
        "field": parts[1] if len(parts) > 2 else None,
        "end_year": end_year,
        "raw": block.strip(),
    }
