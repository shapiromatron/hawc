from typing import Dict, List

import pandas as pd

from .base_client import BaseClient


class AssessmentClient(BaseClient):
    """
    Client class for assessment requests.
    """

    def public(self) -> List[Dict]:
        """
        Retrieves data pertaining to all public assessments

        Returns:
            List[Dict]: Public assessment data
        """
        url = f"{self.session.root_url}/assessment/api/assessment/public/"
        return self.session.get(url).json()

    def bioassay_ml_dataset(self) -> pd.DataFrame:
        """
        Retrieves anonymized bioassay data and their related study identification for all eligible assessments, designed for training of machine learning algorithms.

        Returns:
            pd.DataFrame: Anonymized bioassay data
        """
        url = f"{self.session.root_url}/assessment/api/assessment/bioassay_ml_dataset/?format=csv"
        response = self.session.get(url)
        return self._csv_to_df(response.text)
