from typing import Dict, List, Optional, Tuple

import pandas as pd

from .client import BaseClient


class RiskOfBiasClient(BaseClient):
    """
    Client class for risk of bias requests.
    """

    def data(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves risk of bias data for the given assessment.
        This includes only final reviews.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            pd.DataFrame: Risk of bias data
        """
        url = f"{self.session.root_url}/rob/api/assessment/{assessment_id}/export/"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def full_data(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves full risk of bias data for the given assessment.
        This includes user-level reviews.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            pd.DataFrame: Full risk of bias data
        """
        url = f"{self.session.root_url}/rob/api/assessment/{assessment_id}/full-export/"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def create(
        self, study_id: int, author_id: int, active: bool, final: bool, scores: List[Dict]
    ) -> Dict:
        """
        Create a Risk of Bias review for a study. The review must be complete and contain answers for
        all required metrics.

        Args:
            study_id (int): id of study.
            author_id (int): id of author of the Risk of Bias data.
            active (bool): create the new Risk of Bias data as active or not
            final (bool): create the new Risk of Bias data as final or not
            scores (List[Dict]): List of scores. Each element of the List is a Dict containing the following
                                 string keys / expected values:
                * "metric_id" (int): the id of the metric for this score
                * "is_default" (bool): create this score as default or not
                * "label" (str): label for this score
                * "notes" (str): notes for this core
                * "score" (int): numeric score value. Actual legal values for this are dependent on the value
                                 of the HAWC_FLAVOR setting for this instance of HAWC and correspond to readable
                                 values like "Critically deficient" or "++". See also:
                                    hawc.apps.riskofbias.constants.SCORE_CHOICES
                                    + hawc.apps.riskofbias.constants.SCORE_SYMBOLS
                * bias_direction (int, optional): bias direction
                * "overridden_objects" (List[Dict], optional): a list of overrides for this particular score. Optional.
                                                     Each element of this List is a Dict containing the
                                                     following string keys / expected values:
                    * "content_type_name" (str): the name of the data type relevant to this override.
                    * "object_id" (int): the id of the particular instance of that data type relevant to this override.
        """
        payload = {
            "study_id": study_id,
            "author_id": author_id,
            "active": active,
            "final": final,
            "scores": scores,
        }
        url = f"{self.session.root_url}/rob/api/review/"
        return self.session.post(url, payload).json()

    def bulk_rob_copy(
        self,
        src_assessment_id: int,
        dst_assessment_id: int,
        src_dst_study_ids: List[Tuple[int, int]],
        src_dst_metric_ids: List[Tuple[int, int]],
        copy_mode: int,
        author_mode: int,
        dst_author_id: Optional[int] = None,
    ):
        """
        Copy final scores from a subset of studies from one assessment as the scores in a
        different assessment. Useful when an assessment is cloned or repurposed and existing
        evaluations should be used in a new evaluation.

        Args:
            src_assessment_id (int): source assessment
            dst_assessment_id (int): destination assessment
            src_dst_study_ids (List[Tuple[int, int]]): source study id, destination study id pairings
            src_dst_metric_ids (List[Tuple[int, int]]): source metric id, destination metric id pairings
            copy_mode (int): enum for copy mode
                1 = src active riskofbias -> dest active risk of bias
                2 = src final riskofbias -> dest initial risk of bias
            author_mode (int): enum for author mode
                1: original authors are preserved
                2: authors are overwritten by given dst_author_id
            dst_author_id (Optional[int]): author for destination RoBs when author_mode = 2.

        Returns:
            Dict: Log information and mapping of all source ids to destination ids
        """

        payload = {
            "src_assessment_id": src_assessment_id,
            "dst_assessment_id": dst_assessment_id,
            "src_dst_study_ids": src_dst_study_ids,
            "src_dst_metric_ids": src_dst_metric_ids,
            "copy_mode": copy_mode,
            "author_mode": author_mode,
        }
        if dst_author_id is not None:
            payload["dst_author_id"] = dst_author_id

        url = f"{self.session.root_url}/rob/api/assessment/bulk_rob_copy/"
        return self.session.post(url, payload).json()

    def metrics(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves all metrics for the given assessment.
        Args:
            assessment_id (int): Assessment ID
        Returns:
            pd.DataFrame: A dataframe of metrics
        """
        url = f"{self.session.root_url}/rob/api/metrics/?assessment_id={assessment_id}"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def reviews(self, assessment_id: int) -> Dict:
        """
        Retrieves all reviews for the given assessment.
        Args:
            assessment_id (int): Assessment ID
        Returns:
            pd.DataFrame: A dictionary of reviews
        """
        url = f"{self.session.root_url}/rob/api/review/?assessment_id={assessment_id}"
        return self.session.get(url).json()
