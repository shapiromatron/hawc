import pandas as pd
from django.conf import settings

from ..common.exports import ModelExport
from ..common.helper import FlatFileExporter
from ..common.models import sql_format
from .models import AssessmentValue


class DSSToxExport(ModelExport):
    def get_value_map(self):
        return {
            "dtxsid": "dtxsid",
            "dashboard_url": "dashboard_url",
            "img_url": "img_url",
            "content": "content",
            "created": "created",
            "last_updated": "last_updated",
        }

    def get_annotation_map(self, query_prefix):
        img_url_str = (
            f"https://api-ccte.epa.gov/chemical/file/image/search/by-dtxsid/{{}}?x-api-key={settings.CCTE_API_KEY}"
            if settings.CCTE_API_KEY
            else "https://comptox.epa.gov/dashboard-api/ccdapp1/chemical-files/image/by-dtxsid/{}"
        )
        return {
            "dashboard_url": sql_format(
                "https://comptox.epa.gov/dashboard/dsstoxdb/results?search={}",
                query_prefix + "dtxsid",
            ),
            "img_url": sql_format(img_url_str, query_prefix + "dtxsid"),
        }

    def prepare_df(self, df):
        return self.format_time(df)


class ValuesListExport(FlatFileExporter):
    def build_df(self) -> pd.DataFrame:
        return AssessmentValue.objects.get_df()
