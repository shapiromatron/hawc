from . import models

from hawc.apps.common.helper import FlatFileExporter
from hawc.apps.study.models import Study

class EcoFlatComplete(FlatFileExporter):
    """
    Returns a complete export of all data required to rebuild the the
    epidemiological meta-result study type from scratch.
    """
    def _get_header_row(self):
        header = []
        header.extend(Study.flat_complete_header_row())
        header.extend(models.Design.flat_complete_header_row())
        header.extend(models.Cause.flat_complete_header_row())
        header.extend(models.Effect.flat_complete_header_row()),
        header.extend(models.Result.flat_complete_header_row()),
        return header

    def get_optimized_queryset(self):
        return self.queryset.select_related(
            "cause",
            "effect",
            "design__study",
        ).prefetch_related("design__countries", "design__states")

    def _get_data_rows(self):
        rows = []
        identifiers_df = Study.identifiers_df(self.queryset, "design__study_id")
        for obj in self.get_optimized_queryset():
            row = []
            row.extend(
                Study.flat_complete_data_row(
                    obj.design.study.get_json(json_encode=False), identifiers_df
                )
            )
            row.extend(obj.design.flat_complete_data_row())
            row.extend(obj.cause.flat_complete_data_row())
            row.extend(obj.effect.flat_complete_data_row())
            row.extend(obj.flat_complete_data_row())
            rows.append(row)
        return rows


class EcoStudyComplete(FlatFileExporter):
    def _get_header_row(self):
        header = []
        header.extend(Study.flat_complete_header_row())
        return header

    def get_optimized_queryset(self):
        return self.queryset.select_related(
            "design__study",
            "design__study_setting",
            "cause__term",
            "cause__biological_organization",
            "effect__term",
            "effect__biological_organization",
            "statistical_sig_type",
            "measure_type",
            "variability",
        ).prefetch_related(
            "design__countries",
            "design__states",
            "design__ecoregions",
            "design__habitats",
            "design__climates",
        )

    def _get_data_rows(self):
        rows = []
        identifiers_df = Study.identifiers_df(self.queryset, "design__study_id")
        for obj in self.get_optimized_queryset():
            row = []
            row.extend(
                Study.flat_complete_data_row(
                    obj.design.study.get_json(json_encode=False), identifiers_df
                )
            )
            rows.append(row)
        return rows
