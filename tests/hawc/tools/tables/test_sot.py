from pathlib import Path

import pandas as pd
import pytest
from docx import Document

from hawc.tools.tables.sot import AttributeChoices, StudyOutcomeTable

from . import documents_equal

FILE_PATH = Path(__file__).parent.absolute() / "data" / "sot_report.docx"


class TestAttributeChoices:
    empty_df = pd.DataFrame(
        {"score_score": [], "study citation": [], "animal description": [], "doses": []}
    )

    def test_rob_score(self):
        attribute = AttributeChoices.RobScore

        # test valid
        df = pd.DataFrame({"score_score": [1, 2]})
        cell = attribute.get_cell(df)
        assert cell.judgment == 1  # uses first value

        # test invalid
        cell = attribute.get_cell(self.empty_df)
        assert cell.judgment == -1

    def test_study_name(self):
        attribute = AttributeChoices.StudyName

        # test valid
        df = pd.DataFrame({"study citation": ["Foo et al.", "Bar et al."]})
        cell = attribute.get_cell(df)
        assert cell.quill_text == "<p>Foo et al.; Bar et al.</p>"

        # test invalid
        cell = attribute.get_cell(self.empty_df)
        assert cell.quill_text == "<p></p>"

    def test_species_strain_sex(self):
        attribute = AttributeChoices.SpeciesStrainSex

        # test valid
        df = pd.DataFrame({"animal description": ["Rat (Male)", "Rat (Female)"]})
        cell = attribute.get_cell(df)
        assert cell.quill_text == "<p>Rat (Male); Rat (Female)</p>"

        # test invalid
        cell = attribute.get_cell(self.empty_df)
        assert cell.quill_text == "<p></p>"

    def test_doses(self):
        attribute = AttributeChoices.Doses

        # test valid
        df = pd.DataFrame({"doses": ["0, 1, 100", "1, 100, 1000"]})
        cell = attribute.get_cell(df)
        assert cell.quill_text == "<p>0, 1, 100; 1, 100, 1000</p>"

        # test invalid
        cell = attribute.get_cell(self.empty_df)
        assert cell.quill_text == "<p></p>"

    def test_free_html(self):
        attribute = AttributeChoices.FreeHtml

        # will be valid regardless of selection; always returns empty cell
        df = pd.DataFrame({"column": [1, 2, 3]})
        cell = attribute.get_cell(df)
        assert cell.quill_text == "<p></p>"
        cell = attribute.get_cell(self.empty_df)
        assert cell.quill_text == "<p></p>"


@pytest.mark.django_db
class TestStudyOutcomeTable:
    def test_docx(self, rewrite_data_files: bool):
        data = {
            "assessment_id": 1,
            "data_source": "ani",
            "subheaders": [{"label": "This is a subheader", "start": 2, "length": 2}],
            "columns": [
                {"label": "Study name", "attribute": "study_name", "key": "1", "width": 1},
                {
                    "label": "Animal description",
                    "attribute": "species_strain_sex",
                    "key": "2",
                    "width": 2,
                },
                {"label": "Doses", "attribute": "doses", "key": "3", "width": 2},
                {
                    "label": "Rob score",
                    "attribute": "rob_score",
                    "metric": 1,
                    "key": "4",
                    "width": 4,
                },
            ],
            "rows": [
                {"id": 1, "type": "study", "customized": []},
                {
                    "id": 1,
                    "type": "study",
                    "customized": [
                        {"key": "1", "html": "<p>Custom study name</p>"},
                        {"key": "2", "html": "<p>Custom animal description</p>"},
                        {"key": "3", "html": "<p>Custom dose</p>"},
                        {"key": "4", "score_id": -1},
                    ],
                },
                {"id": -1, "type": "study", "customized": []},
            ],
        }
        table = StudyOutcomeTable.parse_obj(data)
        document = table.to_docx()
        if rewrite_data_files:
            document.save(FILE_PATH)
        saved_document = Document(FILE_PATH)

        assert documents_equal(document, saved_document)
