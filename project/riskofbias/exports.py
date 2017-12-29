from . import models
from study.models import Study
from utils.helper import FlatFileExporter


class RiskOfBiasFlat(FlatFileExporter):
    """
    Returns a complete export of active Final Study Evaluation reviews, without
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

            try:
                scores = [
                    rob['scores'] for rob in ser.get('riskofbiases', [])
                    if rob['final'] and rob['active']
                ][0]
            except IndexError:
                scores = []

            for score in scores:
                row_copy = list(row)  # clone
                row_copy.extend(models.RiskOfBiasScore.flat_complete_data_row(score))
                rows.append(row_copy)
        return rows


class RiskOfBiasCompleteFlat(RiskOfBiasFlat):
    """
    Returns a complete export of all Study Evaluation reviews including reviewer
    information.
    """

    def _get_header_row(self):
        header = super()._get_header_row()
        header.extend(models.RiskOfBias.flat_complete_header_row())
        return header

    def _get_data_rows(self):
        rows = []
        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)
            row = []
            row.extend(Study.flat_complete_data_row(ser))
            for rob in ser.get('riskofbiases', []):
                rob_data = models.RiskOfBias.flat_complete_data_row(rob)
                for score in rob['scores']:
                    row_copy = list(row)
                    row_copy.extend(models.RiskOfBiasScore.flat_complete_data_row(score))
                    row_copy.extend(rob_data)
                    rows.append(row_copy)
        return rows
