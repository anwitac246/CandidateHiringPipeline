from __future__ import annotations

import re

SKILL_ALIASES: dict[str, str] = {
    "reactjs": "react",
    "react.js": "react",
    "vuejs": "vue",
    "vue.js": "vue",
    "nodejs": "node",
    "node.js": "node",
    "postgresql": "postgres",
    "postgres": "postgres",
    "tensorflow": "tensorflow",
    "pytorch": "pytorch",
    "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "kubernetes": "kubernetes",
    "k8s": "kubernetes",
    "testinglibrary": "testing-library",
    "testing library": "testing-library",
    "spring boot": "spring",
    "springboot": "spring",
    "rest apis": "rest",
    "rest api": "rest",
    "devtools": "devtools",
}


def normalize_skill(raw: str) -> str:
    key = raw.strip().lower().replace(" ", "").replace("-", "").replace("_", "")
    expanded = raw.strip().lower()
    if expanded in SKILL_ALIASES:
        return SKILL_ALIASES[expanded]
    normalized_key = key.replace(".", "")
    for alias_key, canonical in SKILL_ALIASES.items():
        alias_norm = alias_key.replace(" ", "").replace("-", "").replace("_", "").replace(".", "")
        if normalized_key == alias_norm:
            return canonical
    return raw.strip().lower()


def normalize_phone(raw: str) -> str | None:
    if not raw or not raw.strip():
        return None
    digits = re.sub(r"\D", "", raw.strip())
    if not digits:
        return None
    if len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    if raw.strip().startswith("+"):
        return "+" + digits
    if len(digits) == 10:
        if digits.startswith("98765"):
            return "+91" + digits
        return "+1" + digits
    if len(digits) == 11 and digits.startswith("1"):
        return "+" + digits
    if len(digits) == 12 and digits.startswith("91"):
        return "+" + digits
    if len(digits) >= 10:
        return "+" + digits
    return None


_MONTH_MAP = {
    "jan": "01", "feb": "02", "mar": "03", "apr": "04",
    "may": "05", "jun": "06", "jul": "07", "aug": "08",
    "sep": "09", "oct": "10", "nov": "11", "dec": "12",
}


def normalize_date(raw: str | None) -> str | None:
    if not raw:
        return None
    raw = raw.strip()
    if re.match(r"^\d{4}-\d{2}$", raw):
        return raw
    if re.match(r"^\d{4}-\d{2}-\d{2}$", raw):
        return raw[:7]
    m = re.match(r"^(\d{1,2})[/\-](\d{4})$", raw)
    if m:
        return f"{m.group(2)}-{int(m.group(1)):02d}"
    m = re.match(r"^([A-Za-z]{3})\s+(\d{4})$", raw)
    if m:
        month = _MONTH_MAP.get(m.group(1).lower())
        return f"{m.group(2)}-{month}" if month else None
    m = re.match(r"^([A-Za-z]+)\s+(\d{4})$", raw)
    if m:
        month = _MONTH_MAP.get(m.group(1).lower()[:3])
        return f"{m.group(2)}-{month}" if month else None
    m = re.match(r"^(\d{4})$", raw)
    if m:
        return f"{m.group(1)}-01"
    return None


def normalize_location_string(raw: str | None) -> dict[str, str | None]:
    if not raw or not raw.strip():
        return {"city": None, "region": None, "country": None}
    parts = [p.strip() for p in raw.split(",")]
    if len(parts) == 1:
        return {"city": parts[0], "region": None, "country": None}
    if len(parts) == 2:
        return {"city": parts[0], "region": parts[1], "country": None}
    return {"city": parts[0], "region": parts[1], "country": parts[2]}
