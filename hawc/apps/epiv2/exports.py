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
            row = []
            row.extend(Study.flat_complete_data_row(obj.design.study.get_json(json_encode=False)))
            row.extend(models.Design.flat_complete_data_row(obj.design))
            row.extend(models.Chemical.flat_complete_data_row(obj.exposure_level.chemical))
            row.extend(
                models.Exposure.flat_complete_data_row(obj.exposure_level.exposure_measurement)
            )
            row.extend(models.ExposureLevel.flat_complete_data_row(obj.exposure_level))
            row.extend(models.Outcome.flat_complete_data_row(obj.outcome))
            row.extend(models.AdjustmentFactor.flat_complete_data_row(obj.factors))
            row.extend(models.DataExtraction.flat_complete_data_row(obj))
        return rows
