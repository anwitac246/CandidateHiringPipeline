import sys, json
sys.path.insert(0, '.')
from pathlib import Path
from src.ingest import resume_ingestor, csv_ingestor, ats_ingestor, linkedin_ingestor, github_ingestor, notes_ingestor

base = Path('data/sources')

# ── RESUME INGESTOR ──────────────────────────────────────────────────────────
print("=" * 60)
print("RESUME INGESTOR")
print("=" * 60)
records = resume_ingestor.ingest(base / 'resumes')
by_file = {r['source_file']: r for r in records}

checks = [
    ('C01.txt', 'full_name', 'Linus Torvalds'),
    ('C01.txt', 'email',     'linus.t@example.com'),
    ('C01.txt', 'phone',     '+1-415-555-0101'),
    ('C03.txt', 'full_name', 'Sindre Sorhus'),
    ('C03.txt', 'skills',    []),
    ('C04.txt', 'full_name', 'Priya Nair'),
    ('C04.txt', 'email',     'priya.nair@example.com'),
    ('C04.txt', 'phone',     '9876510004'),
    ('C06.txt', 'email',     None),
    ('C07.txt', 'phone',     '+91 9876512345'),
    ('C09.txt', 'full_name', 'Rohit Verma'),
    ('C11.txt', 'phone',     '9876510011'),
    ('C12.txt', 'email',     'kent.d@example.com'),
    ('C14.txt', 'full_name', None),
    ('C14.txt', 'skills',    []),
    ('C15.txt', 'full_name', 'Tom Preston-Werner'),
    ('C16.txt', 'email',     None),
    ('C20.txt', 'email',     'paul.i@example.com'),
]

all_pass = True
for fname, field, expected in checks:
    actual = by_file.get(fname, {}).get(field)
    ok = actual == expected
    if not ok:
        all_pass = False
    status = 'PASS' if ok else 'FAIL'
    print(f"  [{status}] {fname} > {field}: expected={repr(expected)}  got={repr(actual)}")

print()
print("EXPERIENCE ENTRIES per resume:")
for fname in ['C01.txt', 'C04.txt', 'C07.txt', 'C09.txt', 'C15.txt']:
    r = by_file.get(fname, {})
    exp = r.get('experience', [])
    print(f"  {fname}: {len(exp)} entries")
    for e in exp:
        c = e.get('company', '')
        t = e.get('title', '')
        s = e.get('start', '')
        en = e.get('end', '')
        print(f"    company={repr(c)}  title={repr(t)}  start={repr(s)}  end={repr(en)}")

print()
print("SKILLS:")
for fname in ['C12.txt', 'C03.txt', 'C01.txt']:
    r = by_file.get(fname, {})
    print(f"  {fname}: {r.get('skills')}")

print()
print("EDUCATION:")
for fname in ['C01.txt', 'C04.txt']:
    r = by_file.get(fname, {})
    print(f"  {fname}: {r.get('education')}")

print()
if all_pass:
    print("ALL RESUME ASSERTIONS PASSED")
else:
    print("SOME RESUME ASSERTIONS FAILED")

# ── CSV INGESTOR ─────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("CSV INGESTOR")
print("=" * 60)
csv_records = csv_ingestor.ingest(base / 'recruiter_csv' / 'candidates.csv')
csv_checks = [
    ('Sara Khan',        'phone',          None),
    ('Neha Joshi',       'email',          None),
    ('Meera Iyer',       'phone',          '098765 10011'),
    ('Linus Torvalds',   'years_experience', 29.0),
    ('Linus Torvalds',   'location',       'Portland, OR, US'),
]
by_name_csv = {}
for r in csv_records:
    by_name_csv.setdefault(r['full_name'], r)

all_pass_csv = True
for name, field, expected in csv_checks:
    actual = by_name_csv.get(name, {}).get(field)
    ok = actual == expected
    if not ok:
        all_pass_csv = False
    status = 'PASS' if ok else 'FAIL'
    print(f"  [{status}] {name} > {field}: expected={repr(expected)}  got={repr(actual)}")

aditya_rows = [r for r in csv_records if r['full_name'] == 'Aditya Rao']
ok = len(aditya_rows) == 2 and aditya_rows[0]['phone'] != aditya_rows[1]['phone']
all_pass_csv = all_pass_csv and ok
print(f"  [{'PASS' if ok else 'FAIL'}] C13 duplicate rows: {len(aditya_rows)} rows, phones differ: {aditya_rows[0].get('phone')} vs {aditya_rows[1].get('phone')}")

print()
if all_pass_csv:
    print("ALL CSV ASSERTIONS PASSED")
else:
    print("SOME CSV ASSERTIONS FAILED")

# ── ATS INGESTOR ─────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("ATS INGESTOR")
print("=" * 60)
ats_records = ats_ingestor.ingest(base / 'ats_json')
by_name_ats = {r['full_name']: r for r in ats_records}

