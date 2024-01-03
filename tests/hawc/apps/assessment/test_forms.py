import tempfile
from pathlib import Path

import pandas as pd
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from hawc.apps.assessment.filterset import LogFilterSet
from hawc.apps.assessment.forms import AssessmentValueForm, DatasetForm
from hawc.apps.assessment.models import Assessment, Dataset, DatasetRevision

IRIS_DATA_CSV = (
    Path(__file__).parents[3] / "data/private-data/assessment/dataset-revision/iris.csv"
).read_bytes()

IRIS_DATA_XLSX = (
    Path(__file__).parents[3] / "data/private-data/assessment/dataset-revision/iris.xlsx"
).read_bytes()


@pytest.mark.django_db
class TestDatasetForm:
    @classmethod
    def setup_class(cls):
        # set temporary location for data storage
        cls.storage_location = DatasetRevision.data.field.storage.location
        DatasetRevision.data.field.storage.location = tempfile.TemporaryDirectory(
            prefix="hawc-tests"
        ).name

    @classmethod
    def teardown_class(cls):
        # restore location for other tests
        DatasetRevision.data.field.storage.location = cls.storage_location

    def test_initial_versions(self, db_keys):
        form = DatasetForm(parent=Assessment.objects.get(id=db_keys.assessment_working))
        assert form.fields["revision_version"].initial == 1

        form = DatasetForm(instance=Dataset.objects.get(id=db_keys.dataset_working))
        assert form.fields["revision_version"].initial == 3

    def test_valid_new_form(self, db_keys):
        # check valid and objects are created as expected
        settings = {
            "name": "name",
            "description": "description",
            "revision_excel_worksheet_name": "",
            "revision_notes": "notes",
        }
        form = DatasetForm(
            settings,
            {"revision_data": SimpleUploadedFile("test-data.csv", IRIS_DATA_CSV)},
            parent=Assessment.objects.get(id=db_keys.assessment_working),
        )
        assert form.is_valid()
        assert isinstance(form.revision_df, pd.DataFrame)
        assert form.revision_metadata.model_dump() == {
            "filename": "test-data.csv",
            "extension": ".csv",
            "num_rows": 150,
            "num_columns": 5,
            "column_names": [
                "sepal_length",
                "sepal_width",
                "petal_length",
                "petal_width",
                "species",
            ],
        }
        instance = form.save()
        assert instance.name == "name"
        assert instance.revisions.count() == 1
        assert instance.revisions.first().notes == "notes"

    def test_required_data(self, db_keys):
        # data is required when creating a new dataset
        settings = {
            "name": "name",
            "description": "description",
            "revision_excel_worksheet_name": "",
            "revision_notes": "",
        }
        form = DatasetForm(settings, parent=Assessment.objects.get(id=db_keys.assessment_working))
        assert form.is_valid() is False
        assert form.errors == {"revision_data": ["This field is required."]}

        # data is not required when updating a dataset
        settings = {
            "name": "name",
            "description": "description",
            "revision_excel_worksheet_name": "",
            "revision_notes": "",
        }
        form = DatasetForm(settings, instance=Dataset.objects.get(id=db_keys.dataset_working))
        assert form.is_valid()

    def test_bad_datsets(self, db_keys):
        settings = {
            "name": "name",
            "description": "description",
            "revision_excel_worksheet_name": "",
            "revision_notes": "",
        }

        # bad extension
        form = DatasetForm(
            settings,
            {"revision_data": SimpleUploadedFile("data.foo", IRIS_DATA_CSV)},
            parent=Assessment.objects.get(id=db_keys.assessment_working),
        )
        assert form.is_valid() is False
        assert form.errors == {
            "revision_data": ["Invalid file extension: must be one of: .csv, .tsv, .xlsx"]
        }

        # bad dataset (xlsx extension; csv data)
        form = DatasetForm(
            settings,
            {"revision_data": SimpleUploadedFile("data.xlsx", IRIS_DATA_CSV)},
            parent=Assessment.objects.get(id=db_keys.assessment_working),
        )
        assert form.is_valid() is False
        assert form.errors == {
            "revision_data": [
                "Unable to read the submitted dataset file. Please validate that the uploaded file can be read.",
            ]
        }

    def test_worksheet_name(self, db_keys):
        data = {"revision_data": SimpleUploadedFile("data.xlsx", IRIS_DATA_XLSX)}
        parent = Assessment.objects.get(id=db_keys.assessment_working)

        # no worksheet name
        settings = {
            "name": "name",
            "description": "description",
            "revision_excel_worksheet_name": "",
            "revision_notes": "",
        }
        form = DatasetForm(settings, data, parent=parent)
        assert form.is_valid()

        # good worksheet name
        settings["revision_excel_worksheet_name"] = "data"
        form = DatasetForm(settings, data, parent=parent)
        assert form.is_valid()

        # bad worksheet name
        settings["revision_excel_worksheet_name"] = "does not exist"
        form = DatasetForm(settings, data, parent=parent)
        assert form.is_valid() is False
        assert form.errors == {
            "revision_data": [
                "Unable to read the submitted dataset file. Please validate that the uploaded file can be read.",
            ]
        }


