from typing import List

from docx import Document
from docx.oxml.shared import OxmlElement, qn

from .base import BaseCell, BaseCellGroup, BaseTable
from .generic import GenericCell
from .parser import QuillParser, tag_wrapper


class EvidenceStreamGraphic(BaseCell):
    row: int = 1
    column: int = 0
    row_span: int = 5

    def to_docx(self, block):
        parser = QuillParser()
        return parser.feed("<p></p>", block)


class EvidenceBasisCell(BaseCell):
    row: int = 1
    column: int = 4
    row_span: int = 5

    basis: str

    def to_docx(self, block):
        parser = QuillParser()
        return parser.feed(self.basis, block)


class EvidenceStreamCell(BaseCell):
    evidence: List[str]

    def to_docx(self, block):
        parser = QuillParser()
        return parser.feed("".join(self.evidence), block)


class EvidenceStreamGroup(BaseCellGroup):
    level1: EvidenceStreamCell
    level2: EvidenceStreamCell
    level3: EvidenceStreamCell
    level4: EvidenceStreamCell
    level5: EvidenceStreamCell

    def _set_cells(self):
        self.level1.row = 1
        self.level2.row = 2
        self.level3.row = 3
        self.level4.row = 4
        self.level5.row = 5
        self.cells = [self.level1, self.level2, self.level3, self.level4, self.level5]


class EvidenceIntegrationTable(BaseTable):
    human_studies: EvidenceStreamGroup
    animal_studies: EvidenceStreamGroup
    evidence_basis: EvidenceBasisCell

    def column_headers(self):
        text1 = tag_wrapper("Evidence stream scenarios", "p", "strong")
        text2 = tag_wrapper("Evidence in studies of humans", "p", "strong")
        text3 = tag_wrapper("Evidence in animal studies", "p", "strong")
        text4 = tag_wrapper("Evidence Basis", "p", "strong")
        return [
            GenericCell.parse_args(True, 0, 0, 1, 2, text1),
            GenericCell.parse_args(True, 0, 2, 1, 1, text2,),
            GenericCell.parse_args(True, 0, 3, 1, 1, text3),
            GenericCell.parse_args(True, 0, 4, 1, 1, text4),
        ]

    def row_headers(self):
        text1 = tag_wrapper("No Studies, or Low Confidence or Conflicting Evidence", "p", "em")
        text2 = tag_wrapper("Strong Mechanistic Evidence Alone", "p", "em")
        text3 = tag_wrapper(
            "One High or Medium Confidence Apical Study without Supporting or Conflicting Evidence",
            "p",
            "em",
        )
        text4 = tag_wrapper(
            "Multiple High or Medium Confidence Apical Studies with Some inconsistency or important Uncertainties",
            "p",
            "em",
        )
        text5 = tag_wrapper(
            "Multiple High or Medium Confidence Apical Studies with Strong Support (e.g., MOA understanding supporting biological plausibility)",
            "p",
            "em",
        )
        return [
            GenericCell.parse_args(True, 1, 1, 1, 1, text1),
            GenericCell.parse_args(True, 2, 1, 1, 1, text2,),
            GenericCell.parse_args(True, 3, 1, 1, 1, text3),
            GenericCell.parse_args(True, 4, 1, 1, 1, text4),
            GenericCell.parse_args(True, 5, 1, 1, 1, text5),
        ]

    def _set_cells(self):
        cells = []
        cells.append(EvidenceStreamGraphic())
        cells.extend(self.row_headers())
        cells.extend(self.column_headers())
        self.human_studies.add_offset(column=2)
        cells.extend(self.human_studies.cells)
        self.animal_studies.add_offset(column=3)
        cells.extend(self.animal_studies.cells)
        cells.append(self.evidence_basis)
        self.cells = cells

    def shade_cells(self, cells, shade):
        for cell in cells:
            tcPr = cell._tc.get_or_add_tcPr()
            shd = OxmlElement("w:shd")
            shd.set(qn("w:fill"), shade)
            tcPr.append(shd)

    def to_docx(self, docx: Document = None):
        docx = super().to_docx(docx)
        shade1 = "#7F7F7F"
        shade2 = "#9F9F9F"
        shade3 = "#BFBFBF"
        shade4 = "#DFDFDF"
        table = docx.tables[0]
        self.shade_cells([table.cell(1, 1), table.cell(1, 2), table.cell(1, 3)], shade1)
        self.shade_cells([table.cell(2, 1), table.cell(2, 2), table.cell(2, 3)], shade2)
        self.shade_cells([table.cell(3, 1), table.cell(3, 2), table.cell(3, 3)], shade3)
        self.shade_cells([table.cell(4, 1), table.cell(4, 2), table.cell(4, 3)], shade4)

        return docx

    @classmethod
    def build_default(cls):
        return cls.parse_obj(
            {
                "human_studies": {
                    "level1": {"evidence": ["<p>asdf</p>"]},
                    "level2": {"evidence": ["<p>asdf</p>"]},
                    "level3": {"evidence": ["<p>asdf</p>"]},
                    "level4": {"evidence": ["<p>asdf</p>"]},
                    "level5": {"evidence": ["<p>asdf</p>"]},
                },
                "animal_studies": {
                    "level1": {"evidence": ["<p>asdf</p>"]},
                    "level2": {"evidence": ["<p>asdf</p>"]},
                    "level3": {"evidence": ["<p>asdf</p>"]},
                    "level4": {"evidence": ["<p>asdf</p>"]},
                    "level5": {"evidence": ["<p>asdf</p>"]},
                },
                "evidence_basis": {"basis": "<p>asdf</p>"},
            }
        )
