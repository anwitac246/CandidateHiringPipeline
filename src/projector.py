from __future__ import annotations

import re
from typing import Any

from src.schema import CandidateRecord
from src.normalizer import normalize_phone, normalize_skill

DEFAULT_CONFIG: dict = {
    "fields": [
        {"path": "candidate_id",      "type": "string",   "required": True},
        {"path": "full_name",         "type": "string",   "required": True},
        {"path": "emails",            "type": "string[]"},
        {"path": "phones",            "type": "string[]"},
        {"path": "location",          "type": "object"},
        {"path": "links",             "type": "object"},
        {"path": "headline",          "type": "string"},
        {"path": "years_experience",  "type": "number"},
        {"path": "skills",   "from": "skills[].name",  "type": "string[]"},
        {"path": "experience",        "type": "object[]"},
        {"path": "education",         "type": "object[]"},
        {"path": "provenance",        "type": "object[]"},
        {"path": "overall_confidence","type": "number"},
        {"path": "alternatives",      "type": "object",   "on_missing": "omit"},
        {"path": "raw_notes",         "type": "string",   "on_missing": "omit"},
    ],
    "include_confidence": True,
    "include_provenance": True,
    "on_missing": "null",
}


def project(record: CandidateRecord, config: dict) -> dict:
    fields = config.get("fields", DEFAULT_CONFIG["fields"])
    include_confidence = config.get("include_confidence", True)
    include_provenance = config.get("include_provenance", True)
    on_missing = config.get("on_missing", "null")

    record_dict = record.model_dump()
    output: dict[str, Any] = {}

    for spec in fields:
        out_key = spec["path"]
        in_path = spec.get("from", out_key)
        required = spec.get("required", False)
        normalize = spec.get("normalize")

        value = _resolve_path(record_dict, in_path)
        value = _apply_normalize(value, normalize)

        if value is None or value == [] or value == {}:
            if on_missing == "omit":
                continue
            if on_missing == "error" and required:
                raise ValueError(f"Required field '{out_key}' is missing or null")
            output[out_key] = None
        else:
            output[out_key] = value

    if include_confidence and "overall_confidence" not in output:
        output["overall_confidence"] = record.overall_confidence

    if include_provenance and "provenance" not in output:
        output["provenance"] = [p.model_dump() for p in record.provenance]

    return output


def _resolve_path(record_dict: dict, path: str) -> Any:
    # skills[].name  → map over list extracting attribute
    m = re.match(r'^(\w+)\[\]\.(\w+)$', path)
    if m:
        lst = record_dict.get(m.group(1), []) or []
        return [item.get(m.group(2)) for item in lst
                if isinstance(item, dict) and item.get(m.group(2)) is not None]

    # emails[0]  → index into list
    m = re.match(r'^(\w+)\[(\d+)\]$', path)
    if m:
        lst = record_dict.get(m.group(1), []) or []
        idx = int(m.group(2))
        return lst[idx] if isinstance(lst, list) and len(lst) > idx else None

    # location.city  → nested dict
    if '.' in path:
        head, tail = path.split('.', 1)
        parent = record_dict.get(head)
        if isinstance(parent, dict):
            return parent.get(tail)
        return None

    return record_dict.get(path)


def _apply_normalize(value: Any, normalize: str | None) -> Any:
    if normalize is None or value is None:
        return value
    if normalize == "E164":
        if isinstance(value, list):
            return [normalize_phone(v) or v for v in value]
        return normalize_phone(str(value)) or value
    if normalize == "canonical":
        if isinstance(value, list):
            return [normalize_skill(str(v)) for v in value]
        return normalize_skill(str(value))
    return value
