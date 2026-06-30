"""
Generates synthetic source data for all 20 candidates: CSV, ATS JSON,
resumes, LinkedIn, recruiter notes. Each candidate is built to hit specific
edge cases listed in data/CANDIDATE_PLAN.md. Does not touch GitHub data,
that comes from github_user_fetcher.py.

Run: python scripts/generate_synthetic_data.py
"""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "sources"

# real names for github-linked candidates, matches the public profiles
GH_NAMES = {
    "C01": "Linus Torvalds",
    "C02": "Dan Abramov",
    "C03": "Sindre Sorhus",
    "C05": "Evan You",
    "C06": "Addy Osmani",
    "C10": "TJ Holowaychuk",
    "C12": "Kent C. Dodds",
    "C15": "Tom Preston-Werner",
    "C20": "Paul Irish",
}

# CSV rows: candidate_id is for our own tracking only, not a real field,
# stripped before writing to the actual CSV file
CSV_ROWS = [
    dict(candidate_id="C01", full_name="Linus Torvalds", email="linus.t@example.com",
         phone="+1-415-555-0101", current_company="Linux Foundation", title="Kernel Maintainer",
         last_updated="2026-05-01"),
    dict(candidate_id="C02", full_name="Dan Abramov", email="dan.a@example.com",
         phone="+1-415-555-0102", current_company="Meta", title="Senior Software Engineer",
         last_updated="2026-05-01"),
    dict(candidate_id="C03", full_name="Sindre Sorhus", email="sindre.s@example.com",
         phone="+1-415-555-0103", current_company="Independent", title="Open Source Maintainer",
         last_updated="2026-05-01"),
    dict(candidate_id="C04", full_name="Priya Nair", email="priya.nair@example.com",
         phone="+91-98765-10004", current_company="Razorpay", title="Backend Engineer",
         last_updated="2026-05-02"),
    dict(candidate_id="C05", full_name="Evan You", email="evan.y@example.com",
         phone="+1-415-555-0105", current_company="VoidZero", title="Founder",
         last_updated="2026-05-01"),
    dict(candidate_id="C07", full_name="Arjun Mehta", email="arjun.mehta@example.com",
         phone="+91-98765-10007", current_company="Flipkart", title="SDE 2",
         last_updated="2026-05-03"),
    dict(candidate_id="C08", full_name="Sara Khan", email="sara.khan@example.com",
         phone="", current_company="Zomato", title="Data Engineer",
         last_updated="2026-05-02"),
    dict(candidate_id="C09", full_name="Rohit Verma", email="rohit.verma@example.com",
         phone="+91-98765-10009", current_company="Swiggy", title="SRE",
         last_updated="2026-05-02"),
    dict(candidate_id="C10", full_name="TJ Holowaychuk", email="tj.h@example.com",
         phone="+1-415-555-0110", current_company="Independent", title="Open Source Engineer",
         last_updated="2026-05-01"),
    dict(candidate_id="C11", full_name="Meera Iyer", email="meera.iyer@example.com",
         phone="098765 10011", current_company="Paytm", title="ML Engineer",
         last_updated="2026-05-04"),
    dict(candidate_id="C12", full_name="Kent C. Dodds", email="kent.d@example.com",
         phone="+1-415-555-0112", current_company="Epic Web Dev", title="Educator",
         last_updated="2026-05-01"),
    # C13 has two rows: duplicate within same source, different phone, different last_updated
    dict(candidate_id="C13", full_name="Aditya Rao", email="aditya.rao@example.com",
         phone="+91-98765-10013", current_company="PhonePe", title="Backend Engineer",
         last_updated="2026-04-10"),
    dict(candidate_id="C13", full_name="Aditya Rao", email="aditya.rao@example.com",
         phone="+91-98765-99913", current_company="PhonePe", title="Backend Engineer",
         last_updated="2026-05-20"),
    dict(candidate_id="C15", full_name="Tom Preston-Werner", email="tom.pw@example.com",
         phone="+1-415-555-0115", current_company="Chatterbug", title="Co-founder",
         last_updated="2026-05-01"),
    # C16 has no email
    dict(candidate_id="C16", full_name="Neha Joshi", email="",
         phone="+91-98765-10016", current_company="Ola", title="Frontend Engineer",
         last_updated="2026-05-05"),
    # C17 and C18 are different people with similar names, must not merge
    dict(candidate_id="C17", full_name="Aman Sharma", email="aman.sharma17@example.com",
         phone="+91-98765-10017", current_company="Cred", title="Product Engineer",
         last_updated="2026-05-02"),
    dict(candidate_id="C18", full_name="Amann Sharma", email="amann.sharma18@example.com",
         phone="+91-98765-10018", current_company="Groww", title="Backend Engineer",
         last_updated="2026-05-02"),
    dict(candidate_id="C19", full_name="Divya Pillai", email="divya.pillai@example.com",
         phone="+91-98765-10019", current_company="Freshworks", title="Software Engineer",
         last_updated="2026-05-03"),
    dict(candidate_id="C20", full_name="Paul Irish", email="paul.i@example.com",
         phone="+1-415-555-0120", current_company="Google", title="Developer Advocate",
         last_updated="2026-05-01"),
]

