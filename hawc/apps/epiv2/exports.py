from hawc.apps.common.helper import FlatFileExporter
from hawc.apps.study.models import Study
from . import models


class EpiFlatComplete(FlatFileExporter):
    """
    Returns a complete export of all data required to rebuild the the
    epidemiological meta-result study type from scratch.
    """

    def _get_header_row(self):
        header = []
        header.extend(Study.flat_complete_header_row())
        header.extend(models.Design.flat_complete_header_row())
        header.extend(models.Chemical.flat_complete_header_row())
        header.extend(models.Exposure.flat_complete_header_row())
        header.extend(models.ExposureLevel.flat_complete_header_row())
        header.extend(models.Outcome.flat_complete_header_row())
        header.extend(models.AdjustmentFactor.flat_complete_header_row())
        header.extend(models.DataExtraction.flat_complete_header_row())
        return header

    def _get_data_rows(self):
        rows = []
        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)
            row = []
            row.extend(Study.flat_complete_data_row(ser["design"]["study"]))
            row.extend(models.Design.flat_complete_data_row(ser["design"]))
            row.extend(models.Chemical.flat_complete_data_row(ser["exposure_level"]["chemical"]))
            row.extend(models.Exposure.flat_complete_data_row(ser["exposure_level"]["exposure"]))
            row.extend(models.ExposureLevel.flat_complete_data_row(ser["exposure_level"]))
            row.extend(models.Outcome.flat_complete_data_row(ser["outcome"]))
            row.extend(models.AdjustmentFactor.flat_complete_data_row(ser["adjustment_factor"]))
            row.extend(models.DataExtraction.flat_complete_data_row(ser))

            if len(ser["single_results"]) == 0:
                # print one-row with no single-results
                row.extend([None] * 10)
                rows.append(row)
            else:
                # print each single-result as a new row
                for sr in ser["single_results"]:
                    row_copy = list(row)  # clone
                    row_copy.extend(models.SingleResult.flat_complete_data_row(sr))
                    rows.append(row_copy)

        return rows
