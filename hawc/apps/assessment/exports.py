import pandas as pd

from ..common.helper import FlatFileExporter
from .models import AssessmentValue


class ValuesListExport(FlatFileExporter):
    def build_df(self) -> pd.DataFrame:
        return AssessmentValue.objects.get_df()
