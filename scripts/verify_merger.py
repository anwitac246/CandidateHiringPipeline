import sys, json
sys.path.insert(0, '.')
from pathlib import Path
from src.ingest import csv_ingestor, ats_ingestor, resume_ingestor, linkedin_ingestor, github_ingestor, notes_ingestor
from src.merger import merge_all

base = Path('data/sources')

all_records = (
    csv_ingestor.ingest(base / 'recruiter_csv' / 'candidates.csv') +
    ats_ingestor.ingest(base / 'ats_json') +
    resume_ingestor.ingest(base / 'resumes') +
    linkedin_ingestor.ingest(base / 'linkedin') +
    github_ingestor.ingest(base / 'github') +
    notes_ingestor.ingest(base / 'recruiter_notes')
)

candidate_index = json.loads((base / 'candidate_index.json').read_text())
merged = merge_all(all_records, candidate_index)

print(f"Total merged candidates: {len(merged)}")
print()

# ── C01: clean happy path ─────────────────────────────────────────────────────
c01 = next((r for r in merged if r.full_name and 'Torvalds' in r.full_name), None)
print("=== C01 Linus Torvalds (clean happy path) ===")
if c01:
    print(f"  candidate_id : {c01.candidate_id}")
    print(f"  emails       : {c01.emails}")
    print(f"  phones       : {c01.phones}")
    print(f"  headline     : {c01.headline}")
    print(f"  location     : {c01.location}")
    print(f"  skills       : {[s.name for s in c01.skills[:5]]}")
    print(f"  experience   : {len(c01.experience)} entries")
    print(f"  education    : {len(c01.education)} entries")
    print(f"  confidence   : {c01.overall_confidence}")
    print(f"  sources      : {list({p.source for p in c01.provenance})}")
    print(f"  conflicts    : {list(c01.alternatives.keys())}")
else:
    print("  NOT FOUND - grouping failure")

print()

# ── C02: title conflict CSV vs ATS vs LinkedIn ────────────────────────────────
c02 = next((r for r in merged if r.full_name and 'Abramov' in r.full_name), None)
print("=== C02 Dan Abramov (title conflict) ===")
if c02:
    print(f"  headline (winner)  : {c02.headline}")
    print(f"  alternatives       : {json.dumps(c02.alternatives.get('headline', []), indent=4)}")
    print(f"  confidence         : {c02.overall_confidence}")
else:
    print("  NOT FOUND")

print()

# ── C06: no email in ATS, matched via name ─────────────────────────────────────
c06 = next((r for r in merged if r.full_name and 'Osmani' in r.full_name), None)
print("=== C06 Addy Osmani (no email in ATS - name match) ===")
if c06:
    print(f"  emails   : {c06.emails}")
    print(f"  phones   : {c06.phones}")
    print(f"  skills   : {[s.name for s in c06.skills[:5]]}")
    print(f"  sources  : {list({p.source for p in c06.provenance})}")
else:
    print("  NOT FOUND - grouping failure")

print()

# ── C07: phone conflict CSV vs resume ─────────────────────────────────────────
c07 = next((r for r in merged if r.full_name and 'Mehta' in r.full_name), None)
print("=== C07 Arjun Mehta (phone conflict) ===")
if c07:
    print(f"  phones (all)   : {c07.phones}")
    print(f"  phone conflicts: {json.dumps(c07.alternatives.get('phones', []), indent=4)}")
else:
    print("  NOT FOUND")

print()

# ── C13: duplicate CSV rows ────────────────────────────────────────────────────
c13 = next((r for r in merged if r.full_name and 'Aditya' in r.full_name), None)
print("=== C13 Aditya Rao (duplicate CSV rows, location null) ===")
if c13:
    print(f"  phones       : {c13.phones}")
    print(f"  location     : {c13.location}")
    print(f"  suppressed   : {c13.alternatives.get('phones', [])}")
else:
    print("  NOT FOUND")

print()

# ── C16: no email, name+phone match ───────────────────────────────────────────
c16 = next((r for r in merged if r.full_name and 'Joshi' in r.full_name), None)
print("=== C16 Neha Joshi (no email anywhere) ===")
if c16:
    print(f"  emails   : {c16.emails}")
    print(f"  phones   : {c16.phones}")
    print(f"  sources  : {list({p.source for p in c16.provenance})}")
else:
    print("  NOT FOUND")

print()

# ── C17 vs C18: must NOT have merged ─────────────────────────────────────────
c17 = next((r for r in merged if r.full_name and 'aman sharma' in (r.full_name or '').lower() and r.emails and 'sharma17' in r.emails[0]), None)
c18 = next((r for r in merged if r.full_name and 'sharma' in (r.full_name or '').lower() and r.emails and 'sharma18' in r.emails[0]), None)
print("=== C17/C18 Aman vs Amann Sharma (must NOT merge) ===")
print(f"  C17 found: {c17 is not None} email={c17.emails if c17 else None}")
print(f"  C18 found: {c18 is not None} email={c18.emails if c18 else None}")
print(f"  Are they separate: {c17 is not c18 and c17 is not None and c18 is not None}")

print()

# ── C03: skills only from GitHub ─────────────────────────────────────────────
c03 = next((r for r in merged if r.full_name and 'Sorhus' in r.full_name), None)
print("=== C03 Sindre Sorhus (skills from GitHub only) ===")
if c03:
    skill_sources = [(s.name, s.sources) for s in c03.skills]
    print(f"  skills+sources: {skill_sources}")
else:
    print("  NOT FOUND")

print()

# ── C20: has recruiter notes ──────────────────────────────────────────────────
c20 = next((r for r in merged if r.full_name and 'Irish' in r.full_name), None)
print("=== C20 Paul Irish (recruiter notes) ===")
if c20:
    print(f"  raw_notes: {c20.raw_notes[:80] if c20.raw_notes else None}...")
    print(f"  sources  : {list({p.source for p in c20.provenance})}")
else:
    print("  NOT FOUND")
