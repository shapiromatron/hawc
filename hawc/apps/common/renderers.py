import json
from io import BytesIO, StringIO
from typing import NamedTuple

import matplotlib.pyplot as plt
import pandas as pd
from django.conf import settings
from django.utils.text import slugify
from matplotlib.axes import Axes
from rest_framework import status
from rest_framework.renderers import BaseRenderer, BrowsableAPIRenderer
from rest_framework.response import Response

from .helper import FlatExport, ReportExport, rename_duplicate_columns


class DocxRenderer(BaseRenderer):
    """
    Renders a ReportExport object into a docx file.
    """

    media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    format = ""

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # return error or OPTIONS as JSON
        status_code = renderer_context["response"].status_code
        method = renderer_context["request"].method if "request" in renderer_context else None

        # throw error if we don't have a ReportExport
        if not isinstance(data, ReportExport):
            success = status.is_success(status_code)
            if (method == "OPTIONS" or not success) and isinstance(data, dict):
                return json.dumps(data)
            raise ValueError(f"Expecting `ReportExport`; got {type(data)}")

        file = BytesIO()
        data.docx.save(file)
        response = renderer_context["response"]
        response["Content-Disposition"] = f"attachment; filename={data.filename}.docx"
        return file.getvalue()


class SvgRenderer(BaseRenderer):
    media_type = "image/svg+xml"
    format = "svg"

    def render(self, ax: Axes, accepted_media_type=None, renderer_context=None):
        if isinstance(ax, dict):
            return f'<svg xmlns="http://www.w3.org/2000/svg"><text y="15">{json.dumps(ax)}</text></svg>'
        f = StringIO()
        ax.figure.savefig(f, format="svg")
        plt.close(ax.figure)
        return f.getvalue()


class PandasBaseRenderer(BaseRenderer):
    """
    Renders DataFrames using their built in pandas implementation.
    Borrowed heavily from `django-rest-pandas`.
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # return error or OPTIONS as JSON
        status_code = renderer_context["response"].status_code
        method = renderer_context["request"].method if "request" in renderer_context else None
        if not status.is_success(status_code) or method == "OPTIONS":
            if isinstance(data, dict):
                return json.dumps(data)
            else:
                raise ValueError(f"Expecting data as `dict`; got {type(data)}")

        # throw error if we don't have a FlatExport
        if not isinstance(data, FlatExport):
            raise ValueError(f"Expecting `FlatExport`; got {type(data)}")

        return self.render_dataframe(data, renderer_context["response"])


class PandasHtmlRenderer(PandasBaseRenderer):
    """
    Renders dataframe as Html
    """

    media_type = "text/html"
    format = "html"

    def render_dataframe(self, export: FlatExport, response: Response) -> str:
        with pd.option_context("display.max_colwidth", None):
            return export.df.fillna("-").to_html(index=False)


class PandasCsvRenderer(PandasBaseRenderer):
    """
    Renders dataframe as CSV
    """

    media_type = "text/csv"
    format = "csv"

    def render_dataframe(self, export: FlatExport, response: Response) -> str:
        # set line terminator to keep consistent on windows too
        return export.df.to_csv(index=False, lineterminator="\n")


class PandasTsvRenderer(PandasBaseRenderer):
    """
    Renders dataframe as TSV
    """

    media_type = "text/tab-separated-values"
    format = "tsv"

    def render_dataframe(self, export: FlatExport, response: Response) -> str:
        # set line terminator to keep consistent on windows too
        return export.df.to_csv(index=False, sep="\t", lineterminator="\n")


class PandasJsonRenderer(PandasBaseRenderer):
    """
    Renders dataframe as JSON
    """

    media_type = "application/json"
    format = "json"

    def render_dataframe(self, export: FlatExport, response: Response) -> str:
        if export.df.columns.has_duplicates:
            rename_duplicate_columns(export.df)
        return export.df.to_json(orient="records")


class PandasBrowsableAPIRenderer(BrowsableAPIRenderer):
    """
    Renders dataframe using the DRF browser.

    This can be useful in debugging to view the django debug toolbar
    for database query performance.
    """

    def get_content(self, renderer, data, accepted_media_type, renderer_context):
        # handle OPTIONS
        if isinstance(data, dict):
            return json.dumps(data, indent=4)

        # handle dataframe
        if data.df.columns.has_duplicates:
            rename_duplicate_columns(data.df)
        return data.df.to_json(orient="records", indent=4)


class BinaryXlsxDataFormat(NamedTuple):
    bytes: BytesIO
    filename: str


class XlsxBinaryRenderer(BaseRenderer):
    """
    Renders dataframe as xlsx
    """

    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    format = "xlsx"

    def render(self, data: BinaryXlsxDataFormat, accepted_media_type=None, renderer_context=None):
        # return error or OPTIONS as JSON
        status_code = renderer_context["response"].status_code
        method = renderer_context["request"].method if "request" in renderer_context else None
        if not status.is_success(status_code) or method == "OPTIONS":
            if isinstance(data, dict):
                return json.dumps(data)
            else:
                raise ValueError(f"Expecting data as `dict`; got {type(data)}")

        disposition = f"attachment; filename={slugify(data.filename)}.xlsx"
        renderer_context["response"]["Content-Disposition"] = disposition
        return data.bytes.getvalue()


class PandasXlsxRenderer(PandasBaseRenderer):
    """
    Renders dataframe as xlsx
    """

    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    format = "xlsx"

    def render_dataframe(self, export: FlatExport, response: Response) -> bytes:
        response["Content-Disposition"] = f"attachment; filename={slugify(export.filename)}.xlsx"
        f = export.to_excel()
        return f.getvalue()


PandasRenderers = [
    PandasJsonRenderer,
    PandasHtmlRenderer,
    PandasCsvRenderer,
    PandasTsvRenderer,
    PandasXlsxRenderer,
]

if settings.DEBUG:
    # insert at position 1 to keep JSON the default renderer
    PandasRenderers.insert(1, PandasBrowsableAPIRenderer)
