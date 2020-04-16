import json
from io import BytesIO

import pandas as pd
from rest_framework import status
from rest_framework.renderers import BaseRenderer
from rest_framework.response import Response


class PandasBaseRenderer(BaseRenderer):
    """
    Renders DataFrames using their built in pandas implementation.
    Borrowed heavily from `django-rest-pandas`.
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):

        # return error in JSON
        status_code = renderer_context["response"].status_code
        if not status.is_success(status_code):
            if isinstance(data, dict):
                return json.dumps(data)

        # throw error if we don't have a data frame
        if not isinstance(data, pd.DataFrame):
            raise ValueError(f"Expecting data frame; got {type(data)}")

        return self.render_dataframe(data, renderer_context["response"])


class PandasHtmlRenderer(PandasBaseRenderer):
    """
    Renders dataframe as Html
    """

    media_type = "text/html"
    format = "html"

    def render_dataframe(self, df: pd.DataFrame, response: Response) -> str:
        with pd.option_context("display.max_colwidth", -1):
            return df.fillna("-").to_html(index=False)


class PandasCsvRenderer(PandasBaseRenderer):
    """
    Renders dataframe as CSV
    """

    media_type = "text/csv"
    format = "csv"

    def render_dataframe(self, df: pd.DataFrame, response: Response) -> str:
        # set line terminator to keep consistent on windows too
        return df.to_csv(index=False, line_terminator="\n")


class PandasJsonRenderer(PandasBaseRenderer):
    """
    Renders dataframe as JSON
    """

    media_type = "application/json"
    format = "json"

    def render_dataframe(self, df: pd.DataFrame, response: Response) -> str:
        return df.to_json(orient="records")


class PandasXlsxRenderer(PandasBaseRenderer):
    """
    Renders dataframe as xlsx
    """

    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    format = "xlsx"
    charset = None
    render_style = "binary"

    def render_dataframe(self, df: pd.DataFrame, response: Response) -> bytes:
        response["Content-Disposition"] = "attachment; filename=hawc-export.xlsx"

        # We have to remove the timezone from datetime objects to make it Excel compatible
        ## Note: DataFrame update doesn't preserve dtype, so we must iterate through the columns instead
        df_datetime = df.select_dtypes(include="datetimetz").apply(lambda x: x.dt.tz_localize(None))
        for col in df_datetime.columns:
            df[col] = df_datetime[col]

        f = BytesIO()
        with pd.ExcelWriter(
            f, date_format="YYYY-MM-DD", datetime_format="YYYY-MM-DD HH:MM:SS"
        ) as writer:
            df.to_excel(writer, index=False)
        return f.getvalue()


PandasRenderers = (PandasJsonRenderer, PandasHtmlRenderer, PandasCsvRenderer, PandasXlsxRenderer)
