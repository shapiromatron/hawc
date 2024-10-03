import pandas as pd
import pytest
from django.test.client import RequestFactory

from hawc.apps.summary import constants, models


@pytest.mark.django_db
class TestSummaryTable:
    def test_build_default(self):
        # make sure 'build_default' returns a valid table
        for table_type in constants.TableType:
            instance = models.SummaryTable.build_default(1, table_type)
            assert instance.get_table() is not None

    def test_clean(self):
        table = models.SummaryTable.objects.get(id=1)
        table.clean()

    def test_docx(self):
        table = models.SummaryTable.objects.get(id=1)
        table.to_docx()


@pytest.mark.django_db
class TestVisual:
    def test_get_editing_dataset(self):
        obj = models.Visual.objects.filter(visual_type=constants.VisualType.ROB_HEATMAP).first()
        rf = RequestFactory()
        request = rf.get("/")
        obj.get_editing_dataset(request)

    def test_get_plotly_from_json(self):
        # fails with non plotly visual
        obj = models.Visual.objects.filter(
            visual_type=constants.VisualType.BIOASSAY_CROSSVIEW
        ).first()
        with pytest.raises(ValueError):
            obj.get_plotly_from_json()

        # works with plotly visual
        obj = models.Visual.objects.filter(visual_type=constants.VisualType.PLOTLY).first()
        obj.get_plotly_from_json()

    def test_data_df(self):
        # fails with some visuals
        obj = models.Visual.objects.filter(
            visual_type=constants.VisualType.BIOASSAY_CROSSVIEW
        ).first()
        with pytest.raises(ValueError):
            obj.get_plotly_from_json()

        # works with correct type
        obj = models.Visual.objects.filter(visual_type=constants.VisualType.ROB_HEATMAP).first()
        df = obj.data_df(use_settings=True)
        assert isinstance(df, pd.DataFrame)
        assert not df.empty


@pytest.mark.django_db
class TestDataPivot:
    def test_clean(self):
        obj = models.DataPivotQuery.objects.get(id=1)
        obj.clean()
