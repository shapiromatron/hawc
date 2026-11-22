from pathlib import Path

import pandas as pd
from docx import Document

from hawc.tools.tables.set.constants import AttributeChoices
from hawc.tools.tables.set.table import Column, StudyEvaluationTable

from . import documents_equal

FILE_PATH = Path(__file__).parent.absolute() / "data" / "set_report.docx"


class TestAttributeChoices:
    def test_free_html(self):
        attribute = AttributeChoices.FreeHtml
        col = Column.model_construct(attribute=attribute)

        # returns an empty cell; overridden by customizations
        series = pd.Series({"foo": "foo", "bar": "bar", "free_html": "free_html"})
        cell = col.get_cell(series)
        assert cell.quill_text == "<p></p>"
        series = pd.Series(dtype=float)
        cell = col.get_cell(series)
        assert cell.quill_text == "<p></p>"

    def test_rob(self):
        attribute = AttributeChoices.Rob
        col = Column.model_construct(attribute=attribute)

        # test with scores
        df = pd.DataFrame({"score_score": [1, 2]})
        cell = col.get_cell(df)
        assert cell.judgment == 1  # uses first value

        # test with no scores
        df = pd.DataFrame({"score_score": []})
        cell = col.get_cell(df)
        assert cell.judgment == -1

    def test_animal_group_doses(self):
        attribute = AttributeChoices.AnimalGroupDoses

        series = pd.Series(
            {"animal_group_doses": {"ppm": ["0, 1, 10", "1, 10, 100"], "mg/m3": ["1, 10, 100"]}}
        )

        # show all doses
        col = Column.model_construct(attribute=attribute, dose_unit="")
        cell = col.get_cell(series)
        assert cell.quill_text == "<p>0, 1, 10 ppm; 1, 10, 100 ppm; 1, 10, 100 mg/m3</p>"

        # show ppm doses
        col = Column.model_construct(attribute=attribute, dose_unit="ppm")
        cell = col.get_cell(series)
        assert cell.quill_text == "<p>0, 1, 10; 1, 10, 100</p>"

        # unit not present
        col = Column.model_construct(attribute=attribute, dose_unit="mg/kg")
        cell = col.get_cell(series)
        assert cell.quill_text == "<p></p>"

    def test_default(self):
        attribute = AttributeChoices.StudyShortCitation
        col = Column.model_construct(attribute=attribute)

        # valid
        series = pd.Series({"study_short_citation": "Foo et al.; Bar et al."})
        cell = col.get_cell(series)
        assert cell.quill_text == "<p>Foo et al.; Bar et al.</p>"


class TestStudyEvaluationTable:
    def test_docx(self, study_data, rewrite_data_files: bool):
        data = {
            "assessment_id": study_data.assessment.id,
            "data_source": "ani",
            "published_only": False,
            "subheaders": [
                {"label": "Subheader above animal description", "start": 2, "length": 1}
            ],
            "columns": [
                {
                    "label": "Study citation",
                    "attribute": "study_short_citation",
                    "key": "1",
                    "width": 1,
                },
                {
                    "label": "Animal description",
                    "attribute": "animal_group_description",
                    "key": "2",
                    "width": 2,
                },
                {
                    "label": "Rob score",
                    "attribute": "rob",
                    "metric_id": study_data.metric.id,
                    "key": "3",
                    "width": 3,
                },
            ],
            "rows": [
                {"id": study_data.study.id, "type": "study", "customized": []},
                {
                    "id": study_data.study.id,
                    "type": "study",
                    "customized": [
                        {"key": "1", "html": "<p>Custom study name</p>"},
                        {"key": "2", "html": "<p>Custom animal description</p>"},
                        {"key": "3", "score_id": -1},
                    ],
                },
                {"id": -1, "type": "study", "customized": []},
            ],
        }
        table = StudyEvaluationTable.model_validate(data)
        document = table.to_docx()
        if rewrite_data_files:
            document.save(FILE_PATH)
        saved_document = Document(FILE_PATH)

        assert documents_equal(document, saved_document)

    def test_cells(self, study_data):
        score_column = {
            "label": "Rob",
            "attribute": "rob",
            "metric_id": study_data.metric.id,
            "key": "1",
        }
        rows = [
            {"id": study_data.study.id, "type": "study", "customized": []},  # multiple scores
            {"id": study_data.none_study.id, "type": "study", "customized": []},  # no scores
            {
                "id": study_data.study.id,
                "type": "study",
                "customized": [{"key": "1", "score_id": study_data.override_score.id}],
            },
            {"id": -1, "type": "study", "customized": []},  # not found
        ]
        table = StudyEvaluationTable.model_validate(
            {
                "assessment_id": study_data.assessment.id,
                "data_source": "study",
                "published_only": True,
                "subheaders": [],
                "columns": [score_column],
                "rows": rows,
            }
        )
        cells = {(cell.row, cell.column): cell for cell in table.cells}
        assert [cells[(i, 0)].judgment for i in range(1, 4)] == [17, -1, 14]
        assert cells[(4, 0)].quill_text == "<p>study -1 not found</p>"

    def test_cells_single_score(self, study_data):
        table = StudyEvaluationTable.model_validate(
            {
                "assessment_id": study_data.unique_assessment.id,
                "data_source": "study",
                "published_only": True,
                "subheaders": [],
                "columns": [
                    {
                        "label": "Rob",
                        "attribute": "rob",
                        "metric_id": study_data.unique_metric.id,
                        "key": "1",
                    }
                ],
                "rows": [{"id": study_data.unique_study.id, "type": "study", "customized": []}],
            }
        )
        assert [c.judgment for c in table.cells if c.row == 1] == [16]

    def test_animal_cells(self, study_data):
        columns = [
            ("experiment_name", "Exp 1"),
            ("experiment_chemical", "Chem A"),
            ("animal_group_name", "Group 1"),
            ("animal_group_route_of_exposure", "Oral"),
            ("animal_group_treatment_period", "Chronic  (2 years)"),
            ("animal_group_doses", "0, 10 test mg/kg"),
            ("endpoint_system", "Liver"),
            ("endpoint_effect", "Weight"),
            ("endpoint_name", "Endpoint 1"),
        ]
        table = StudyEvaluationTable.model_validate(
            {
                "assessment_id": study_data.assessment.id,
                "data_source": "ani",
                "published_only": True,
                "subheaders": [],
                "columns": [
                    {"label": a, "attribute": a, "key": str(i), "dose_unit": ""}
                    for i, (a, _) in enumerate(columns)
                ],
                "rows": [{"id": study_data.study.id, "type": "study", "customized": []}],
            }
        )
        cells = {cell.column: cell for cell in table.cells if cell.row == 1}
        assert [cells[i].quill_text for i in range(len(columns))] == [
            f"<p>{text}</p>" for _, text in columns
        ]

    def test_get_default_props(self):
        props = StudyEvaluationTable.get_default_props()
        assert props["data_source"] == "study"
        assert props["columns"] == props["rows"] == props["subheaders"] == []
