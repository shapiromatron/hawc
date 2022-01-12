from typing import Dict, List

import pandas as pd

from .client import BaseClient


class AnimalClient(BaseClient):
    """
    Client class for animal experiment requests.
    """

    def create_experiment(self, data: Dict) -> Dict:
        """
        Create a new experiment.

        Args:
            data (Dict): required metadata for creation

        Returns:
            Dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/ani/api/experiment/"
        return self.session.post(url, data).json()

    def create_animal_group(self, data: Dict) -> Dict:
        """
        Create a new animal-group and dosing regime.

        Args:
            data (Dict): required metadata for creation

        Returns:
            Dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/ani/api/animal-group/"
        return self.session.post(url, data).json()

    def create_endpoint(self, data: Dict) -> Dict:
        """
        Create a new endpoint.

        Args:
            data (Dict): required metadata for creation

        Returns:
            Dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/ani/api/endpoint/"
        return self.session.post(url, data).json()

    def data(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves a complete export of animal bioassay data for a given assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            pd.DataFrame: Complete bioassay export
        """
        url = f"{self.session.root_url}/ani/api/assessment/{assessment_id}/full-export/"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def data_summary(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves an endpoint summary of animal bioassay data for a given assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            pd.DataFrame: Endpoint bioassay summary
        """
        url = f"{self.session.root_url}/ani/api/assessment/{assessment_id}/endpoint-export/"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def endpoints(self, assessment_id: int) -> List[Dict]:
        """
        Retrieves all bioassay endpoints for a given assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            List[Dict]: Endpoints
        """
        payload = {"assessment_id": assessment_id}
        url = f"{self.session.root_url}/ani/api/endpoint/"
        generator = self.session.iter_pages(url, payload)
        return [res for results in generator for res in results]

    def metadata(self) -> Dict:
        """
        Retrieves field choices for all animal models.

        Returns:
            Dict: Model metadata
        """
        url = f"{self.session.root_url}/ani/api/metadata/"
        return self.session.get(url).json()
