import pandas as pd

from .client import BaseClient


class MgmtClient(BaseClient):
    """
    Client class for task management requests
    """

    def tasks(self, assessment_id: int) -> list[dict]:
        """
        Retrieves all tasks for the given assessment

        Args:
            Assessment (int): Assessment Id

        Returns:
            pd.DataFrame: Assessment task information
        """
        url = f"{self.session.root_url}/mgmt/api/assessment/{assessment_id}/export"
        response_json = self.session.post(url, assessment_id).json()
        return pd.DataFrame(response_json)

    def time_spent(self, assessment_id: int):
        """
        Retrieves time spent for the given assessment

        Args:
            Assessment (int): Assessment Id

        Returns:
            pd.DataFrame: Assessment time spent
        """

        url = f"{self.session.root_url}/mgmt/api/assessment/{assessment_id}/time-spent"
        response_json = self.session.post(url, assessment_id).json()
        return pd.DataFrame(response_json)
