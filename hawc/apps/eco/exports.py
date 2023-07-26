import pandas as pd

from hawc.apps.common.helper import FlatFileExporter


class EcoFlatComplete(FlatFileExporter):
    """
    Returns a complete export of all data required to rebuild the
    ecology study type from scratch.
    """

    def build_df(self) -> pd.DataFrame:
        data = self.queryset.values_list("id", flat=True)
        headers = ["id"]
        return pd.DataFrame(data=data, columns=headers)
