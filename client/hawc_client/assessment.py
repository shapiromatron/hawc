from typing import Dict, List

from .client import BaseClient


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
