# Multi-Source Candidate Data Transformer

A pipeline that ingests candidate data from multiple structured (CSV, ATS JSON) and unstructured (resumes, LinkedIn, GitHub, recruiter notes) sources, normalizes and merges the records using a deterministic trust hierarchy, resolves conflicts, handles edge cases, and projects the output to custom runtime configurations with validation.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Data validation & schemas | [Pydantic v2](https://docs.pydantic.dev/latest/) |
| Environment variables | [python-dotenv](https://pypi.org/project/python-dotenv/) |
| GitHub API | `urllib` (stdlib, no extra dependencies) |
| Web UI server | `http.server` (stdlib) |
| Tests | `unittest` + `pytest` |
| Data formats | JSON, CSV, plain-text resumes |

No external web framework, no ORM, no database. The pipeline is a pure Python process.


https://github.com/user-attachments/assets/fb3fa98e-be11-4076-8211-91e791d7cbe6




---

## 1. System Architecture

The pipeline consists of the following processing stages:

```
Ingest Sources ──► Extract dicts ──► Normalize ──► Merge/Deduplicate ──► Project ──► Validate ──► Output JSON
```

- **Ingestion (`src/ingest/`)**: Independent modules read different file types. Missing paths or malformed formats are caught, logged, and skipped without halting pipeline execution.
- **Normalization (`src/normalizer.py`)**: Sanitizes formats (phones to E.164, dates to YYYY-MM, location split, skills mapped to canonical aliases).
- **Merging & Conflict Resolution (`src/merger.py`)**: Unifies records using identity keys, resolves conflicts based on trust rank, and compiles alternatives/provenance.
- **Projection & Validation (`src/projector.py`, `src/validator.py`)**: Maps canonical records to custom formats at runtime, handling missing-value options (null, omit, error) and validating types.

---

## 2. Merge & Conflict-Resolution Policies

- **Matching Key**: Candidate records are grouped using *email* as the primary key. If a record lacks an email (e.g. resumes, notes, or GitHub files), it matches using a fallback of *name + normalized-phone*. If no matches exist, a new group is created.
- **Trust Tiers**: When sources contain conflicting values, the highest tier wins:
  ```
  Resume (5) > ATS JSON (4) > Recruiter CSV (3) > LinkedIn/GitHub (2) > Recruiter Notes (1)
  ```
  For equal trust tiers, the record with the most recent `last_updated` date wins.
- **In-Source Deduplication**: If multiple records appear within the same source, the record with the newest timestamp is kept as active. The older record's conflicting field values are suppressed from the active profile and logged under `alternatives`.
- **Alternatives Log**: Lower-trust or older conflicting values are preserved in the `alternatives` block mapping the value, source, trust score, and suppression reason.
- **Confidence Scoring**: Calculated based on the number of sources, source trust values, present fields (bonuses for name/email/phone/experience/skills), and conflict count penalties.

---

## 3. Getting Started

### Prerequisites
- Python 3.10+
- A GitHub personal access token (classic, no scopes required) — only needed if re-fetching GitHub profiles

### Installation

```bash
pip install -r requirements.txt
```

### Regenerating Synthetic Data

To regenerate the enriched synthetic candidate data from scratch:

```bash
python scripts/generate_user_data.py
```

This writes all source files under `data/sources/` (CSV, ATS JSON, resumes, LinkedIn, recruiter notes, candidate index).

### Fetching GitHub Profiles

The GitHub profiles under `data/sources/github/` are pre-fetched and committed. To re-fetch them from the live GitHub API:

1. Generate a classic GitHub personal access token at [github.com/settings/tokens](https://github.com/settings/tokens). No scopes are required — public profile data only.

2. Set the token as an environment variable:
   ```bash
   # Linux / macOS
   export GITHUB_TOKEN=ghp_xxxxxxxxxxxx

   # Windows (PowerShell)
   $env:GITHUB_TOKEN = "ghp_xxxxxxxxxxxx"
   ```
   Or add it to a `.env` file in the project root:
   ```
   GITHUB_TOKEN=ghp_xxxxxxxxxxxx
   ```

3. Run the fetcher:
   ```bash
   python scripts/github_user_fetcher.py
   ```

   This calls the GitHub API for each GitHub-linked candidate, writes one JSON file per candidate to `data/sources/github/`, and sleeps 1 second between requests to respect rate limits.



## 4. Running the CLI

Run the pipeline using the default output configuration:
```bash
python cli.py --output output/candidates_final.json
```

Run the pipeline with a custom projection configuration (e.g., remapping fields and applying E.164/canonical normalizations):
```bash
python cli.py --config path/to/custom_config.json --output output/candidates_custom.json
```

---

## 5. Running Tests

Run the unit test suite verifying normalization, projector, and missing field behaviors:
```bash
python -m pytest tests/test_pipeline.py -v
```

---

## 6. Running the Interactive UI

An interactive local UI is included to visualize the full pipeline run step by step — raw source data, normalized records, merge decisions, conflict resolution, and the final projected output.

Start the local UI web server:
```bash
python ui_server.py
```
Open your browser and navigate to: **[http://localhost:8000](http://localhost:8000)**

- **Left Panel**: Click any candidate to view details. Items with overridden conflicts show an amber warning dot.
- **Center Tab 1 (Unified Profile)**: Rendered details, skills, timeline, and education.
- **Center Tab 2 (Provenance & Governance)**: Lists source decisions and overrides.
- **Right Panel (Config Editor & JSON)**: Select preset configurations or edit the JSON config directly. Click **Apply Config** to project.
