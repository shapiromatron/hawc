import pandas as pd

from .client import BaseClient


class EpiMetaClient(BaseClient):
    """
    Client class for epidemiology metadata requests.
    """

    def data(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves epidemiology metadata for the given assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            pd.DataFrame: Epidemiology metadata
        """
        url = f"{self.session.root_url}/epi-meta/api/assessment/{assessment_id}/export/"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)
