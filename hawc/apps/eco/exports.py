from hawc.apps.common.helper import FlatFileExporter
from hawc.apps.study.models import Study


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
