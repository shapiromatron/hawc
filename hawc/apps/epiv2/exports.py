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
        header.extend(models.DataExtraction.flat_complete_header_row())
        header.extend(models.AdjustmentFactor.flat_complete_header_row())
        return header

    def get_optimized_queryset(self):
        return self.queryset.select_related(
            "exposure_level__exposure_measurement",
            "exposure_level__chemical__dsstox",
            "factors",
            "outcome",
            "design__study",
        ).prefetch_related("design__countries")

    def _get_data_rows(self):
        rows = []
        identifiers_df = Study.identifiers_df(self.queryset, "design__study_id")
        n_col_factors = len(models.AdjustmentFactor.flat_complete_header_row())
        for obj in self.get_optimized_queryset():
            row = []
            row.extend(
                Study.flat_complete_data_row(
                    obj.design.study.get_json(json_encode=False), identifiers_df
                )
            )
            row.extend(obj.design.flat_complete_data_row())
            row.extend(obj.exposure_level.chemical.flat_complete_data_row())
            row.extend(obj.exposure_level.exposure_measurement.flat_complete_data_row())
            row.extend(obj.exposure_level.flat_complete_data_row())
            row.extend(obj.outcome.flat_complete_data_row())
            row.extend(obj.flat_complete_data_row())
            row.extend(
                obj.factors.flat_complete_data_row() if obj.factors else [None] * n_col_factors
            )
            rows.append(row)
        return rows
