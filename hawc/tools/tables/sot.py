from enum import Enum
from typing import List, Optional

import pandas as pd
from pydantic import BaseModel, Field, conint

from hawc.apps.animal.models import Endpoint
from hawc.apps.materialized.models import FinalRiskOfBiasScore
from hawc.apps.riskofbias.constants import SCORE_SHADES, SCORE_SYMBOLS

from .base import BaseCell, BaseCellGroup, BaseTable
from .generic import GenericCell
from .parser import QuillParser, color_background, tag_wrapper


class AttributeChoices(Enum):
    RobScore = "rob_score"
    StudyName = "study_name"
    SpeciesStrainSex = "species_strain_sex"
    Doses = "doses"
    FreeHtml = "free_html"


class Subheader(BaseModel):
    label: str
    start: conint(ge=0)
    length: conint(ge=1)


class Column(BaseModel):
    label: str
    attribute: AttributeChoices
    metric: Optional[int]
    key: str


class Row(BaseModel):
    id: int
    type: str
    customized: List


class JudgementCell(BaseCell):
    judgement: int

    def to_docx(self, parser: QuillParser, block):
        text = SCORE_SYMBOLS[self.judgement]
        color = SCORE_SHADES[self.judgement].strip("#")
        color_background(block, color)
        return parser.feed(tag_wrapper(text, "p"), block)


class StudyOutcomeTable(BaseTable):
    assessment_id: int
    subheaders: List[Subheader]
    cell_columns: List[Column] = Field([], alias="columns")
    cell_rows: List[Row] = Field([], alias="rows")

    def get_html(self, data, row, attribute):
        selection = data.loc[data["study id"] == row.id]
        if attribute == "study_name":
            text = selection["study citation"].values[0]
            return tag_wrapper(text, "p")
        elif attribute == "species_strain_sex":
            text = selection["species"].values[0]
            return tag_wrapper(text, "p")
        elif attribute == "doses":
            text = selection["dose units"].values[0]
            return tag_wrapper(text, "p")
        elif attribute == "free_html":
            return tag_wrapper("", "p")

    def _subheaders_group(self):
        cells = []
        for subheader in self.subheaders:
            html = tag_wrapper(subheader.label, "p", "strong")
            cells.append(
                GenericCell.parse_args(True, 0, subheader.start, 1, subheader.length, html)
            )
        return BaseCellGroup.construct(cells=cells)

    def _columns_group(self):
        cells = []
        for i, col in enumerate(self.cell_columns):
            html = tag_wrapper(col.label, "p", "strong")
            cells.append(GenericCell.parse_args(True, 0, i, 1, 1, html))
        return BaseCellGroup.construct(cells=cells)

    def _rows_group(self):
        cells = []

        study_ids = {row.id for row in self.cell_rows if row.type == "study"}
        final_scores = pd.DataFrame.from_records(
            FinalRiskOfBiasScore.objects.filter(study_id__in=study_ids).values()
        )
        bioassay_data = Endpoint.heatmap_study_df(
            assessment_id=self.assessment_id, published_only=False
        )

        for i, row in enumerate(self.cell_rows):
            for j, col in enumerate(self.cell_columns):
                if col.attribute.value == "rob_score":
                    judgement = final_scores.loc[
                        (final_scores["study_id"] == row.id)
                        & (final_scores["metric_id"] == col.metric)
                        & (final_scores["content_type_id"].isnull())
                    ]["score_score"]
                    cell = JudgementCell(row=i, column=j, judgement=judgement)
                else:
                    html = self.get_html(bioassay_data, row, col.attribute.value)
                    cell = GenericCell(row=i, column=j, quill_text=html)
                for custom in [custom for custom in row.customized if custom["key"] == col.key]:
                    if "quill_text" in custom:
                        cell.quill_text = custom["quill_text"]
                    elif "judgement" in custom:
                        cell.judgement = custom["judgement"]
                cells.append(cell)
        return BaseCellGroup.construct(cells=cells)

    def _set_cells(self):
        # get cell groups
        subheaders_group = self._subheaders_group()
        columns_group = self._columns_group()
        rows_group = self._rows_group()

        # offset cell groups
        columns_group.add_offset(row=subheaders_group.rows)
        rows_group.add_offset(row=columns_group.rows)

        # combine cell groups
        self.cells = subheaders_group.cells + columns_group.cells + rows_group.cells

    @classmethod
    def get_default_props(cls):
        return {
            "assessment_id": -1,
            "subheaders": [],
            "columns": [],
            "rows": [],
        }
