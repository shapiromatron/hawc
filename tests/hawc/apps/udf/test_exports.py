import pandas as pd

from hawc.apps.udf import exports


def test_expand_content():
    input = {
        "a": 1,
        "b": "b",
        "c": [],
        "d": [1, 2],
    }
    df = pd.DataFrame({"z": [input]})

    df2 = exports.expand_content(df, content_column="z", flatten=False)
    assert df2.to_dict(orient="records")[0] == {
        "z-field-a": 1,
        "z-field-b": "b",
        "z-field-c": [],
        "z-field-d": [1, 2],
    }

    df2 = exports.expand_content(df, content_column="z", flatten=True)
    assert df2.to_dict(orient="records")[0] == {
        "z-field-a": 1,
        "z-field-b": "b",
        "z-field-c": "",
        "z-field-d": "1|2",
    }
