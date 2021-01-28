from typing import List

from pydantic import BaseModel

from .base import BaseCell, BaseTable

## Summary judgement


class SummaryJudgementCell(BaseCell):
    judgement: str
    description: str
    human_relevance: str
    cross_stream_coherence: str
    susceptibility: str


## Evidence cells


class EvidenceCell(BaseCell):
    evidence: str
    confidence: str
    optional: str


class CertainFactorsCell(BaseCell):
    factors: List[str]


class UncertainFactorsCell(BaseCell):
    factors: List[str]


class SummaryCell(BaseCell):
    findings: str


class JudgementCell(BaseCell):
    judgement: str
    description: str


## Mechanistic cells


class MechanisticEvidenceCell(BaseCell):
    description: str


class MechanisticSummaryCell(BaseCell):
    findings: str


class MechanisticJudgementCell(BaseCell):
    description: str


## Rows


class EvidenceRow(BaseModel):
    evidence: EvidenceCell
    certain_factors: CertainFactorsCell
    uncertain_factors: UncertainFactorsCell
    summary: SummaryCell
    judgement: JudgementCell


class MechanisticRow(BaseModel):
    evidence: MechanisticEvidenceCell
    summary: MechanisticSummaryCell
    judgement: MechanisticJudgementCell


## Table


class EvidenceProfileTable(BaseTable):
    exposed_human_title: str
    exposed_human_rows: List[EvidenceRow]

    animal_title: str
    animal_rows: List[EvidenceRow]

    mechanistic_title: str
    mechanistic_rows: List[MechanisticRow]
