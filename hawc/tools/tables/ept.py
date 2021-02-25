from typing import List

from .base import BaseCell, BaseCellGroup, BaseTable
from .generic import GenericCell
from .parser import QuillParser, strip_tags, tag_wrapper, ul_wrapper

## Summary judgement


class SummaryJudgementCell(BaseCell):
    row: int = 1
    column: int = 5

    judgement: str
    description: str
    human_relevance: str
    cross_stream_coherence: str
    susceptibility: str

    def to_docx(self, block):
        text = ""
        text += self.judgement
        text += tag_wrapper("\nPrimary basis:", "p", "em")
        text += self.description
        text += tag_wrapper("\nHuman relevance:", "p", "em")
        text += self.human_relevance
        text += tag_wrapper("\nCross-stream coherence:", "p", "em")
        text += self.cross_stream_coherence
        text += tag_wrapper("\nSusceptible populations and lifestages:", "p", "em")
        text += self.susceptibility
        parser = QuillParser()
        return parser.feed(text, block)


## Evidence cells


class EvidenceCell(BaseCell):
    column: int = 0

    evidence: str
    confidence: str
    optional: str

    def to_docx(self, block):
        text = self.evidence + self.confidence + self.optional
        parser = QuillParser()
        return parser.feed(text, block)


class CertainFactorsCell(BaseCell):
    column: int = 1

    factors: List[str]

    def to_docx(self, block):
        factors = [strip_tags(factor, "p") for factor in self.factors]
        text = ul_wrapper(factors)
        parser = QuillParser()
        return parser.feed(text, block)


class UncertainFactorsCell(BaseCell):
    column: int = 2

    factors: List[str]

    def to_docx(self, block):
        factors = [strip_tags(factor, "p") for factor in self.factors]
        text = ul_wrapper(factors)
        parser = QuillParser()
        return parser.feed(text, block)


class SummaryCell(BaseCell):
    column: int = 3

    findings: str

    def to_docx(self, block):
        parser = QuillParser()
        return parser.feed(self.findings, block)


