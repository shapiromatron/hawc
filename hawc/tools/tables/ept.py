from enum import Enum, IntEnum
from typing import List

from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from pydantic import BaseModel, Field

from .base import BaseCell, BaseCellGroup, BaseTable
from .generic import GenericCell
from .parser import QuillParser, tag_wrapper, ul_wrapper


class JudgementTexts(Enum):
    Robust = ("⊕⊕⊕", "Robust")
    Moderate = ("⊕⊕⊙", "Moderate")
    Slight = ("⊕⊙⊙", "Slight")
    Indeterminate = ("⊙⊙⊙", "Indeterminate")
    NoEffect = ("⊝⊝⊝", "Evidence of no effect")


class SummaryJudgementTexts(Enum):
    Confident = ("⊕⊕⊕", "Evidence demonstrates")
    Likely = ("⊕⊕⊙", "Evidence indicates (likely)")
    Suggests = ("⊕⊙⊙", "Evidence suggests")
    Inadequate = ("⊙⊙⊙", "Evidence inadequate")
    NoEffect = ("⊝⊝⊝", "Strong evidence supports no effect")


class JudgementChoices(IntEnum):
    Robust = 30
    Moderate = 20
    Slight = 10
    Indeterminate = 1
    NoEffect = -10
    NoJudgement = 900
    Custom = 910


class SummaryJudgementChoices(IntEnum):
    Confident = 30
    Likely = 20
    Suggests = 10
    Inadequate = 1
    NoEffect = -10
    NoJudgement = 900
    Custom = 910


## Summary judgement


class SummaryJudgementCell(BaseCell):

    judgement: SummaryJudgementChoices
    custom_judgement_icon: str = ""
    custom_judgement_label: str = ""

    description: str
    human_relevance: str
    cross_stream_coherence: str
    susceptibility: str

    hide_content: bool

    def judgement_html(self):
        if self.judgement == SummaryJudgementChoices.NoJudgement:
            return ""
        if self.judgement == SummaryJudgementChoices.Custom:
            return tag_wrapper(self.custom_judgement_icon, "p",) + tag_wrapper(
                self.custom_judgement_label, "p", "em"
            )
        icon = SummaryJudgementTexts[self.judgement.name].value[0]
        label = SummaryJudgementTexts[self.judgement.name].value[1]
        return tag_wrapper(icon, "p",) + tag_wrapper(label, "p", "em")

    def to_docx(self, block):
        text = ""
        text += self.judgement_html()
        text += tag_wrapper("\nPrimary basis:", "p", "em")
        text += self.description
        text += tag_wrapper("\nHuman relevance:", "p", "em")
        text += self.human_relevance
        text += tag_wrapper("\nCross-stream coherence:", "p", "em")
        text += self.cross_stream_coherence
        text += tag_wrapper("\nSusceptible populations and lifestages:", "p", "em")
        text += self.susceptibility
        parser = QuillParser()
        parser.feed(text, block)
        if self.judgement != SummaryJudgementChoices.NoJudgement:
            for paragraph in block.paragraphs[0:2]:
                paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER


## Evidence cells


class EvidenceCell(BaseCell):
    column: int = 0

    description: str

    def to_docx(self, block):
        text = self.description
        parser = QuillParser()
        return parser.feed(text, block)


class SummaryCell(BaseCell):
    column: int = 1

    findings: str

    def to_docx(self, block):
        parser = QuillParser()
        return parser.feed(self.findings, block)


class FactorLabel(Enum):
    NoFactors = "No factors noted"
    UpConsistency = "Consistency"
    UpDoseGradient = "Dose - response gradient"
    UpCoherence = "Coherence of effects"
    UpEffect = "Large or concerning magnitude of effect"
    UpPlausible = "Mechanistic evidence providing plausibility"
    UpConfidence = "Medium or high confidence studies"
    UpOther = ""
    DownConsistency = "Unexplained inconsistency"
    DownImprecision = "Imprecision"
    DownCoherence = "Lack of expected coherence"
    DownImplausible = "Evidence demonstrating implausibility"
    DownConfidence = "Low confidence studies"
    DownInterpretation = "Interpretation limitations"
    DownOther = ""


class FactorType(IntEnum):
    NoFactors = 0
    UpConsistency = 20
    UpDoseGradient = 30
    UpCoherence = 40
    UpEffect = 50
    UpPlausible = 60
    UpConfidence = 70
    UpOther = 100
    DownConsistency = -20
    DownImprecision = -30
    DownCoherence = -40
    DownImplausible = -50
    DownConfidence = -60
    DownInterpretation = -70
    DownOther = -100


class Factor(BaseModel):
    key: FactorType
    short_description: str
    long_description: str

    def to_html(self):
        label = FactorLabel[self.key.name].value
        if label:
            return tag_wrapper(label, "em") + " - " + self.short_description
        else:
            return self.short_description


