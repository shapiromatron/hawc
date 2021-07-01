from ..common.helper import FlatFileExporter
from ..study.models import Study
from . import models


class RiskOfBiasFlat(FlatFileExporter):
    """
    Returns a complete export of active Final Risk of Bias reviews, without
    reviewer information.
    """

    final_only = True  # only return final data

    def _get_header_row(self):
        header = []
        header.extend(Study.flat_complete_header_row())
        header.extend(models.RiskOfBias.flat_header_row(final_only=self.final_only))
        header.extend(models.RiskOfBiasScore.flat_complete_header_row())
        return header

    def _get_data_rows(self):
        rows = []
        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)

            domains = ser["rob_settings"]["domains"]
            metrics = ser["rob_settings"]["metrics"]
            domain_map = {domain["id"]: domain for domain in domains}
            metric_map = {
                metric["id"]: dict(metric, domain=domain_map[metric["domain_id"]])
                for metric in metrics
            }

            row1 = []
            row1.extend(Study.flat_complete_data_row(ser))

            robs = [rob for rob in ser.get("riskofbiases", [])]
            if self.final_only:
                robs = [rob for rob in robs if rob["final"] and rob["active"]]

            for rob in robs:
                row2 = list(row1)
                row2.extend(models.RiskOfBias.flat_data_row(rob, final_only=self.final_only))
                for score in rob["scores"]:
                    row3 = list(row2)
                    score["metric"] = metric_map[score["metric_id"]]
                    row3.extend(models.RiskOfBiasScore.flat_complete_data_row(score))
                    rows.append(row3)

        return rows


class RiskOfBiasCompleteFlat(RiskOfBiasFlat):
    """
    Returns a complete export of all Risk of Bias reviews including reviewer
    information.
    """

    final_only = False
