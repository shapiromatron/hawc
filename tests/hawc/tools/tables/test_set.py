from pathlib import Path

import pandas as pd
import pytest
from docx import Document

from hawc.tools.tables.set import AttributeChoices, StudyEvaluationTable

from . import documents_equal

FILE_PATH = Path(__file__).parent.absolute() / "data" / "set_report.docx"


class TestAttributeChoices:
    empty_df = pd.DataFrame({"score_score": [], "study citation": [], "animal description": []})

    def test_free_html(self):
        attribute = AttributeChoices.FreeHtml

        # will be valid regardless of selection; always returns empty cell
        df = pd.DataFrame({"column": [1, 2, 3]})
        cell = attribute.get_cell(df)
        assert cell.quill_text == "<p></p>"
        cell = attribute.get_cell(self.empty_df)
        assert cell.quill_text == "<p></p>"

    def test_rob(self):
        attribute = AttributeChoices.Rob

        # test valid
        df = pd.DataFrame({"score_score": [1, 2]})
        cell = attribute.get_cell(df)
        assert cell.judgment == 1  # uses first value

        # test invalid
        cell = attribute.get_cell(self.empty_df)
        assert cell.judgment == -1

    def test_study_short_citation(self):
        attribute = AttributeChoices.StudyShortCitation

        # test valid
        df = pd.DataFrame({"study citation": ["Foo et al.", "Bar et al."]})
        cell = attribute.get_cell(df)
        assert cell.quill_text == "<p>Foo et al.; Bar et al.</p>"

        # test invalid
        cell = attribute.get_cell(self.empty_df)
        assert cell.quill_text == "<p></p>"

    def test_animal_group_description(self):
        attribute = AttributeChoices.AnimalGroupDescription

        # test valid
        df = pd.DataFrame({"animal description": ["Rat (Male)", "Rat (Female)"]})
        cell = attribute.get_cell(df)
        assert cell.quill_text == "<p>Rat (Male); Rat (Female)</p>"

        # test invalid
        cell = attribute.get_cell(self.empty_df)
        assert cell.quill_text == "<p></p>"


@pytest.mark.django_db
class TestStudyEvaluationTable:
    def test_docx(self, rewrite_data_files: bool):
        data = {
            "assessment_id": 1,
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
                {"label": "Rob score", "attribute": "rob", "metric_id": 1, "key": "3", "width": 3},
            ],
            "rows": [
                {"id": 1, "type": "study", "customized": []},
                {
                    "id": 1,
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
        table = StudyEvaluationTable.parse_obj(data)
        document = table.to_docx()
        if rewrite_data_files:
            document.save(FILE_PATH)
        saved_document = Document(FILE_PATH)

        assert documents_equal(document, saved_document)
