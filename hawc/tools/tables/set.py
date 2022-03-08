from enum import Enum
from typing import Dict, List, Optional

import pandas as pd
from pydantic import BaseModel, Field, conint

from hawc.apps.animal.models import Endpoint
from hawc.apps.materialized.models import FinalRiskOfBiasScore
from hawc.apps.riskofbias.constants import SCORE_SHADES, SCORE_SYMBOLS
from hawc.apps.study.models import Study

from .base import BaseCell, BaseCellGroup, BaseTable
from .generic import GenericCell
from .parser import QuillParser, color_background, tag_wrapper

NM_SYMBOL = "NM"
NM_SHADE = "#DFDFDF"


class DataSourceChoices(Enum):
    Animal = "ani"
    Study = "study"

    def get_ani_data(self, assessment_id: int, published_only: bool) -> Dict:
        ani_data = (
            Endpoint.heatmap_doses_df(assessment_id=assessment_id, published_only=published_only)
            .fillna("")
            .to_dict(orient="records")
        )
        study_ids = Study.objects.filter(
            assessment_id=assessment_id, bioassay=True, riskofbiases__final=True
        ).values_list("id", flat=True)
        rob_data = (
            FinalRiskOfBiasScore.objects.filter(study_id__in=study_ids).order_by("id").values()
        )

        return {"data": ani_data, "rob": rob_data}

    def get_study_data(self, assessment_id: int, published_only: bool) -> Dict:
        study_filters = {"assessment_id": assessment_id, "riskofbiases__final": True}
        if published_only:
            study_filters["published"] = True
        study_qs = Study.objects.filter(**study_filters)
        study_df = pd.DataFrame.from_records(study_qs.values("id", "short_citation"))
        study_ids = study_df.id.tolist() if study_df.size > 0 else []
        study_data = study_df.rename(
            columns={"id": "study id", "short_citation": "study citation"}
        ).to_dict(orient="records")
        rob_data = (
            FinalRiskOfBiasScore.objects.filter(study_id__in=study_ids).order_by("id").values()
        )

        return {"data": study_data, "rob": rob_data}

    def get_data(self, assessment_id: int, published_only: bool) -> Dict:
        return getattr(self, f"get_{self.value}_data")(assessment_id, published_only)


class AttributeChoices(Enum):
    FreeHtml = "free_html"
    Rob = "rob"
    StudyShortCitation = "study_short_citation"
    AnimalGroupDescription = "animal_group_description"

    def get_free_html(self, selection: pd.DataFrame) -> BaseCell:
        # this will be overridden by 'customized' html
        return GenericCell()

    def get_rob(self, selection: pd.DataFrame) -> BaseCell:
        values = selection["score_score"].values

        judgment = -1 if values.size == 0 else values[0]
        return JudgmentColorCell(judgment=judgment)

    def get_study_short_citation(self, selection: pd.DataFrame) -> BaseCell:
        values = selection["study citation"].dropna().unique()

        text = "; ".join(values)
        return GenericCell(quill_text=tag_wrapper(text, "p"))

    def get_animal_group_description(self, selection: pd.DataFrame) -> BaseCell:
        values = selection["animal description"].dropna().unique()

        text = "; ".join(values)
        return GenericCell(quill_text=tag_wrapper(text, "p"))

    def get_cell(self, selection: pd.DataFrame) -> BaseCell:
        return getattr(self, f"get_{self.value}")(selection)


class Subheader(BaseModel):
    label: str
    start: conint(ge=1)
    length: conint(ge=1)


class Column(BaseModel):
    label: str
    attribute: AttributeChoices
    width: int = 1
    metric_id: Optional[int]
    key: str


class Row(BaseModel):
    id: int
    type: str
    customized: List


class JudgmentColorCell(BaseCell):
    judgment: int

    def to_docx(self, parser: QuillParser, block):
        text = SCORE_SYMBOLS.get(self.judgment, NM_SYMBOL)
        color = SCORE_SHADES.get(self.judgment, NM_SHADE)
        color_background(block, color)
        return parser.feed(tag_wrapper(text, "p"), block)


class StudyEvaluationTable(BaseTable):
    assessment_id: int
    data_source: DataSourceChoices
    published_only: bool
    subheaders: List[Subheader]
    cell_columns: List[Column] = Field([], alias="columns")
    cell_rows: List[Row] = Field([], alias="rows")

    _data: pd.DataFrame
    _rob: pd.DataFrame

    def _setup(self):
        self.column_widths = [col.width for col in self.cell_columns]

        data_dict = self.get_data(self.assessment_id, self.data_source, self.published_only)
        self._data = pd.DataFrame.from_records(data_dict["data"])
        self._rob = pd.DataFrame.from_records(
            data_dict["rob"],
            columns=[
                "study_id",
                "metric_id",
                "id",
                "score_id",
                "score_label",
                "score_notes",
                "score_score",
                "bias_direction",
                "is_default",
                "riskofbias_id",
                "content_type_id",
                "object_id",
            ],
        ).set_index(["study_id", "metric_id"])

    def _subheaders_group(self):
        cells = []
        for subheader in self.subheaders:
            html = tag_wrapper(subheader.label, "p", "strong")
            cells.append(
                GenericCell.parse_args(True, 0, subheader.start - 1, 1, subheader.length, html)
            )
        return BaseCellGroup.construct(cells=cells)

    def _columns_group(self):
        cells = []
        for i, col in enumerate(self.cell_columns):
            html = tag_wrapper(col.label, "p", "strong")
            cells.append(GenericCell.parse_args(True, 0, i, 1, 1, html))
        return BaseCellGroup.construct(cells=cells)

    def _set_override(self, cell: BaseCell, row: Row, column: Column):
        for custom in [custom for custom in row.customized if custom["key"] == column.key]:
            if "html" in custom:
                cell.quill_text = custom["html"]
            elif "score_id" in custom:
                values = self._rob.loc[self._rob["score_id"] == custom["score_id"]][
                    "score_score"
                ].values
                cell.judgment = -1 if values.size == 0 else values[0]

    def _get_selection(self, row: Row, column: Column) -> pd.DataFrame:
        if column.attribute.value == "rob":
            try:
                selection = self._rob.loc[(row.id, column.metric_id)]
            except KeyError:
                return pd.DataFrame(columns=self._rob.columns)
            # if there are duplicate indices, selection is a dataframe
            if isinstance(selection, pd.DataFrame):
                return selection.loc[selection["content_type_id"].isnull()]
            # if there are no duplicate indices, selection is a series
            return pd.DataFrame([selection])
        else:
            return self._data.loc[self._data["study id"] == row.id]

    def _rows_group(self):
        cells = []

        for i, row in enumerate(self.cell_rows):
            if row.id not in self._data["study id"].values and self.cell_columns:
                html = tag_wrapper(f"{row.type} {row.id} not found", "p")
                col_span = len(self.cell_columns)
                cells.append(GenericCell.parse_args(False, i, 0, 1, col_span, html))
                continue
            for j, col in enumerate(self.cell_columns):
                selection = self._get_selection(row, col)
                cell = col.attribute.get_cell(selection)
                self._set_override(cell, row, col)
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
    def get_data(cls, assessment_id: int, data_source: str, published_only: bool) -> Dict:
        return DataSourceChoices(data_source).get_data(assessment_id, published_only)

    @classmethod
    def get_default_props(cls):
        return {
            "assessment_id": -1,
            "data_source": "study",
            "published_only": True,
            "subheaders": [],
            "columns": [],
            "rows": [],
        }