class FactorsCell(BaseCell):
    factors: List[Factor]
    text: str

    def to_docx(self, block):
        factors = [factor.to_html() for factor in self.factors]
        text = ""
        if len(factors):
            text = ul_wrapper(factors)
        text += self.text
        parser = QuillParser()
        return parser.feed(text, block)


class CertainFactorsCell(FactorsCell):
    column: int = 2


class UncertainFactorsCell(FactorsCell):
    column: int = 3


class JudgementCell(BaseCell):
    column: int = 4

    judgement: JudgementChoices
    custom_judgement_icon: str = ""
    custom_judgement_label: str = ""

    description: str

    def judgement_html(self):
        if self.judgement == JudgementChoices.NoJudgement:
            return ""
        if self.judgement == JudgementChoices.Custom:
            return tag_wrapper(self.custom_judgement_icon, "p",) + tag_wrapper(
                self.custom_judgement_label, "p", "em"
            )
        icon = JudgementTexts[self.judgement.name].value[0]
        label = JudgementTexts[self.judgement.name].value[1]
        return tag_wrapper(icon, "p",) + tag_wrapper(label, "p", "em")

    def to_docx(self, block):
        text = self.judgement_html() + self.description
        parser = QuillParser()
        parser.feed(text, block)
        if self.judgement != JudgementChoices.NoJudgement:
            for paragraph in block.paragraphs[0:2]:
                paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER


## Mechanistic cells


class MechanisticEvidenceCell(BaseCell):
    column: int = 0

    description: str

    def to_docx(self, block):
        parser = QuillParser()
        return parser.feed(self.description, block)


class MechanisticSummaryCell(BaseCell):
    column: int = 1
    col_span: int = 3

    findings: str

    def to_docx(self, block):
        parser = QuillParser()
        return parser.feed(self.findings, block)


class MechanisticJudgementCell(BaseCell):
    column: int = 4

    description: str

    def to_docx(self, block):
        parser = QuillParser()
        return parser.feed(self.description, block)


## Rows


class EvidenceRow(BaseCellGroup):
    evidence: EvidenceCell
    summary: SummaryCell
    certain_factors: CertainFactorsCell
    uncertain_factors: UncertainFactorsCell
    judgement: JudgementCell

    def _set_cells(self):
        self.cells = [
            self.evidence,
            self.summary,
            self.certain_factors,
            self.uncertain_factors,
            self.judgement,
        ]


class MechanisticRow(BaseCellGroup):
    evidence: MechanisticEvidenceCell
    summary: MechanisticSummaryCell
    judgement: MechanisticJudgementCell

    def _set_cells(self):
        self.cells = [
            self.evidence,
            self.summary,
            self.judgement,
        ]


class EvidenceGroup(BaseCellGroup):
    title: str
    cell_rows: List[EvidenceRow] = Field([], alias="rows")
    merge_judgement: bool
    hide_content: bool
    no_content_text: str

    def _set_cells(self):
        cells = []
        cells.append(GenericCell.parse_args(True, 0, 0, 1, 5, tag_wrapper(self.title, "h2")))

        if len(self.cell_rows) == 0:
            text = tag_wrapper(self.no_content_text, "p", "em")
            cells.append(GenericCell.parse_args(True, 1, 0, 1, 5, text))
        elif self.merge_judgement:
            self.cell_rows[0].judgement.row_span = len(self.cell_rows)
            self.cell_rows[0].add_offset(row=1)
            cells.extend(self.cell_rows[0].cells)
            for index, row in enumerate(self.cell_rows[1:]):
                row.add_offset(row=index + 2)
                cells.extend(row.cells[:-1])
        else:
            for index, row in enumerate(self.cell_rows):
                row.add_offset(row=index + 1)
                cells.extend(row.cells)
        self.cells = cells


class MechanisticGroup(BaseCellGroup):
    title: str
    col_header_1: str
    cell_rows: List[MechanisticRow] = Field([], alias="rows")
    merge_judgement: bool
    hide_content: bool
    no_content_text: str

    @property
    def column_headers(self):
        text1 = tag_wrapper(self.col_header_1, "p", "strong")
        text2 = tag_wrapper("Summary of key findings and interpretation", "p", "strong")
        text3 = tag_wrapper("Judgment(s) and rationale", "p", "strong")
        return [
            GenericCell.parse_args(True, 1, 0, 1, 1, text1),
            GenericCell.parse_args(True, 1, 1, 1, 3, text2,),
            GenericCell.parse_args(True, 1, 4, 1, 1, text3),
        ]

    def _set_cells(self):
        cells = []
        cells.append(GenericCell.parse_args(True, 0, 0, 1, 5, tag_wrapper(self.title, "h2")))
        cells.extend(self.column_headers)

        if len(self.cell_rows) == 0:
            text = tag_wrapper(self.no_content_text, "p", "em")
            cells.append(GenericCell.parse_args(True, 2, 0, 1, 5, text))
        elif self.merge_judgement:
            self.cell_rows[0].judgement.row_span = len(self.cell_rows)
            self.cell_rows[0].add_offset(row=2)
            cells.extend(self.cell_rows[0].cells)
            for index, row in enumerate(self.cell_rows[1:]):
                row.add_offset(row=index + 3)
                cells.extend(row.cells[:-1])
        else:
            for index, row in enumerate(self.cell_rows):
                row.add_offset(row=index + 2)
                cells.extend(row.cells)
        self.cells = cells


