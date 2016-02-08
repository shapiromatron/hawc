from utils.helper import FlatFileExporter
from . import models


class StudyQualityFlatComplete(FlatFileExporter):
    """
    Returns a complete export of all data required to rebuild
    study-quality data from scratch.
    """

    def _get_header_row(self):
        header = []
        header.extend(models.Study.flat_complete_header_row())
        header.extend(models.StudyQuality.flat_complete_header_row())
        return header

    def _get_data_rows(self):
        rows = []
        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)
            row = []
            row.extend(models.Study.flat_complete_data_row(ser))
            for sq in ser['qualities']:
                row_copy = list(row)  # clone
                row_copy.extend(models.StudyQuality.flat_complete_data_row(sq))
                rows.append(row_copy)
        return rows