# ATS JSON records: structured but semi-free, own field names, not all candidates present
ATS_RECORDS = [
    dict(candidate_id="C01", name="Linus Torvalds", email="linus.t@example.com",
         phone="+14155550101", role_title="Kernel Maintainer", company="Linux Foundation",
         skills=["c", "linux", "git"], last_updated="2026-05-01"),
    dict(candidate_id="C02", name="Dan Abramov", email="dan.a@example.com",
         phone="+14155550102", role_title="Staff Software Engineer", company="Meta",
         skills=["javascript", "react"], last_updated="2026-05-02"),
    dict(candidate_id="C04", name="Priya Nair", email="priya.nair@example.com",
         phone="+919876510004", role_title="Backend Engineer", company="Razorpay",
         skills=["java", "spring", "postgresql"], last_updated="2026-05-02"),
    dict(candidate_id="C05", name="Evan You", email="evan.y@example.com",
         phone="+14155550105", role_title="Founder", company="VoidZero",
         skills=["javascript", "vue", "rust"], last_updated="2026-05-01"),
    # C06 has no email here, must match via name+phone fallback
    dict(candidate_id="C06", name="Addy Osmani", email="", phone="+14155550106",
         role_title="Engineering Lead", company="Google",
         skills=["javascript", "performance"], last_updated="2026-05-01"),
    dict(candidate_id="C07", name="Arjun Mehta", email="arjun.mehta@example.com",
         phone="+919876510007", role_title="Senior SDE", company="Flipkart",
         skills=["python", "django"], last_updated="2026-05-03"),
    dict(candidate_id="C08", name="Sara Khan", email="sara.khan@example.com",
         phone="+919876510008", role_title="Data Engineer", company="Zomato",
         skills=["python", "spark", "airflow"], last_updated="2026-05-02"),
    # C09 ATS blob is intentionally malformed, written separately as raw text
    dict(candidate_id="C13", name="Aditya Rao", email="aditya.rao@example.com",
         phone="+919876599913", role_title="Backend Engineer", company="PhonePe",
         skills=["go", "kubernetes"], last_updated="2026-05-20"),
    dict(candidate_id="C17", name="Aman Sharma", email="aman.sharma17@example.com",
         phone="+919876510017", role_title="Product Engineer", company="Cred",
         skills=["kotlin", "android"], last_updated="2026-05-02"),
    dict(candidate_id="C18", name="Amann Sharma", email="amann.sharma18@example.com",
         phone="+919876510018", role_title="Backend Engineer", company="Groww",
         skills=["java", "kafka"], last_updated="2026-05-02"),
    dict(candidate_id="C19", name="Divya Pillai", email="divya.pillai@example.com",
         phone="+919876510019", role_title="Software Engineer II", company="Freshworks",
         skills=["reactjs", "node"], last_updated="2026-05-03"),
]

