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
                - sort_order (str): how results are sorted

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
                - sort_order (str): how results are sorted

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

    def get_visual(self, visual_id: int):
        """Get a visual.

        Args:
            visual_id (int): ID of the visual to read

        Returns:
            dict: The result object, if get was successful
        """
        url = f"{self.session.root_url}/summary/api/visual/{visual_id}/"
        return self.session.get(url)

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

    def create_datapivot(self, data: dict) -> dict:
        """Create a new data pivot (query)

        Args:
            data (dict): Required metadata for object creation.
                - title (str): Visual title
                - slug (str): Visual identifier/URL base
                - evidence_type (int): Constant representing type of evidence used in data pivot
                     (see hawc.apps.study.constants.StudyType)
                - export_style (int): Constant representing how the level at which data are aggregated,
                     and therefore which columns and types of data are presented in the export, for use
                     in the visual (see hawc.apps.summary.constants.ExportStyle)
                - preferred_units: List of preferred dose-values IDs, in order of preference.
                     If empty, dose-units will be random for each endpoint
                     presented. This setting may used for comparing
                     percent-response, where dose-units are not needed, or for
                     creating one plot similar, but not identical, dose-units.
                - published (bool): datapivot is published for public view
                - settings (str): JSON of object settings
                - assessment (int): assessment ID
                - prefilters (str): JSON of object prefilters
                - caption (str): Data pivot caption

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/summary/api/data_pivot_query/"
        return self.session.post(url, data=data).json()

    def update_datapivot(self, datapivot_id: int, data: dict) -> dict:
        """Update an existing data pivot (query)

        Args:
            id (int): Data pivot identifier
            data (dict): Required metadata for object creation.
                - title (str): Visual title
                - slug (str): Visual identifier/URL base
                - evidence_type (int): Constant representing type of evidence used in data pivot
                     (see hawc.apps.study.constants.StudyType)
                - export_style (int): Constant representing how the level at which data are aggregated,
                     and therefore which columns and types of data are presented in the export, for use
                     in the visual (see hawc.apps.summary.constants.ExportStyle)
                - preferred_units: List of preferred dose-values IDs, in order of preference.
                     If empty, dose-units will be random for each endpoint
                     presented. This setting may used for comparing
                     percent-response, where dose-units are not needed, or for
                     creating one plot similar, but not identical, dose-units.
                - published (bool): datapivot is published for public view
                - settings (str): JSON of object settings
                - assessment (int): assessment ID
                - prefilters (str): JSON of object prefilters
                - caption (str): Data pivot caption

        Returns:
            dict: The resulting object, if update was successful
        """
        url = f"{self.session.root_url}/summary/api/data_pivot_query/{datapivot_id}/"
        return self.session.patch(url, data=data).json()

    def get_datapivot(self, datapivot_id: int):
        """Get a data pivot (query).

        Args:
            visual_id (int): ID of the visual to read

        Returns:
            dict: object, if successful

        """
        url = f"{self.session.root_url}/summary/api/data_pivot_query/{datapivot_id}/"
        return self.session.get(url)

    def delete_datapivot(self, datapivot_id: int):
        """Delete a data pivot (query).

        Args:
            visual_id (int): ID of the visual to delete

        Returns:
            None: If the operation is successful there is no return value.
            If the operation is unsuccessful, an error will be raised.
        """
        url = f"{self.session.root_url}/summary/api/data_pivot_query/{datapivot_id}/"
        self.session.delete(url)

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
