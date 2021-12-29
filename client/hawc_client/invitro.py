import pandas as pd

from .client import BaseClient


class InvitroClient(BaseClient):
    """
    Client class for in-vitro requests.
    """

    def data(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves in-vitro data for the given assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            pd.DataFrame: In-vitro data
        """
        url = f"{self.session.root_url}/in-vitro/api/assessment/{assessment_id}/full-export/"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)
