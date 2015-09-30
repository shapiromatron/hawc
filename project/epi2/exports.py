from study.models import Study
from utils.helper import FlatFileExporter

from . import models


class OutcomeFlatComplete(FlatFileExporter):

    def _get_header_row(self):
        header = []
        header.extend(Study.flat_complete_header_row())
        header.extend(models.StudyPopulation.flat_complete_header_row())
        header.extend(models.Outcome.flat_complete_header_row())
        header.extend(models.Exposure2.flat_complete_header_row())
        header.extend(models.ComparisonGroups.flat_complete_header_row())
        header.extend(models.Result.flat_complete_header_row())
        header.extend(models.Group.flat_complete_header_row())
        header.extend(models.GroupResult.flat_complete_header_row())
        return header

    def _get_data_rows(self):
        rows = []
        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)
            row = []
            row.extend(Study.flat_complete_data_row(ser['study_population']['study']))
            row.extend(models.StudyPopulation.flat_complete_data_row(ser['study_population']))
            row.extend(models.Outcome.flat_complete_data_row(ser))
            for res in ser['results']:
                row_copy = list(row)
                row_copy.extend(models.Exposure2.flat_complete_data_row(res["groups"]["exposure"]))
                row_copy.extend(models.ComparisonGroups.flat_complete_data_row(res["groups"]))
                row_copy.extend(models.Result.flat_complete_data_row(res))
                for rg in res['results']:
                    row_copy2 = list(row_copy)
                    row_copy2.extend(models.Group.flat_complete_data_row(rg["group"]))
                    row_copy2.extend(models.GroupResult.flat_complete_data_row(rg))
                    rows.append(row_copy2)
        return rows
