import json

import pandas as pd
from rest_framework import status
from rest_framework.renderers import BaseRenderer


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

        return self.render_dataframe(data)


class PandasHtmlRenderer(PandasBaseRenderer):
    """
    Renders dataframe as Html
    """

    media_type = "text/html"
    format = "html"

    def render_dataframe(self, df: pd.DataFrame) -> str:
        with pd.option_context("display.max_colwidth", -1):
            return df.fillna("-").to_html(index=False)


class PandasCsvRenderer(PandasBaseRenderer):
    """
    Renders dataframe as CSV
    """

    media_type = "text/csv"
    format = "csv"

    def render_dataframe(self, df: pd.DataFrame) -> str:
        return df.to_csv(index=False)


class PandasJsonRenderer(PandasBaseRenderer):
    """
    Renders dataframe as JSON
    """

    media_type = "application/json"
    format = "json"

    def render_dataframe(self, df: pd.DataFrame) -> str:
        return df.to_json(orient="records")


PandasRenderers = (PandasJsonRenderer, PandasHtmlRenderer, PandasCsvRenderer)
