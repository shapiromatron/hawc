import pandas as pd

from ..common.helper import FlatFileExporter


class EcoFlatComplete(FlatFileExporter):
    def build_df(self) -> pd.DataFrame:
        return self.queryset.complete_df()
