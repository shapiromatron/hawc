from .client import BaseClient


class AssessmentClient(BaseClient):
    """
    Client class for assessment requests.
    """

    def public(self) -> list[dict]:
        """
        Retrieves data pertaining to all public assessments

        Returns:
            list[dict]: Public assessment data
        """
        url = f"{self.session.root_url}/assessment/api/assessment/public/"
        return self.session.get(url).json()

    def create_value(self, data: dict) -> dict:
        """
        Create an assessment value.

        Args:
            data (dict): required metadata for creation

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/assessment/api/value/"
        return self.session.post(url, data).json()

    def create_detail(self, data: dict) -> dict:
        """
        Create additional details for an assessment.

        Args:
            data (dict): required metadata for creation

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/assessment/api/detail/"
        return self.session.post(url, data).json()

    def all_values(self) -> list[dict]:
        """
        Get a list of all assessment values in HAWC (admin only).

        Returns:
            list[dict]: Assessment values data
        """
        url = f"{self.session.root_url}/admin/api/reports/values/"
        return self.session.get(url).json()
