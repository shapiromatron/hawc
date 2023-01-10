from ..common.helper import FlatFileExporter, get_study_export_identifiers
from ..study.models import Study
from . import models


class MetaResultFlatComplete(FlatFileExporter):
    """
    Returns a complete export of all data required to rebuild the the
    epidemiological meta-result study type from scratch.
    """

    def _get_header_row(self):
        header = []
        header.extend(Study.flat_complete_header_row())
        header.extend(models.MetaProtocol.flat_complete_header_row())
        header.extend(models.MetaResult.flat_complete_header_row())
        header.extend(models.SingleResult.flat_complete_header_row())
        return header

    def _get_data_rows(self):
        rows = []
        identifiers_df = get_study_export_identifiers(self.queryset, "protocol__study_id")
        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)
            row = []
            row.extend(Study.flat_complete_data_row(ser["protocol"]["study"], identifiers_df))
            row.extend(models.MetaProtocol.flat_complete_data_row(ser["protocol"]))
            row.extend(models.MetaResult.flat_complete_data_row(ser))

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


class MetaResultFlatDataPivot(FlatFileExporter):
    """
    Return a subset of frequently-used data for generation of data-pivot
    visualizations.

    Note: data pivot does not currently include study confidence. Could be added if needed.
    """

    def _get_header_row(self):
        return [
            "study id",
            "study name",
            "study published",
            "protocol id",
            "protocol name",
            "protocol type",
            "total references",
            "identified references",
            "key",
            "meta result id",
            "meta result label",
            "health outcome",
            "exposure",
            "result references",
            "statistical metric",
            "statistical metric abbreviation",
            "N",
            "estimate",
            "lower CI",
            "upper CI",
            "CI units",
            "heterogeneity",
        ]

    def _get_data_rows(self):
        rows = []
        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)
            row = [
                ser["protocol"]["study"]["id"],
                ser["protocol"]["study"]["short_citation"],
                ser["protocol"]["study"]["published"],
                ser["protocol"]["id"],
                ser["protocol"]["name"],
                ser["protocol"]["protocol_type"],
                ser["protocol"]["total_references"],
                ser["protocol"]["total_studies_identified"],
                ser["id"],  # repeat for data-pivot key
                ser["id"],
                ser["label"],
                ser["health_outcome"],
                ser["exposure_name"],
                ser["number_studies"],
                ser["metric"]["metric"],
                ser["metric"]["abbreviation"],
                ser["n"],
                ser["estimate"],
                ser["lower_ci"],
                ser["upper_ci"],
                ser["ci_units"],
                ser["heterogeneity"],
            ]
            rows.append(row)

        return rows