@pytest.mark.django_db
class TestLogFilterForm:
    def test_setup(self):
        assess = Assessment.objects.get(id=1)
        form = LogFilterSet(data={}, assessment=assess)
        assert form.is_valid()
        assert len(form.qs) > 1

        form = LogFilterSet(data=dict(object_id=999), assessment=assess)
        assert form.is_valid()
        assert len(form.qs) == 1


@pytest.mark.django_db
class TestAssessmentValueForm:
    valid_data = {
        "system": "nervous",
        "evaluation_type": 1,
        "value_type": 0,
        "value": 10.0,
        "value_unit": "mg/kg/day",
        "basis": "",
        "pod_type": "NOAEL",
        "pod_value": 100.0,
        "pod_unit": "mg/kg/day",
        "uncertainty": 10,
        "confidence": "Medium High",
        "species_studied": "",
        "duration": "1 week",
        "study": None,
        "tumor_type": "big",
        "extrapolation_method": "very carefully",
        "evidence": "strong evidence",
        "comments": "",
        "extra": "",
    }

    def test_errors(self, db_keys):
        assessment = Assessment.objects.get(id=db_keys.assessment_working)
        valid_data = self.valid_data.copy()
        form = AssessmentValueForm(data=valid_data, parent=assessment)
        assert form.is_valid()

        # Cancer fields aren't filled out
        data = valid_data.copy()
        data.update(evaluation_type=0, tumor_type="", extrapolation_method="", evidence="")
        form = AssessmentValueForm(data=data, parent=assessment)
        assert form.is_valid() is False
        error_str = "Required for Cancer evaluation types."
        assert form.errors == {
            "tumor_type": [error_str],
            "extrapolation_method": [error_str],
            "evidence": [error_str],
        }

        # Noncancer field isn't filled out
        data = valid_data.copy()
        data.update(evaluation_type=1, uncertainty=None)
        form = AssessmentValueForm(data=data, parent=assessment)
        assert form.is_valid() is False
        assert form.errors["uncertainty"] == ["Required for Noncancer evaluation types."]

        # pod/uncertainty != value
        data = valid_data.copy()
        data.update(uncertainty=100)
        form = AssessmentValueForm(data=data, parent=assessment)
        assert form.is_valid() is False
        assert form.errors["value"] == ["POD / uncertainty is not equal to value."]

    def test_extra(self, db_keys):
        assessment = Assessment.objects.get(id=db_keys.assessment_working)
        valid_data = self.valid_data.copy()

        # check that blank-like converted to empty dict
        for blank in ["{}", [], {}]:
            valid_data["extra"] = blank
            form = AssessmentValueForm(data=valid_data, parent=assessment)
            assert form.is_valid()
            assert form.cleaned_data["extra"] == {}

        # check that nested structures fail
        for invalid in [{"test": []}, {"test": {}}]:
            valid_data.update(extra=invalid)
            form = AssessmentValueForm(data=valid_data, parent=assessment)
            assert form.is_valid() is False
            assert "extra" in form.errors