class JudgementCell(BaseCell):
    column: int = 4

    judgement: str
    description: str

    def to_docx(self, block):
        text = self.judgement + self.description
        parser = QuillParser()
        return parser.feed(text, block)


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
    certain_factors: CertainFactorsCell
    uncertain_factors: UncertainFactorsCell
    summary: SummaryCell
    judgement: JudgementCell

    def _set_cells(self):
        self.cells = [
            self.evidence,
            self.certain_factors,
            self.uncertain_factors,
            self.summary,
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
    cell_rows: List[EvidenceRow] = []
    merge_judgement: bool = True

    def column_headers(self):
        return [
            GenericCell.parse_args(
                True, 1, 0, 1, 1, tag_wrapper("Studies and confidence", "p", "strong")
            ),
            GenericCell.parse_args(
                True, 1, 1, 1, 1, tag_wrapper("Factors that increase certainty", "p", "strong")
            ),
            GenericCell.parse_args(
                True, 1, 2, 1, 1, tag_wrapper("Factors that decrease certainty", "p", "strong")
            ),
            GenericCell.parse_args(
                True, 1, 3, 1, 1, tag_wrapper("Summary and key findings", "p", "strong")
            ),
            GenericCell.parse_args(
                True, 1, 4, 1, 1, tag_wrapper("Evidence stream judgement", "p", "strong")
            ),
        ]

    def _set_cells(self):
        cells = []
        cells.append(GenericCell.parse_args(True, 0, 0, 1, 5, tag_wrapper(self.title, "h2")))
        cells.extend(self.column_headers())

        if len(self.cell_rows) == 0:
            text = tag_wrapper("No data available", "p", "em")
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


class MechanisticGroup(BaseCellGroup):
    title: str
    cell_rows: List[MechanisticRow] = []
    merge_judgement: bool = True

    def column_headers(self):
        text1 = tag_wrapper("Biological events or pathways", "p", "strong")
        text2 = tag_wrapper(
            "Summary of key findings, interpretation, and limitations", "p", "strong"
        )
        text3 = tag_wrapper("Evidence stream judgement", "p", "strong")
        return [
            GenericCell.parse_args(True, 1, 0, 1, 1, text1),
            GenericCell.parse_args(True, 1, 1, 1, 3, text2,),
            GenericCell.parse_args(True, 1, 4, 1, 1, text3),
        ]

    def _set_cells(self):
        cells = []
        cells.append(GenericCell.parse_args(True, 0, 0, 1, 5, tag_wrapper(self.title, "h2")))
        cells.extend(self.column_headers())

        if len(self.cell_rows) == 0:
            text = tag_wrapper("No data available", "p", "em")
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

    def _set_cells(self):
        cells = []
        text = tag_wrapper("Evidence Stream Summary and Interpretation", "h1")
        cells.append(GenericCell.parse_args(True, 0, 0, 1, 5, text))
        text = tag_wrapper("Evidence Integration Summary Judgement", "h1")
        cells.append(GenericCell.parse_args(True, 0, 5, 1, 1, text))
        self.exposed_human.add_offset(row=1)
        cells.extend(self.exposed_human.cells)
        self.animal.add_offset(row=self.exposed_human.rows)
        cells.extend(self.animal.cells)
        self.mechanistic.add_offset(row=self.animal.rows)
        cells.extend(self.mechanistic.cells)
        self.summary_judgement.row_span = self.mechanistic.rows - 1
        cells.append(self.summary_judgement)
        self.cells = cells

    @classmethod
    def build_default(cls):
        return cls.parse_obj(
            {
                "exposed_human": {
                    "title": "exposed human",
                    "cell_rows": [
                        {
                            "evidence": {
                                "evidence": "<p>asdf</p>",
                                "confidence": "<p>asdf</p>",
                                "optional": "<p>asdf</p>",
                            },
                            "certain_factors": {"factors": ["<p>asdf</p>", "<p>asdf</p>"]},
                            "uncertain_factors": {"factors": ["<p>asdf</p>", "<p>asdf</p>"]},
                            "summary": {"findings": "<p>asdf</p>"},
                            "judgement": {"judgement": "<p>asdf</p>", "description": "<p>asdf</p>"},
                        },
                        {
                            "evidence": {
                                "evidence": "<p>asdf</p>",
                                "confidence": "<p>asdf</p>",
                                "optional": "<p>asdf</p>",
                            },
                            "certain_factors": {"factors": ["<p>asdf</p>", "<p>asdf</p>"]},
                            "uncertain_factors": {"factors": ["<p>asdf</p>", "<p>asdf</p>"]},
                            "summary": {"findings": "<p>asdf</p>"},
                            "judgement": {"judgement": "<p>asdf</p>", "description": "<p>asdf</p>"},
                        },
                    ],
                },
                "animal": {
                    "title": "animal",
                    "cell_rows": [
                        {
                            "evidence": {
                                "evidence": "<p>asdf</p>",
                                "confidence": "<p>asdf</p>",
                                "optional": "<p>asdf</p>",
                            },
                            "certain_factors": {"factors": ["<p>asdf</p>", "<p>asdf</p>"]},
                            "uncertain_factors": {"factors": ["<p>asdf</p>", "<p>asdf</p>"]},
                            "summary": {"findings": "<p>asdf</p>"},
                            "judgement": {"judgement": "<p>asdf</p>", "description": "<p>asdf</p>"},
                        },
                        {
                            "evidence": {
                                "evidence": "<p>asdf</p>",
                                "confidence": "<p>asdf</p>",
                                "optional": "<p>asdf</p>",
                            },
                            "certain_factors": {"factors": ["<p>asdf</p>", "<p>asdf</p>"]},
                            "uncertain_factors": {"factors": ["<p>asdf</p>", "<p>asdf</p>"]},
                            "summary": {"findings": "<p>asdf</p>"},
                            "judgement": {"judgement": "<p>asdf</p>", "description": "<p>asdf</p>"},
                        },
                    ],
                    "merge_judgement": False,
                },
                "mechanistic": {"title": "mechanistic"},
                "summary_judgement": {
                    "judgement": "<p>asdf</p>",
                    "description": "<p>asdf</p>",
                    "human_relevance": "<p>asdf</p>",
                    "cross_stream_coherence": "<p>asdf</p>",
                    "susceptibility": "<p>asdf</p>",
                },
            }
        )
