import pandas as pd

from .client import BaseClient


class SummaryClient(BaseClient):
    """
    Client class for summary requests.
    """

    def visual_list(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves a visual list for the given assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            pd.DataFrame: Visual list
        """
        url = f"{self.session.root_url}/summary/api/visual/?assessment_id={assessment_id}"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def datapivot_list(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves a data pivot list for the given assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            pd.DataFrame: Data Pivot list
        """
        url = f"{self.session.root_url}/summary/api/data_pivot/?assessment_id={assessment_id}"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def table_list(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves a table list for the given assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            pd.DataFrame: Data Pivot list
        """
        url = f"{self.session.root_url}/summary/api/summary-table/?assessment_id={assessment_id}"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)
