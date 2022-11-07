from typing import Dict

from .client import BaseClient


class AssessmentClient(BaseClient):
    """
    Client class for assessment requests.
    """

    def public(self) -> list[Dict]:
        """
        Retrieves data pertaining to all public assessments

        Returns:
            list[Dict]: Public assessment data
        """
        url = f"{self.session.root_url}/assessment/api/assessment/public/"
        return self.session.get(url).json()