ats_checks = [
    ('Addy Osmani',    'email',     None),
    ('Linus Torvalds', 'bio',       'Creator of the Linux kernel and Git version control system.'),
    ('Dan Abramov',    'title',     'Staff Software Engineer'),
    ('Divya Pillai',   'title',     'Software Engineer II'),
]
all_pass_ats = True
for name, field, expected in ats_checks:
    actual = by_name_ats.get(name, {}).get(field)
    ok = actual == expected
    if not ok:
        all_pass_ats = False
    status = 'PASS' if ok else 'FAIL'
    print(f"  [{status}] {name} > {field}: expected={repr(expected)}  got={repr(actual)}")

c01_ats = by_name_ats.get('Linus Torvalds', {})
exp_count = len(c01_ats.get('experience', []))
ok = exp_count == 3
all_pass_ats = all_pass_ats and ok
print(f"  [{'PASS' if ok else 'FAIL'}] C01 ATS experience entries: expected=3  got={exp_count}")

ok = len(ats_records) == 11
all_pass_ats = all_pass_ats and ok
print(f"  [{'PASS' if ok else 'FAIL'}] C09 malformed skipped: expected=11 records  got={len(ats_records)}")

print()
if all_pass_ats:
    print("ALL ATS ASSERTIONS PASSED")
else:
    print("SOME ATS ASSERTIONS FAILED")

# ── LINKEDIN ─────────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("LINKEDIN INGESTOR")
print("=" * 60)
li_records = linkedin_ingestor.ingest(base / 'linkedin')
by_name_li = {r['full_name']: r for r in li_records}

li_checks = [
    ('Dan Abramov',  'headline',  'Software Engineer II'),
    ('Dan Abramov',  'connections', 8400),
    ('TJ Holowaychuk','skills',   ['go', 'node.js', 'javascript', 'c', 'lua', 'rust']),
    ('Meera Iyer',   'headline',  'Machine Learning Engineer'),
]
all_pass_li = True
for name, field, expected in li_checks:
    actual = by_name_li.get(name, {}).get(field)
    ok = actual == expected
    if not ok:
        all_pass_li = False
    status = 'PASS' if ok else 'FAIL'
    print(f"  [{status}] {name} > {field}: expected={repr(expected)}  got={repr(actual)}")

dan_exp = by_name_li.get('Dan Abramov', {}).get('experience', [])
ok = len(dan_exp) == 2
all_pass_li = all_pass_li and ok
print(f"  [{'PASS' if ok else 'FAIL'}] Dan Abramov LinkedIn experience entries: expected=2  got={len(dan_exp)}")

print()
if all_pass_li:
    print("ALL LINKEDIN ASSERTIONS PASSED")
else:
    print("SOME LINKEDIN ASSERTIONS FAILED")

# ── GITHUB ───────────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("GITHUB INGESTOR")
print("=" * 60)
gh_records = github_ingestor.ingest(base / 'github')
by_hint = {r['candidate_id_hint']: r for r in gh_records}

gh_checks = [
    ('C03', 'full_name',  'Sindre Sorhus'),
    ('C01', 'full_name',  'Linus Torvalds'),
    ('C20', 'candidate_id_hint', 'C20'),
]
all_pass_gh = True
for hint, field, expected in gh_checks:
    actual = by_hint.get(hint, {}).get(field)
    ok = actual == expected
    if not ok:
        all_pass_gh = False
    status = 'PASS' if ok else 'FAIL'
    print(f"  [{status}] {hint} > {field}: expected={repr(expected)}  got={repr(actual)}")

ok = len(gh_records) == 9
all_pass_gh = all_pass_gh and ok
print(f"  [{'PASS' if ok else 'FAIL'}] Total GitHub profiles: expected=9  got={len(gh_records)}")

c03_skills = by_hint.get('C03', {}).get('skills', [])
ok = len(c03_skills) > 0
all_pass_gh = all_pass_gh and ok
print(f"  [{'PASS' if ok else 'FAIL'}] C03 GitHub has skills (only source): {c03_skills}")

print()
if all_pass_gh:
    print("ALL GITHUB ASSERTIONS PASSED")
else:
    print("SOME GITHUB ASSERTIONS FAILED")

# ── NOTES ────────────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("NOTES INGESTOR")
print("=" * 60)
notes_records = notes_ingestor.ingest(base / 'recruiter_notes')
hints = [r['candidate_id_hint'] for r in notes_records]
ok = set(hints) == {'C04', 'C12', 'C20'}
print(f"  [{'PASS' if ok else 'FAIL'}] Notes files: expected C04/C12/C20  got={hints}")
for r in notes_records:
    ok = bool(r.get('raw_notes'))
    print(f"  [{'PASS' if ok else 'FAIL'}] {r['candidate_id_hint']} has raw_notes: {r['raw_notes'][:60]}...")

print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)
all_ok = all_pass and all_pass_csv and all_pass_ats and all_pass_li and all_pass_gh
print(f"  Resumes  : {'PASS' if all_pass else 'FAIL'}")
print(f"  CSV      : {'PASS' if all_pass_csv else 'FAIL'}")
print(f"  ATS      : {'PASS' if all_pass_ats else 'FAIL'}")
print(f"  LinkedIn : {'PASS' if all_pass_li else 'FAIL'}")
print(f"  GitHub   : {'PASS' if all_pass_gh else 'FAIL'}")
print(f"  OVERALL  : {'ALL PASS' if all_ok else 'FAILURES PRESENT - see above'}")
