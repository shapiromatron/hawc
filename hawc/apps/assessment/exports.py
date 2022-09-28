import pandas as pd

from hawc.apps.assessment.models import AssessmentValue
from hawc.apps.common.helper import FlatFileExporter


class ValuesListExport(FlatFileExporter):
    def build_df(self) -> pd.DataFrame:
        return AssessmentValue.objects.get_df()
