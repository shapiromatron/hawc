import time
from io import StringIO
from pathlib import Path

import pandas as pd

from hawc.apps.common import helper


def test_create_uuid():
    # Make sure UUID creation is stable over time
    id_1 = 1234
    uuid_1 = helper.create_uuid(id_1)
    time.sleep(1)
    assert uuid_1 == helper.create_uuid(id_1)

    # Simple test to ensure our UUID creation is unique
    id_2 = 12345
    uuid_2 = helper.create_uuid(id_2)
    assert uuid_1 != uuid_2


class TestFlatFileExporter:
    def test_get_flattened_tags(self):
        # check if key doesn't exist
        assert helper.FlatFileExporter.get_flattened_tags({}, "nope") == "||"

        # check if key doesn't exist but no values
        assert helper.FlatFileExporter.get_flattened_tags({"hi": []}, "hi") == "||"

        # check if key exists and there are values
        assert (
            helper.FlatFileExporter.get_flattened_tags({"hi": [{"name": "a"}, {"name": "b"}]}, "hi")
            == "|a|b|"
        )


def test_df_move_column():
    df = pd.read_csv(StringIO("a,b,c\n1,2,3"))

    # check expected behavior
    df2 = helper.df_move_column(df, "c", "a")
    assert df2.columns.tolist() == ["a", "c", "b"]
    assert df2.c.iloc[0] == 3

    # check optional argument
    df2 = helper.df_move_column(df, "c")
    assert df2.columns.tolist() == ["c", "a", "b"]
    assert df2.c.iloc[0] == 3

    # no change to original dataframe
    assert df.columns.tolist() == ["a", "b", "c"]


def test_tryParseInt():
    assert helper.tryParseInt(None) is None
    assert helper.tryParseInt("") is None
    assert helper.tryParseInt("", default=0) == 0
    assert helper.tryParseInt("10") == 10
    assert helper.tryParseInt(123.5) == 123
    assert helper.tryParseInt(-1, min_value=0) == 0
    assert helper.tryParseInt(1e6, max_value=1) == 1


def test_try_parse_list_ints():
    # expected None case
    assert helper.try_parse_list_ints(None) == []

    # expected str cases
    assert helper.try_parse_list_ints("") == []
    assert helper.try_parse_list_ints("1,2,3") == [1, 2, 3]
    assert helper.try_parse_list_ints("123") == [123]
    assert helper.try_parse_list_ints("1, 2 , 3 ") == [1, 2, 3]

    # edge cases
    assert helper.try_parse_list_ints("a") == []
    assert helper.try_parse_list_ints("1,a") == []


def test_read_excel():
    # excel file should be read in as a dataframe without error
    iris_xlsx_fn = str(
        Path(__file__).parents[3] / "data/private-data/assessment/dataset-revision/iris.xlsx"
    )
    df = helper.read_excel(iris_xlsx_fn)
    assert not df.empty
