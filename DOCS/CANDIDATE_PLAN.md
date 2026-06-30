# Candidate Plan

20 candidates total. 8 are linked to real public GitHub profiles (fetched live
from the GitHub API). 12 are fully synthetic. Every candidate is built to
demonstrate at least one specific edge case. A few are "clean" candidates with
no conflicts, to prove the happy path works.

| ID  | Sources present                              | GitHub-linked | Edge case(s) demonstrated |
|-----|-----------------------------------------------|---------------|----------------------------|
| C01 | csv, ats, github, resume                       | torvalds      | Clean happy path, all sources agree |
| C02 | csv, ats, github, linkedin                     | gaearon       | Field conflict, same confidence tier (title differs CSV vs LinkedIn) |
| C03 | csv, github, resume                            | sindresorhus  | Field completion only (skills only on GitHub) |
| C04 | csv, ats, resume                               | -             | No GitHub source at all (missing source) |
| C05 | csv, ats, github                               | yyx990803     | No resume (missing source) |
| C06 | ats, github, resume                            | addyosmani    | No CSV; matched via name+phone fallback (no email in ATS) |
| C07 | csv, resume                                    | -             | Field conflict, different confidence tier (phone differs, CSV wins) |
| C08 | csv, ats                                       | -             | Empty/blank phone field in CSV |
| C09 | csv, ats, resume                               | -             | Garbage/malformed JSON in ATS blob |
| C10 | csv, github, linkedin                          | tj            | Inconsistent date formats across 3 sources |
| C11 | csv, resume, linkedin                          | -             | Inconsistent phone formats needing E.164 normalization |
| C12 | csv, github, resume                            | kentcdodds    | Non-canonical skill name variants (ReactJS / React.js / react) |
| C13 | csv (2 rows, duplicate), ats                   | -             | Field present in zero sources (location null) + duplicate CSV rows for same person (different phone, different last_updated) |
| C14 | resume (corrupt/empty text)                    | -             | Fully malformed source, must degrade gracefully not crash |
| C15 | csv, ats, github, resume                       | mojombo       | Clean happy path, second instance |
| C16 | csv (no email), resume                         | -             | No-email candidate, name+phone fallback match |
| C17 | csv, ats                                       | -             | Near-duplicate name of C18, must NOT merge (different person) |
| C18 | csv, ats                                       | -             | Near-duplicate name of C17, must NOT merge (different person) |
| C19 | csv, ats, resume, linkedin                     | -             | Field conflict, same tier + non-canonical skills combined |
| C20 | csv, github, resume, recruiter_notes.txt       | paulirish     | Recruiter free-text notes as an extra unstructured source |

Note: github usernames fetched are torvalds, gaearon, sindresorhus, yyx990803,
addyosmani, tj, kentcdodds, mojombo, paulirish (9 real profiles total, one per
GitHub-linked candidate, all distinct).

## Source trust tiers (for confidence scoring)
1. ATS JSON (highest - internal system of record)
2. Recruiter CSV (high - human-entered but structured)
3. LinkedIn fields (medium)
4. GitHub profile (medium - good for skills/bio, not for title/experience)
5. Resume (medium-low - free text, parsing risk)
6. Recruiter notes .txt (lowest - informal, free text)

## Edge case 13: duplicate records within a single source
A candidate may appear more than once within the same source (e.g. CSV has
two rows for the same person from separate applications). Resolution policy:
the record with the most recent timestamp (last_updated / application_date
field) wins as the active value for that source. The older record's
conflicting field(s) are preserved in provenance as a suppressed alternative,
tagged with its own timestamp, same as a cross-source conflict. This requires
every source record to carry a timestamp field; this is a stated assumption
in the design doc. Demonstrated by C13 (two CSV rows, different phone
numbers, different last_updated dates).