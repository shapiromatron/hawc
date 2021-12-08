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

    def get_rob_score(self, selection: pd.DataFrame) -> BaseCell:
        values = selection["score_score"].values

        judgment = 0 if values.size == 0 else values[0]
        return JudgmentCell(judgment=judgment)

    def get_study_name(self, selection: pd.DataFrame) -> BaseCell:
        values = selection["study citation"].dropna().unique()

        text = "; ".join(values)
        return GenericCell(quill_text=tag_wrapper(text, "p"))

    def get_species_strain_sex(self, selection: pd.DataFrame) -> BaseCell:
        values = selection["animal description"].dropna().unique()

        text = "; ".join(values)
        return GenericCell(quill_text=tag_wrapper(text, "p"))

    def get_doses(self, selection: pd.DataFrame) -> BaseCell:
        values = selection["doses"].dropna().unique()

        text = "; ".join(values)
        return GenericCell(quill_text=tag_wrapper(text, "p"))

    def get_free_html(self, selection: pd.DataFrame) -> BaseCell:
        # this will be overridden by 'customized' html
        return GenericCell()

    def get_cell(self, selection: pd.DataFrame) -> BaseCell:
        return getattr(self, f"get_{self.value}")(selection)


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


class JudgmentCell(BaseCell):
    judgment: int

    def to_docx(self, parser: QuillParser, block):
        text = SCORE_SYMBOLS[self.judgment]
        color = SCORE_SHADES[self.judgment].strip("#")
        color_background(block, color)
        return parser.feed(tag_wrapper(text, "p"), block)


class StudyOutcomeTable(BaseTable):
    assessment_id: int
    subheaders: List[Subheader]
    cell_columns: List[Column] = Field([], alias="columns")
    cell_rows: List[Row] = Field([], alias="rows")

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

    def _set_override(self, final_scores: pd.DataFrame, cell: BaseCell, row: Row, column: Column):
        for custom in [custom for custom in row.customized if custom["key"] == column.key]:
            if "html" in custom:
                cell.quill_text = custom["html"]
            elif "score_id" in custom:
                values = final_scores.loc[final_scores["score_id"] == custom["score_id"]][
                    "score_score"
                ].values
                cell.judgment = 0 if values.size == 0 else values[0]

    def _get_selection(
        self, bioassay_data: pd.DataFrame, final_scores: pd.DataFrame, row: Row, column: Column
    ) -> pd.DataFrame:
        if column.attribute.value == "rob_score":
            return final_scores.loc[
                (final_scores["study_id"] == row.id)
                & (final_scores["metric_id"] == column.metric)
                & (final_scores["content_type_id"].isnull())
            ]
        else:
            return bioassay_data.loc[bioassay_data["study id"] == row.id]

    def _filter_rows(self, bioassay_data: pd.DataFrame) -> List[Row]:
        return [row for row in self.cell_rows if row.id in bioassay_data["study id"].values]

    def _rows_group(self):
        cells = []

        study_ids = {row.id for row in self.cell_rows if row.type == "study"}
        final_scores = pd.DataFrame.from_records(
            FinalRiskOfBiasScore.objects.filter(study_id__in=study_ids).values()
        )
        bioassay_data = Endpoint.heatmap_doses_df(
            assessment_id=self.assessment_id, published_only=False
        )

        rows = self._filter_rows(bioassay_data)

        for i, row in enumerate(rows):
            for j, col in enumerate(self.cell_columns):
                selection = self._get_selection(bioassay_data, final_scores, row, col)
                cell = col.attribute.get_cell(selection)
                self._set_override(final_scores, cell, row, col)
                cell.row = i
                cell.column = j
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
