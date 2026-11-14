"""Typed hand-offs. Nodes exchange data models rather than unstructured text."""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field


class JobSpec(BaseModel):
    job_id: str
    title: str
    requirements: list[str]
    budget: float
    connects_cost: int


class RiskReport(BaseModel):
    score: int = Field(ge=0, le=100)
    is_scam: bool
    flags: list[str] = []
    rationale: str


class EvidenceItem(BaseModel):
    id: str
    title: str
    excerpt: str
    skills: list[str]
    outcome: str


class FitReport(BaseModel):
    score: int = Field(ge=0, le=100)
    evidence: list[EvidenceItem]
    gaps: list[str]


class PriceQuote(BaseModel):
    recommended_bid: float
    rationale: str
    connects_worth_spending: bool


class ClaimCheck(BaseModel):
    claim: str
    status: Literal["supported", "partly_supported", "unsupported"]
    evidence_ids: list[str] = []


class ProposalDraft(BaseModel):
    id: str
    job_id: str
    body: str
    price: float
    claims: list[ClaimCheck]
    compliance_notes: list[str] = []
    status: Literal["draft", "awaiting_approval", "approved", "rejected"] = "draft"


class Decision(BaseModel):
    action: Literal["bid", "skip", "watch"]
    reason: str

