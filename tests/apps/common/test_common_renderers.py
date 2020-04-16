import json
from io import BytesIO

import pandas as pd
import numpy as np
import pytest
from rest_framework.response import Response

from hawc.apps.common import renderers


def test_base_renderer():
    # test that our data-check passes; we use the Csv subclass to check
    with pytest.raises(ValueError):
        renderers.PandasCsvRenderer().render(data="not-a-dataframe", renderer_context={"response": Response()})


def test_csv_renderer():
    df = pd.DataFrame(data=[[1, 2], [3, 4]], columns=["a", "b"])
    response = renderers.PandasCsvRenderer().render(data=df, renderer_context={"response": Response()})
    assert response == "a,b\n1,2\n3,4\n"


def test_html_renderer():
    df = pd.DataFrame(data=[[1, 2], [3, 4]], columns=["a", "b"])
    response = renderers.PandasHtmlRenderer().render(data=df, renderer_context={"response": Response()})
    assert (
        response
        == '<table border="1" class="dataframe">\n  <thead>\n    <tr style="text-align: right;">\n      <th>a</th>\n      <th>b</th>\n    </tr>\n  </thead>\n  <tbody>\n    <tr>\n      <td>1</td>\n      <td>2</td>\n    </tr>\n    <tr>\n      <td>3</td>\n      <td>4</td>\n    </tr>\n  </tbody>\n</table>'
    )


def test_json_renderer():
    df = pd.DataFrame(data=[[1, 2], [3, 4]], columns=["a", "b"])
    response = renderers.PandasJsonRenderer().render(data=df, renderer_context={"response": Response()})
    assert json.loads(response) == [{"a": 1, "b": 2}, {"a": 3, "b": 4}]


def test_xlsx_renderer():
    df = pd.DataFrame(data=[[1, 2], [3, 4]], columns=["a", "b"])
    resp_obj = Response()
    assert "Content-Disposition" not in resp_obj

    response = renderers.PandasXlsxRenderer().render(data=df, renderer_context={"response": resp_obj})
    df2 = pd.read_excel(BytesIO(response))
    assert df2.to_dict(orient="records") == [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    assert "Content-Disposition" in "Content-Disposition" and "attachment; filename=" in resp_obj["Content-Disposition"]

    # Datetimes with timezones are incompatible with Excel. Make sure that the renderer can handle DataFrames with timezoned datetimes.

    datetimes = np.array(["2000-01-01 01:00:00", "2005-12-31 02:10:00", "2010-06-01 03:20:10"], dtype="datetime64")
    datetimes_series = pd.Series(datetimes).dt.tz_localize(tz="US/Eastern")

    df = pd.DataFrame(data=[1, 2, 3], columns=["count"])
    df["when"] = datetimes_series

    resp_obj = Response()
    response = renderers.PandasXlsxRenderer().render(data=df, renderer_context={"response": resp_obj})

    df2 = pd.read_excel(BytesIO(response))

    assert df2.equals(df)
