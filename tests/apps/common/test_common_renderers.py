import json
from io import BytesIO

import pandas as pd
import pytest
from rest_framework.response import Response

from hawc.apps.common import renderers
from hawc.apps.common.helper import FlatExport


@pytest.fixture
def basic_export():
    df = pd.DataFrame(data=[[1, 2], [3, 4]], columns=["a", "b"])
    return FlatExport(df=df, filename="fn")


def test_base_renderer():
    # test that our data-check passes; we use the Csv subclass to check
    with pytest.raises(ValueError):
        renderers.PandasCsvRenderer().render(
            data="not-a-dataframe", renderer_context={"response": Response()}
        )


def test_csv_renderer(basic_export):
    response = renderers.PandasCsvRenderer().render(
        data=basic_export, renderer_context={"response": Response()}
    )
    assert response == "a,b\n1,2\n3,4\n"


def test_tsv_renderer(basic_export):
    response = renderers.PandasTsvRenderer().render(
        data=basic_export, renderer_context={"response": Response()}
    )
    assert response == "a\tb\n1\t2\n3\t4\n"


def test_html_renderer(basic_export):
    response = renderers.PandasHtmlRenderer().render(
        data=basic_export, renderer_context={"response": Response()}
    )
    assert (
        response
        == '<table border="1" class="dataframe">\n  <thead>\n    <tr style="text-align: right;">\n      <th>a</th>\n      <th>b</th>\n    </tr>\n  </thead>\n  <tbody>\n    <tr>\n      <td>1</td>\n      <td>2</td>\n    </tr>\n    <tr>\n      <td>3</td>\n      <td>4</td>\n    </tr>\n  </tbody>\n</table>'
    )


def test_json_renderer(basic_export):
    response = renderers.PandasJsonRenderer().render(
        data=basic_export, renderer_context={"response": Response()}
    )
    assert json.loads(response) == [{"a": 1, "b": 2}, {"a": 3, "b": 4}]


def test_xlsx_renderer(basic_export):
    resp_obj = Response()
    assert "Content-Disposition" not in resp_obj

    response = renderers.PandasXlsxRenderer().render(
        data=basic_export, renderer_context={"response": resp_obj}
    )
    df2 = pd.read_excel(BytesIO(response))
    assert df2.to_dict(orient="records") == [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    assert resp_obj["Content-Disposition"] == "attachment; filename=fn.xlsx"

    # Datetimes with timezones are incompatible with Excel. Make sure that the renderer can handle DataFrames with timezoned datetimes.
    df = pd.DataFrame(
        data=[[1, "2000-01-01 01:00:00"], [2, "2005-12-31 02:10:00"]], columns=["count", "when"],
    )
    df.loc[:, "when"] = df.when.astype("datetime64")
    basic_export

    # naive datetime
    response = renderers.PandasXlsxRenderer().render(
        data=FlatExport(df=df, filename="fn"), renderer_context={"response": Response()}
    )
    df2 = pd.read_excel(BytesIO(response))
    assert df2.equals(df)

    # with timezone
    df.loc[:, "when"] = df.when.dt.tz_localize(tz="US/Eastern")
    response = renderers.PandasXlsxRenderer().render(
        data=FlatExport(df=df, filename="fn"), renderer_context={"response": Response()}
    )
    df2 = pd.read_excel(BytesIO(response))

    # expected; we lost the timezone
    with pytest.raises(TypeError) as err:
        assert df2.equals(df) is False
    assert "data type not understood" in str(err)

    # with appropriate cast, success!
    df2.loc[:, "when"] = df2.when.astype("datetime64").dt.tz_localize(tz="US/Eastern")
    assert df2.equals(df) is True
