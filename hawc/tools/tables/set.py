from enum import Enum
from typing import List, Optional, Union

import pandas as pd
from pydantic import BaseModel, Field, conint

from hawc.apps.riskofbias.constants import SCORE_SHADES, SCORE_SYMBOLS
from hawc.apps.summary.table_serializers import StudyEvaluationSerializer

from .base import BaseCell, BaseCellGroup, BaseTable
from .generic import GenericCell
from .parser import QuillParser, color_background, tag_wrapper

NM_SYMBOL = "NM"
NM_SHADE = "#DFDFDF"


class DataSourceChoices(Enum):
    Animal = "ani"
    Study = "study"


class AttributeChoices(Enum):
    FreeHtml = "free_html"
    Rob = "rob"
    StudyShortCitation = "study_short_citation"
    AnimalGroupDescription = "animal_group_description"
    AnimalGroupDoses = "animal_group_doses"
    ExperimentName = "experiment_name"
    AnimalGroupName = "animal_group_name"
    AnimalGroupTreatmentPeriod = "animal_group_treatment_period"
    AnimalGroupRouteOfExposure = "animal_group_route_of_exposure"
    EndpointSystem = "endpoint_system"
    EndpointEffect = "endpoint_effect"
    EndpointName = "endpoint_name"
    ExperimentChemical = "experiment_chemical"

    def get_free_html(self, col, selection: pd.Series) -> BaseCell:
        # this will be overridden by 'customized' html
        return GenericCell()

    def get_animal_group_doses(self, col, selection: pd.Series) -> BaseCell:
        if selection["animal_group_doses"] == "":
            text = ""
        else:
            dose_units = selection["animal_group_dose_units"].split("|")
            doses = selection["animal_group_doses"].split("|")
            if col.dose_unit == "":
                text = "; ".join(
                    ["; ".join([f"{_d} {dose_units[i]}" for _d in d.split("; ")]) for i, d in enumerate(doses)]
                )
            else:
                try:
                    index = dose_units.index(col.dose_unit)
                    text = doses[index]
                except ValueError:
                    text = ""
        return GenericCell(quill_text=tag_wrapper(text, "p"))

    def get_rob(self, col, selection: pd.DataFrame) -> BaseCell:
        values = selection["score_score"].values
        judgment = -1 if values.size == 0 else values[0]
        return JudgmentColorCell(judgment=judgment)

    def _get_default(self, col, selection: pd.Series) -> BaseCell:
        text = selection[self.value]
        return GenericCell(quill_text=tag_wrapper(text, "p"))

    def get_cell(self, col, selection: Union[pd.DataFrame, pd.Series]) -> BaseCell:
        return getattr(self, f"get_{self.value}", self._get_default)(col, selection)


class Subheader(BaseModel):
    label: str
    start: conint(ge=1)
    length: conint(ge=1)


class Column(BaseModel):
    label: str
    attribute: AttributeChoices
    width: int = 1
    metric_id: Optional[int]
    dose_unit: Optional[str]
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

        ser = StudyEvaluationSerializer(
            data={
                "assessment_id": self.assessment_id,
                "data_source": self.data_source.value,
                "published_only": self.published_only,
            }
        )
        ser.is_valid(raise_exception=True)

        data_dict = ser.get_dfs()
        self._data = data_dict["data"].set_index(["type", "id"])
        self._rob = data_dict["rob"].set_index(["study_id", "metric_id"])

    def _subheaders_group(self):
        cells = []
        for subheader in self.subheaders:
            html = tag_wrapper(subheader.label, "p", "strong")
            cells.append(GenericCell.parse_args(True, 0, subheader.start - 1, 1, subheader.length, html))
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
                values = self._rob.loc[self._rob["score_id"] == custom["score_id"]]["score_score"].values
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
            return self._data.loc[(row.type, row.id)]

    def _rows_group(self):
        cells = []

        for i, row in enumerate(self.cell_rows):
            if (row.type, row.id) not in self._data.index and self.cell_columns:
                html = tag_wrapper(f"{row.type} {row.id} not found", "p")
                col_span = len(self.cell_columns)
                cells.append(GenericCell.parse_args(False, i, 0, 1, col_span, html))
                continue
            for j, col in enumerate(self.cell_columns):
                selection = self._get_selection(row, col)
                cell = col.attribute.get_cell(col, selection)
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
    def get_default_props(cls):
        return {
            "assessment_id": -1,
            "data_source": "study",
            "published_only": True,
            "subheaders": [],
            "columns": [],
            "rows": [],
        }