# resume text, free text per candidate, deliberately messy formatting where relevant
RESUMES = {
    "C01": "Linus Torvalds\nlinus.t@example.com | +1-415-555-0101\nKernel Maintainer, Linux Foundation\nExperience: Linux Foundation, Kernel Maintainer, 2005 - Present\nSkills: C, Linux, Git",
    "C03": "Sindre Sorhus\nsindre.s@example.com\nOpen Source Maintainer\nSkills: JavaScript, Node.js, npm packages\nExperience: Independent, Open Source Maintainer, 2010 - Present",
    "C04": "Priya Nair\npriya.nair@example.com | 9876510004\nBackend Engineer at Razorpay\nExperience: Razorpay, Backend Engineer, Jan 2023 - Present\nEducation: BTech Computer Science, NIT Trichy, 2022\nSkills: Java, Spring Boot, PostgreSQL",
    "C06": "Addy Osmani\nEngineering Lead, Google\nExperience: Google, Engineering Lead, 2017 - Present\nSkills: JavaScript, Web Performance",
    "C07": "Arjun Mehta\narjun.mehta@example.com\nPhone: +91 9876512345\nSDE 2 at Flipkart\nExperience: Flipkart, SDE 2, 03/2022 - Present\nSkills: Python, Django, REST APIs",
    "C09": "Rohit Verma\nrohit.verma@example.com | +91-98765-10009\nSRE at Swiggy\nExperience: Swiggy, Site Reliability Engineer, 2023-06 - Present\nSkills: Kubernetes, Prometheus, Go",
    "C11": "Meera Iyer\nmeera.iyer@example.com\nML Engineer at Paytm\nExperience: Paytm, ML Engineer, Feb 2023 - Present\nSkills: Python, TensorFlow",
    "C12": "Kent C. Dodds\nkent.d@example.com\nEducator, Epic Web Dev\nSkills: ReactJS, TestingLibrary, JavaScript\nExperience: Epic Web Dev, Educator, 2020 - Present",
    "C14": "",
    "C15": "Tom Preston-Werner\ntom.pw@example.com\nCo-founder, Chatterbug\nExperience: Chatterbug, Co-founder, 2016 - Present\nSkills: Ruby, Git",
    "C16": "Neha Joshi\nPhone: +91-98765-10016\nFrontend Engineer at Ola\nExperience: Ola, Frontend Engineer, 2022 - Present\nSkills: React, CSS",
    "C19": "Divya Pillai\ndivya.pillai@example.com\nSoftware Engineer II, Freshworks\nSkills: React.js, Node.js\nExperience: Freshworks, Software Engineer II, 2021 - Present",
    "C20": "Paul Irish\npaul.i@example.com\nDeveloper Advocate, Google\nExperience: Google, Developer Advocate, 2014 - Present\nSkills: JavaScript, DevTools",
}

# linkedin records: own field shapes, headline instead of title
LINKEDIN_RECORDS = [
    dict(candidate_id="C02", full_name="Dan Abramov", email="dan.a@example.com",
         headline="Software Engineer II", company="Meta", last_updated="2026-04-20"),
    dict(candidate_id="C10", full_name="TJ Holowaychuk", email="tj.h@example.com",
         headline="Open Source Engineer", company="Independent", last_updated="2026-04-15"),
    dict(candidate_id="C11", full_name="Meera Iyer", email="meera.iyer@example.com",
         headline="Machine Learning Engineer", company="Paytm", last_updated="2026-04-18"),
    dict(candidate_id="C19", full_name="Divya Pillai", email="divya.pillai@example.com",
         headline="Software Engineer II", company="Freshworks", last_updated="2026-04-22"),
]

RECRUITER_NOTES = {
    "C20": "Spoke to Paul on call. Strong DX background, very articulate. "
           "Mentioned interest in dev tooling roles. Notes from screening, 2026-05-10.",
}


def write_csv():
    path = SRC / "recruiter_csv" / "candidates.csv"
    fields = ["full_name", "email", "phone", "current_company", "title", "last_updated"]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in CSV_ROWS:
            writer.writerow({k: row[k] for k in fields})


def write_ats():
    path = SRC / "ats_json" / "candidates.json"
    records = [{k: v for k, v in r.items() if k != "candidate_id"} for r in ATS_RECORDS]
    path.write_text(json.dumps(records, indent=2))

    # C09: separate malformed blob, truncated/invalid JSON on purpose
    malformed_path = SRC / "ats_json" / "C09_malformed.json"
    malformed_path.write_text(
        '{"name": "Rohit Verma", "email": "rohit.verma@example.com", "phone": "+91-98765-10009", "role_title": "SRE", "skills": ["kubernetes", "go"'
    )


def write_resumes():
    for cid, text in RESUMES.items():
        path = SRC / "resumes" / f"{cid}.txt"
        path.write_text(text)


def write_linkedin():
    path = SRC / "linkedin" / "candidates.json"
    records = [{k: v for k, v in r.items() if k != "candidate_id"} for r in LINKEDIN_RECORDS]
    path.write_text(json.dumps(records, indent=2))


def write_recruiter_notes():
    for cid, text in RECRUITER_NOTES.items():
        path = SRC / "recruiter_notes" / f"{cid}.txt"
        path.write_text(text)


def main():
    write_csv()
    write_ats()
    write_resumes()
    write_linkedin()
    write_recruiter_notes()
    print("synthetic data written for all candidates")


if __name__ == "__main__":
    main()