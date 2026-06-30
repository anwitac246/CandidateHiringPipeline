# Multi-Source Candidate Data Transformer

A pipeline that ingests candidate data from multiple structured (CSV, ATS JSON) and unstructured (resumes, LinkedIn, GitHub, recruiter notes) sources, normalizes and merges the records using a deterministic trust hierarchy, resolves conflicts, handles edge cases, and projects the output to custom runtime configurations with validation.

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
  ATS JSON (5) > Recruiter CSV (4) > LinkedIn/GitHub (3) > Resume (2) > Recruiter Notes (1)
  ```
  For equal trust tiers, the record with the most recent `last_updated` date wins.
- **In-Source Deduplication**: If multiple records appear within the same source, the record with the newest timestamp is kept as active. The older record's conflicting field values are suppressed from the active profile and logged under `alternatives`.
- **Alternatives Log**: Lower-trust or older conflicting values are preserved in the `alternatives` block mapping the value, source, trust score, and suppression reason.
- **Confidence Scoring**: Calculated based on the number of sources, source trust values, present fields (penalties for missing name/email/phone/experience), and conflict counts.

---

## 3. Getting Started

### Installation
Prerequisites: Python 3.10+.
Install dependencies into your environment:
```bash
pip install -r requirements.txt
```

### Running Synthetic Data Generation
To regenerate the enriched synthetic candidate data:
```bash
python scripts/generate_user_data.py
```

### Generating the Technical Design PDF
To compile the Step 1 technical design one-pager:
```bash
python scripts/generate_pdf.py --name "Your Name" --email "your.email@example.com"
```
This writes a single-page PDF named `YourName_your.email@example.com_Eightfold.pdf`.

---

## 4. Running the CLI

Run the pipeline using the default output configuration:
```bash
python cli.py --sources data/sources --output data/output_default.json
```

Run the pipeline with a custom projection configuration (e.g., remapping fields and applying E.164/canonical normalizations):
```bash
python cli.py --sources data/sources --config data/custom_config.json --output data/output_custom.json
```

---

## 5. Running Tests

Run the unit test suite verifying normalization, projector, and missing field behaviors:
```bash
python -m unittest tests/test_pipeline.py
```

---

## 6. Running the Interactive UI

An interactive local UI is included to visualize unified profiles, decision logs, conflicts, and custom projection edits.

Start the local UI web server:
```bash
python ui_server.py
```
Open your browser and navigate to: **[http://localhost:8000](http://localhost:8000)**
- **Left Panel**: Click any candidate to view details. Items with overridden conflicts show an amber warning dot.
- **Center Tab 1 (Unified Profile)**: Rendered details, skills, timeline, and education.
- **Center Tab 2 (Provenance & Governance)**: Lists source decisions and overrides.
- **Right Panel (Config Editor & JSON)**: Select preset configurations or edit the JSON config directly. Click **Apply Config** to project.
