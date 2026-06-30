from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class LocationRecord(BaseModel):
    city: str | None = None
    region: str | None = None
    country: str | None = None


class LinksRecord(BaseModel):
    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None
    other: list[str] = Field(default_factory=list)


class SkillRecord(BaseModel):
    name: str
    confidence: float
    sources: list[str]


class ExperienceRecord(BaseModel):
    company: str | None = None
    title: str | None = None
    start: str | None = None
    end: str | None = None
    summary: str | None = None


class EducationRecord(BaseModel):
    institution: str | None = None
    degree: str | None = None
    field: str | None = None
    end_year: str | None = None


class ProvenanceEntry(BaseModel):
    field: str
    source: str
    method: str


class CandidateRecord(BaseModel):
    candidate_id: str
    full_name: str | None = None
    emails: list[str] = Field(default_factory=list)
    phones: list[str] = Field(default_factory=list)
    location: LocationRecord = Field(default_factory=LocationRecord)
    links: LinksRecord = Field(default_factory=LinksRecord)
    headline: str | None = None
    years_experience: float | None = None
    skills: list[SkillRecord] = Field(default_factory=list)
    experience: list[ExperienceRecord] = Field(default_factory=list)
    education: list[EducationRecord] = Field(default_factory=list)
    provenance: list[ProvenanceEntry] = Field(default_factory=list)
    overall_confidence: float = 0.0
    alternatives: dict[str, list[dict[str, Any]]] = Field(default_factory=dict)
    raw_notes: str | None = None
