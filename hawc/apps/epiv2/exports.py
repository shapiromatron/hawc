import pandas as pd

from hawc.apps.common.helper import FlatFileExporter


class EpiFlatComplete(FlatFileExporter):
    """
    Returns a complete export of all data required to rebuild the the
    epidemiological meta-result study type from scratch.
    """

    def build_df(self) -> pd.DataFrame:
        return self.queryset.complete_df()
