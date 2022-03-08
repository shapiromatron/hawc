import pytest

from hawc.apps.summary import constants, models


@pytest.mark.django_db
class TestSummaryTable:
    def test_build_default(self):
        # make sure 'build_default' returns a valid table
        for table_type in constants.TableType:
            instance = models.SummaryTable.build_default(1, table_type)
            assert instance.get_table() is not None
