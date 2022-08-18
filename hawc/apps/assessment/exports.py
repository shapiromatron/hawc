import pandas as pd

from hawc.apps.assessment.models import Values
from hawc.apps.common.helper import FlatFileExporter


class ValuesListExport(FlatFileExporter):
    def build_df(self) -> pd.DataFrame:
        return Values.get_df(self.queryset)