## Table


class EvidenceProfileTable(BaseTable):
    exposed_human: EvidenceGroup
    animal: EvidenceGroup
    mechanistic: MechanisticGroup
    summary_judgement: SummaryJudgementCell

    @property
    def column_headers(self):
        return [
            GenericCell.parse_args(
                True, 1, 0, 1, 1, tag_wrapper("Studies, outcomes, and confidence", "p", "strong")
            ),
            GenericCell.parse_args(
                True, 1, 1, 1, 1, tag_wrapper("Summary of key findings", "p", "strong")
            ),
            GenericCell.parse_args(
                True, 1, 2, 1, 1, tag_wrapper("Factors that increase certainty", "p", "strong")
            ),
            GenericCell.parse_args(
                True, 1, 3, 1, 1, tag_wrapper("Factors that decrease certainty", "p", "strong")
            ),
            GenericCell.parse_args(
                True, 1, 4, 1, 1, tag_wrapper("Judgment(s) and rationale", "p", "strong")
            ),
        ]

    def _set_cells(self):
        cells = []
        hide_evidence = self.exposed_human.hide_content and self.animal.hide_content

        if not (hide_evidence and self.mechanistic.hide_content):
            text = tag_wrapper("Evidence Summary and Interpretation", "h1")
            cells.append(GenericCell.parse_args(True, 0, 0, 1, 5, text))
        rows = 1

        if not hide_evidence:
            cells.extend(self.column_headers)
            rows = 2
        if not self.exposed_human.hide_content:
            self.exposed_human.add_offset(row=rows)
            cells.extend(self.exposed_human.cells)
            rows = self.exposed_human.rows
        if not self.animal.hide_content:
            self.animal.add_offset(row=rows)
            cells.extend(self.animal.cells)
            rows = self.animal.rows
        if not self.mechanistic.hide_content:
            self.mechanistic.add_offset(row=rows)
            cells.extend(self.mechanistic.cells)
            rows = self.mechanistic.rows

        if not self.summary_judgement.hide_content:
            text = tag_wrapper("Inferences and Summary Judgment", "h1")
            if hide_evidence and self.mechanistic.hide_content:
                cells.append(GenericCell.parse_args(True, 0, 0, 1, 1, text))
                self.summary_judgement.row = 1
                self.summary_judgement.column = 0
                cells.append(self.summary_judgement)
            else:
                header_row_span = 2 if not hide_evidence else 1
                cells.append(GenericCell.parse_args(True, 0, 5, header_row_span, 1, text))
                self.summary_judgement.row = header_row_span
                self.summary_judgement.column = 5
                self.summary_judgement.row_span = rows - header_row_span
                cells.append(self.summary_judgement)

        self.cells = cells

    @classmethod
    def get_default_props(cls):
        return {
            "exposed_human": {
                "title": "Evidence from studies of exposed humans",
                "rows": [
                    {
                        "summary": {"findings": "<p></p>"},
                        "evidence": {"description": "<p><em>No evidence available</em></p>"},
                        "judgement": {
                            "judgement": JudgementChoices.Indeterminate,
                            "description": "<p></p>",
                            "custom_judgement_icon": "",
                            "custom_judgement_label": "",
                        },
                        "certain_factors": {"text": "<p></p>", "factors": []},
                        "uncertain_factors": {"text": "<p></p>", "factors": []},
                    }
                ],
                "merge_judgement": True,
                "hide_content": False,
                "no_content_text": "No evidence available",
            },
            "animal": {
                "title": "Evidence from animal studies",
                "rows": [
                    {
                        "summary": {"findings": "<p></p>"},
                        "evidence": {"description": "<p><em>No evidence available</em></p>"},
                        "judgement": {
                            "judgement": JudgementChoices.Indeterminate,
                            "description": "<p></p>",
                            "custom_judgement_icon": "",
                            "custom_judgement_label": "",
                        },
                        "certain_factors": {"text": "<p></p>", "factors": []},
                        "uncertain_factors": {"text": "<p></p>", "factors": []},
                    }
                ],
                "merge_judgement": True,
                "hide_content": False,
                "no_content_text": "No evidence available",
            },
            "mechanistic": {
                "title": "Mechanistic evidence and supplemental information",
                "col_header_1": "Biological events or pathways",
                "rows": [],
                "merge_judgement": True,
                "hide_content": False,
                "no_content_text": "No evidence available",
            },
            "summary_judgement": {
                "judgement": SummaryJudgementChoices.Inadequate,
                "custom_judgement_icon": "",
                "custom_judgement_label": "",
                "description": "<p></p>",
                "human_relevance": "<p></p>",
                "cross_stream_coherence": "<p></p>",
                "susceptibility": "<p></p>",
                "hide_content": False,
            },
        }
