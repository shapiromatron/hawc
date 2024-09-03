from io import StringIO

import pandas as pd
import pytest
from django.core.exceptions import ValidationError as DjangoValidationError
from pydantic import BaseModel
from rest_framework.serializers import ValidationError as DRFValidationError

from hawc.apps.common import helper


def test_rename_duplicate_columns():
    df = pd.DataFrame(data=[[1, 2]], columns=["a", "b"])
    assert helper.rename_duplicate_columns(df).columns.tolist() == ["a", "b"]

    df = pd.DataFrame(data=[[1, 2]], columns=["a", "a"])
    assert helper.rename_duplicate_columns(df).columns.tolist() == ["a.1", "a.2"]

    df = pd.DataFrame(data=[[1, 2, 3]], columns=["a", "b", "a"])
    assert helper.rename_duplicate_columns(df).columns.tolist() == ["a.1", "b", "a.2"]


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


@pytest.mark.parametrize(
    "kw,expected",
    [
        [dict(items=list("abcde"), target="c", after="b", n_cols=2), "abcde"],
        [dict(items=list("abcde"), target="b", after=None), "bacde"],
        [dict(items=list("abcde"), target="c", after="a", n_cols=2), "acdbe"],
        [dict(items=list("abcde"), target="d", after="b"), "abdce"],
        [dict(items=list("abcde"), target="b", after="d", n_cols=2), "adbce"],
    ],
)
def test_reorder_list(kw, expected):
    assert "".join(helper.reorder_list(**kw)) == expected


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


def test_url_query():
    assert helper.url_query("/", {}) == "/"
    assert helper.url_query("/path/", {"test": 123, "here": 456}) == "/path/?test=123&here=456"
    assert (
        helper.url_query("/path/", {"?=&/\\": "?=&/\\"}) == "/path/?%3F%3D%26%2F%5C=%3F%3D%26%2F%5C"
    )


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


def test_int_or_float():
    assert helper.int_or_float(0.0) == 0
    assert helper.int_or_float(1.0) == 1
    assert helper.int_or_float(3.14) == 3.14
    assert helper.int_or_float(1.00001) == 1.00001
    assert helper.int_or_float(123456.0) == 123456


class ChildSchema(BaseModel):
    integer: int


class Schema(BaseModel):
    string: str
    children: list[ChildSchema]


class TestPydanticToDjangoError:
    bad_obj = {"children": [{"integer": "test"}, {}]}
    err_messages = [
        "string: Field required",
        "children->0->integer: Input should be a valid integer, unable to parse string as an integer",
        "children->1->integer: Field required",
    ]

    def test_django_error(self):
        with pytest.raises(DjangoValidationError) as err:
            with helper.PydanticToDjangoError(drf=False):
                Schema.model_validate(self.bad_obj)
        assert err.value.args[0] == {"__all__": self.err_messages}

    def test_drf_error(self):
        with pytest.raises(DRFValidationError) as err:
            with helper.PydanticToDjangoError(drf=True):
                Schema.model_validate(self.bad_obj)
        assert err.value.args[0] == {"non_field_errors": self.err_messages}

    def test_fields(self):
        # don't include a field; useful for field in form validation
        with pytest.raises(DjangoValidationError) as err:
            with helper.PydanticToDjangoError(include_field=False):
                Schema.model_validate(self.bad_obj)
        assert err.value.args[0] == self.err_messages

        # specify the field; useful for form validation
        with pytest.raises(DjangoValidationError) as err:
            with helper.PydanticToDjangoError(field="field"):
                Schema.model_validate(self.bad_obj)
        assert err.value.args[0] == {"field": self.err_messages}


@pytest.mark.parametrize(
    "input,expected",
    [
        ([[1, 2], [3, 4]], [1, 2, 3, 4]),  # list
        ([(1, 2), (3, 4)], [1, 2, 3, 4]),  # tuple
        ([(1, [2]), (3, 4)], [1, [2], 3, 4]),  # nested
    ],
)
def test_flatten(input, expected):
    assert list(helper.flatten(input)) == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        ([], []),
        (["a"], ["a"]),
        (["a", "a", "a"], ["a", "a (2)", "a (3)"]),
        (["a", "b", "a"], ["a", "b", "a (2)"]),
    ],
)
def test_unique_text_list(input, expected):
    assert list(helper.unique_text_list(input)) == expected
