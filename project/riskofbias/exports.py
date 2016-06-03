from . import models
from study.models import Study
from utils.helper import FlatFileExporter


class RiskOfBiasFlatPublic(FlatFileExporter):
    """
    Returns a complete export of active Final Risk of Bias reviews, without
    reviewer information.
    """

    def _get_header_row(self):
        header = []
        header.extend(Study.flat_complete_header_row())
        header.extend(models.RiskOfBiasScore.flat_complete_header_row())
        return header

    def _get_data_rows(self):
        rows = []
        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)
            row = []
            row.extend(Study.flat_complete_data_row(ser))
            for rob in ser['qualities']:
                row_copy = list(row)  # clone
                row_copy.extend(models.RiskOfBiasScore.flat_complete_data_row(rob))
                rows.append(row_copy)
        return rows

class RiskOfBiasFlatComplete(RiskOfBiasFlatPublic):
    """
    Returns a complete export of all Risk of Bias reviews including reviewer
    information.
    """

    def _get_header_row(self):
        header = super(RiskOfBiasFlatComplete, self)._get_header_row()
        header.extend(models.RiskOfBias.flat_complete_header_row())
        return header

    def _get_data_rows(self):
        rows = []
        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)
            row = []
            row.extend(Study.flat_complete_data_row(ser))
            for rob in ser['riskofbiases']:
                rob_data = models.RiskOfBias.flat_complete_data_row(rob)
                for score in rob['scores']:
                    row_copy = list(row)
                    row_copy.extend(models.RiskOfBiasScore.flat_complete_data_row(score))
                    row_copy.extend(rob_data)
                    rows.append(row_copy)
        return rows
