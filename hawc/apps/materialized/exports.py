import pandas as pd

from ..common.helper import unique_text_list
from .models import FinalRiskOfBiasScore


def get_final_score_df(assessment_id: int, ids: list[int], model: str) -> pd.DataFrame:
    rob_headers, rob_data = FinalRiskOfBiasScore.get_dp_export(assessment_id, ids, model)
    return pd.DataFrame(
        data=[[rob_data[(id, metric_id)] for metric_id in rob_headers.keys()] for id in ids],
        columns=unique_text_list(list(rob_headers.values())),
        index=ids,
    )
