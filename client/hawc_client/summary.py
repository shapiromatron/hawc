import pandas as pd

from .client import BaseClient


class SummaryClient(BaseClient):
    """
    Client class for summary requests.
    """

    def create_visual(self, data: dict) -> dict:
        """Create a new visual

        Args:
            data (dict): Required metadata for object creation.
                - title (str): Visual title
                - slug (str): Visual identifier/URL base
                - visual_type (int): Constant representing visual type
                - evidence_type (int): Constant representing evidence type
                - published (bool): visual is published for public view
                - settings (dict): object settings (must be valid JSON)
                - assessment (int): assessment ID
                - prefilters (dict): object prefilters (must be valid JSON)
                - caption (str): Visual caption

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/summary/api/visual/"
        return self.session.post(url, data=data).json()

    def update_visual(self, visual_id: int, data: dict) -> dict:
        """Create a new visual

        Args:
            id (int): Visual identifier
            data (dict): Metadata to update
                - title (str): Visual title
                - slug (str): Visual identifier/URL base
                - visual_type (int): Constant representing visual type
                - evidence_type (int): Constant representing evidence type
                - published (bool): visual is published for public view
                - settings (dict): object settings (must be valid JSON)
                - assessment (int): assessment ID
                - prefilters (dict): object prefilters (must be valid JSON)
                - caption (str): Visual caption

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/summary/api/visual/{visual_id}/"
        return self.session.patch(url, data=data).json()

    def delete_visual(self, visual_id: int):
        """Delete a visual.

        Args:
            visual_id (int): ID of the visual to delete

        Returns:
            None: If the operation is successful there is no return value.
            If the operation is unsuccessful, an error will be raised.
        """
        url = f"{self.session.root_url}/summary/api/visual/{visual_id}/"
        self.session.delete(url)

    def get_visual(self, visual_id: int) -> dict:
        """Get a visual.

        Args:
            visual_id (int): ID of the visual to read

        Returns:
            Response: A response object, which contains the visual if successful.
        """
        url = f"{self.session.root_url}/summary/api/visual/{visual_id}/"
        return self.session.get(url).json()

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
