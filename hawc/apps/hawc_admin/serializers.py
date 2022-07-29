from hawc.apps.assessment.models import Values
from hawc.apps.common.helper import FlatExport


class ValuesExportOptions:
    @classmethod
    def build_export(cls):
        df = Values.get_df()
        # TODO: improve filename (include slug of datetime?)
        return FlatExport(df, "HAWC-assessment-values")
