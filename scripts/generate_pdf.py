from __future__ import annotations

import argparse
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf(name: str, email: str, output_path: str) -> None:
    # 0.4 inch margins to ensure it fits on a single page with slightly larger font
    margin = 28  # points (72 points = 1 inch)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles to fit on a single page with slightly larger font sizes
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=16,
        textColor=colors.HexColor('#0F172A'),
        alignment=0, # Left aligned
        spaceAfter=2
    )
    
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor('#475569'),
        spaceAfter=8
    )
    
    sec_title_style = ParagraphStyle(
        'SecTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=13,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.0,
        leading=12.0,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=4
    )
    
    bullet_style = ParagraphStyle(
        'DocBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.0,
        leading=12.0,
        leftIndent=12,
        firstLineIndent=-8,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=2
    )
    
    story = []
    
    # Header block
    title_text = "<u><b>Multi-Source Candidate Data Transformer - Technical Design</b></u>"
    subtitle_text = f"Candidate: <b>{name}</b>   |   Email: <b>{email}</b>   |   Date: July 2026"
    story.append(Paragraph(title_text, title_style))
    story.append(Paragraph(subtitle_text, subtitle_style))
    
    # Divider line
    divider = Table([['']], colWidths=[556], rowHeights=[2.0])
    divider.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1E3A8A')),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(divider)
    story.append(Spacer(1, 4))
    
    # Section 1: Pipeline & Step Breakdown
    story.append(Paragraph("<u><b>1. System Architecture & Pipeline Breakdown</b></u>", sec_title_style))
    story.append(Paragraph(
        "The transformer operates as a deterministic multi-stage data processing pipeline. "
        "Separation of concerns is maintained between data ingestion, deduplication/merging, and custom schema projection:",
        body_style
    ))
    story.append(Paragraph(
        "<b>* Ingestion (Stage 1):</b> Independent, low-coupling source modules ingest files (structured and unstructured). "
        "Missing directories or garbage source formats (such as invalid JSON) are logged and skipped without halting the system.<br/>"
        "<b>* Normalization (Stage 2):</b> Low-level sanitization: phone numbers coerced to E.164; dates parsed and normalized to YYYY-MM; location strings split; skill names mapped to canonical representations using aliases.<br/>"
        "<b>* Merging & Deduplication (Stage 3):</b> Records are grouped by unique identity keys. Within-source duplicates are resolved, and cross-source fields are unified based on trust tiers. All modifications and overrides populate a provenance history.<br/>"
        "<b>* Projection & Validation (Stage 4):</b> Runtime configuration maps canonical records into targeted outputs. Fields are optionally filtered, remapped, normalized, or discarded (omit/null/error on missing) and validated against a schema.",
        bullet_style
    ))
    
    # Section 2: Canonical Output Schema & Normalizations
    story.append(Paragraph("<u><b>2. Canonical Internal Schema & Normalizations</b></u>", sec_title_style))
    story.append(Paragraph(
        "The pipeline standardizes candidate information into a Pydantic-based <i>CandidateRecord</i> representation:<br/>"
        "<b>* Dates:</b> Normalized to ISO YYYY-MM using regex heuristics, mapping short months (Jan) and full months (June).<br/>"
        "<b>* Phones:</b> Coerced to E.164 format (using +91 or +1 country prefixes, removing formatting spaces/dashes).<br/>"
        "<b>* Locations:</b> Parsed into a structured <i>LocationRecord</i> containing city, region, and ISO-3166 alpha-2 country codes.<br/>"
        "<b>* Skills:</b> Coerced to lowercase and canonicalized using an alias table (such as ReactJS/React.js to react, Node.js to node).",
        bullet_style
    ))
    
    # Section 3: Merge & Conflict-Resolution Policy
    story.append(Paragraph("<u><b>3. Identity Matching & Conflict-Resolution Policy</b></u>", sec_title_style))
    story.append(Paragraph(
        "<b>* Identity Keys:</b> Candidates are resolved using <i>email</i> as the primary matching key. A fallback match key of <i>name + normalized-phone</i> is applied to merge records lacking an email (such as resume or recruiter notes matches). Near-duplicates (like Aman vs Amann Sharma) are protected against incorrect merges.<br/>"
        "<b>* Trust-Tier Hierarchy:</b> Out-of-source conflicts are resolved using a predefined trust hierarchy rank: "
        "<b>Resume (5) > ATS JSON (4) > Recruiter CSV (3) > LinkedIn/GitHub (2) > Recruiter Notes (1)</b>. "
        "The highest-ranked source wins. For equal-trust conflicts, the most recently updated record (highest last_updated date) is chosen.<br/>"
        "<b>* Alternatives Logging:</b> Overridden or suppressed values are stored in the <i>alternatives</i> dictionary, documenting "
        "the value, source name, trust score, and suppression reason (such as lower_trust, lower_recency, or in_source_duplicate_older).<br/>"
        "<b>* In-Source Deduplication:</b> When duplicate rows appear in a single source, the most recent timestamp wins. "
        "The older values are suppressed from the active profile and registered as alternatives.",
        bullet_style
    ))
    
    # Section 4: Runtime Custom-Output Configuration (Projection & Validation)
    story.append(Paragraph("<u><b>4. Runtime Schema Projection & Validation</b></u>", sec_title_style))
    story.append(Paragraph(
        "The system accepts a runtime configuration mapping that transforms canonical records without altering codebase rules:<br/>"
        "<b>* Paths:</b> Resolves nested attributes (like <i>location.city</i>), array indices (like <i>emails[0]</i>), and collections (like <i>skills[].name</i>).<br/>"
        "<b>* Missing Policy:</b> Handles missing data gracefully according to the configuration's <i>on_missing</i> behavior: "
        "<b>null</b> (keeps field as null), <b>omit</b> (removes key from output), or <b>error</b> (raises a descriptive ValueError).<br/>"
        "<b>* Validation:</b> Projects the configuration mapping and validates the result against the target schema types "
        "(string, number, object, string[], object[]) to guarantee structural safety before returning.",
        bullet_style
    ))
    
    # Section 5: Edge Cases & Scope Tradeoffs
    story.append(Paragraph("<u><b>5. Critical Edge Cases & Scope Trade-offs under Time Pressure</b></u>", sec_title_style))
    story.append(Paragraph(
        "<b>* Handled Edge Cases:</b> (1) Semi-structured JSON truncation (C09) and empty resumes (C14) are handled without crashes; "
        "(2) Candidates matching via fallbacks without email (C06, C16) merge correctly; "
        "(3) In-source duplicates (C13) resolve phone conflicts while preserving the older number in alternatives.<br/>"
        "<b>* Time-Pressure Trade-offs:</b> To prioritize pipeline correctness, we chose: "
        "(1) Regex-based heuristic parser for text resumes rather than heavy LLM/NLP tools; "
        "(2) Simple canonical skill mapping instead of complex taxonomy matching; "
        "(3) Command-line interface instead of an interactive web frontend.",
        bullet_style
    ))
    
    # Build Document
    doc.build(story)

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Eightfold Technical Design PDF")
    parser.add_argument("--name", type=str, default="Candidate User", help="Your Full Name")
    parser.add_argument("--email", type=str, default="candidate@example.com", help="Your Email")
    parser.add_argument("--output", type=str, default=None, help="Output PDF Path")
    
    args = parser.parse_args()
    
    out_path = args.output
    if not out_path:
        clean_name = args.name.replace(" ", "")
        clean_email = args.email.replace(" ", "")
        out_path = f"{clean_name}_{clean_email}_Eightfold.pdf"
        
    try:
        generate_pdf(args.name, args.email, out_path)
        print(f"Technical design one-pager generated: {out_path}")
    except Exception as exc:
        print(f"Error generating PDF: {exc}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
