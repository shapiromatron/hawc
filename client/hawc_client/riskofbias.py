import pandas as pd

from .client import BaseClient
from .utils import fuzz_match


class RiskOfBiasClient(BaseClient):
    """
    Client class for risk of bias requests.
    """

    def export(self, assessment_id: int) -> pd.DataFrame:
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

    def full_export(self, assessment_id: int) -> pd.DataFrame:
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
        self, study_id: int, author_id: int, active: bool, final: bool, scores: list[dict]
    ) -> dict:
        """
        Create a Risk of Bias review for a study. The review must be complete and contain answers for
        all required metrics.

        Args:
            study_id (int): id of study.
            author_id (int): id of author of the Risk of Bias data.
            active (bool): create the new Risk of Bias data as active or not
            final (bool): create the new Risk of Bias data as final or not
            scores (list[dict]): List of scores. Each element of the list is a dict containing the following
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
                * "overridden_objects" (list[dict], optional): a list of overrides for this particular score. Optional.
                                                     Each element of this list is a dict containing the
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
        src_dst_study_ids: list[tuple[int, int]],
        src_dst_metric_ids: list[tuple[int, int]],
        copy_mode: int,
        author_mode: int,
        dst_author_id: int | None = None,
    ):
        """
        Copy final scores from a subset of studies from one assessment as the scores in a
        different assessment. Useful when an assessment is cloned or repurposed and existing
        evaluations should be used in a new evaluation. You must be a project-manager on both
        assessments.

        Args:
            src_assessment_id (int): source assessment
            dst_assessment_id (int): destination assessment
            src_dst_study_ids (list[tuple[int, int]]): source study id, destination study id pairings
            src_dst_metric_ids (list[tuple[int, int]]): source metric id, destination metric id pairings
            copy_mode (int): enum for copy mode
                1 = src active riskofbias -> dest active risk of bias
                2 = src final riskofbias -> dest initial risk of bias
            author_mode (int): enum for author mode
                1: original authors are preserved
                2: authors are overwritten by given dst_author_id
            dst_author_id (Optional[int]): author for destination RoBs when author_mode = 2.

        Returns:
            dict: Log information and mapping of all source ids to destination ids
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
        url = f"{self.session.root_url}/rob/api/metric/?assessment_id={assessment_id}"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def reviews(self, assessment_id: int, study_id: int | None = None) -> dict:
        """
        Retrieves all reviews for the given assessment. Must be team member or higher
        Args:
            assessment_id (int): Assessment ID
            study_id (int | None): A study ID; returns results for a single study
        Returns:
            dict: A dictionary of reviews
        """
        url = f"{self.session.root_url}/rob/api/review/?assessment_id={assessment_id}"
        if study_id:
            url += f"&study={study_id}"
        return self.session.get(url).json()

    def final_reviews(self, assessment_id: int, study_id: int | None = None) -> dict:
        """
        Retrieves all final reviews for the given assessment.
        Args:
            assessment_id (int): Assessment ID
            study_id (int | None): A study ID; returns results for a single study
        Returns:
            dict: A dictionary of final reviews
        """
        url = f"{self.session.root_url}/rob/api/review/final/?assessment_id={assessment_id}"
        if study_id:
            url += f"&study={study_id}"
        return self.session.get(url).json()

    def compare_metrics(
        self, src_assessment_id: int, dest_assessment_id: int
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Match metrics across two different assessments, returning best-matched results.

        This uses a fuzzy-text matching algorithm to attempt to match text between two different
        assessments.  It returns the best metric-match from the destination, for each metric in the
        source.

        Adds three columns to the source metric dataframe:
        - fuzz_key: the matching metric id form the destination
        - fuzz_score: a similarity score between 0 and 100. 100 is an exact match
        - fuzz_text: the text from the destination metric which was compared

        Args:
            src_assessment_id (int): The source assessment, try to match each metric
            dest_assessment_id (int): The target assessment, where matches are returned from

        Returns:
            tuple[pd.DataFrame, pd.DataFrame]: Metrics with matches in source, Metrics in destination
        """
        src = self.metrics(src_assessment_id).assign(assessment_id=src_assessment_id)
        dest = self.metrics(dest_assessment_id).assign(assessment_id=dest_assessment_id)
        src.loc[:, "_comparison"] = src.short_name + " " + src.name + " " + src.description
        dest.loc[:, "_comparison"] = dest.short_name + " " + dest.name + " " + dest.description
        matched = fuzz_match(src, dest, "_comparison", "_comparison", "id").drop(
            columns=["_comparison"]
        )
        return matched, dest
