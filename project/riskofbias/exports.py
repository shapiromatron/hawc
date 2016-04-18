from . import models
from study.models import Study
from utils.helper import FlatFileExporter


class RiskOfBiasFlatComplete(FlatFileExporter):
    """
    Returns a complete export of all data required to rebuild
    study-quality data from scratch.
    """

    def _get_header_row(self):
        header = []
        header.extend(Study.flat_complete_header_row())
        header.extend(models.RiskOfBias.flat_complete_header_row())
        return header

    def _get_data_rows(self):
        rows = []
        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)
            row = []
            row.extend(Study.flat_complete_data_row(ser))
            for rob in ser['qualities']:
                row_copy = list(row)  # clone
                row_copy.extend(models.RiskOfBias.flat_complete_data_row(rob))
                rows.append(row_copy)
        return rows
