from copy import deepcopy
from operator import itemgetter

import pandas as pd

from .client import BaseClient


class AnimalClient(BaseClient):
    """
    Client class for animal experiment requests.
    """

    def create_experiment(self, data: dict) -> dict:
        """
        Create a new experiment.

        Args:
            data (dict): required metadata for creation

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/ani/api/experiment/"
        return self.session.post(url, data).json()

    def create_animal_group(self, data: dict) -> dict:
        """
        Create a new animal-group and dosing regime.

        Args:
            data (dict): required metadata for creation

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/ani/api/animal-group/"
        return self.session.post(url, data).json()

    def create_endpoint(self, data: dict) -> dict:
        """
        Create a new endpoint.

        Args:
            data (dict): required metadata for creation

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/ani/api/endpoint/"
        return self.session.post(url, data).json()

    def data(self, assessment_id: int, include_unpublished: bool = False) -> pd.DataFrame:
        """
        Retrieves a complete export of animal bioassay data for a given assessment.

        Args:
            assessment_id (int): Assessment ID
            include_unpublished (bool, optional): If True, includes data from unpublished studies. Defaults to False.

        Returns:
            pd.DataFrame: Complete bioassay export
        """
        url = f"{self.session.root_url}/ani/api/assessment/{assessment_id}/full-export/"
        if include_unpublished:
            url += "?unpublished=true"
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

    def _invert_endpoints(self, endpoints: list[dict]) -> list[dict]:
        studies = {}
        for endpoint in deepcopy(endpoints):
            study = endpoint["animal_group"]["experiment"]["study"]
            if study["id"] not in studies:
                study["experiments"] = {}
                studies[study["id"]] = study
            matched_study = studies[study["id"]]

            experiment = endpoint["animal_group"]["experiment"]
            if experiment["id"] not in matched_study["experiments"]:
                experiment["animal_groups"] = {}
                matched_study["experiments"][experiment["id"]] = experiment
            matched_experiment = matched_study["experiments"][experiment["id"]]

            animal_group = endpoint["animal_group"]
            if animal_group["id"] not in matched_experiment["animal_groups"]:
                animal_group["endpoints"] = []
                matched_experiment["animal_groups"][animal_group["id"]] = animal_group
            matched_animal_group = matched_experiment["animal_groups"][animal_group["id"]]

            matched_animal_group["endpoints"].append(endpoint)

        # cleanup
        studies = sorted(list(studies.values()), key=itemgetter("id"))
        for study in studies:
            study["experiments"] = sorted(list(study["experiments"].values()), key=itemgetter("id"))
            for experiment in study["experiments"]:
                experiment.pop("study")
                experiment["animal_groups"] = sorted(
                    list(experiment["animal_groups"].values()), key=itemgetter("id")
                )
                for animal_group in experiment["animal_groups"]:
                    animal_group.pop("experiment")
                    for endpoint in animal_group["endpoints"]:
                        endpoint.pop("animal_group")
                    animal_group["endpoints"] = sorted(
                        animal_group["endpoints"], key=itemgetter("id")
                    )

        return studies

    def endpoints(self, assessment_id: int, invert: bool = False) -> list[dict]:
        """
        Retrieves all bioassay endpoints for a given assessment.

        Args:
            assessment_id (int): Assessment ID
            invert (bool, default False): Return a list of endpoints if False (default). This is
                akin to data bottom up. If True, returns a list of studies instead, with related
                data all the way down to endpoints nested within the list of studies. This is
                akin to top-down.

        Returns:
            list[dict]: A list of endpoints and related studies with each (or a list of studies with
                a related endpoints if inverted)
        """
        payload = {"assessment_id": assessment_id}
        url = f"{self.session.root_url}/ani/api/endpoint/"
        generator = self.session.iter_pages(url, payload)
        data = [res for results in generator for res in results]
        if invert:
            data = self._invert_endpoints(data)
        return data

    def bmds_endpoints(self, assessment_id: int, unpublished: bool = False) -> pd.DataFrame:
        url = f"{self.session.root_url}/ani/api/assessment/{assessment_id}/bmds-export/"
        params = {"unpublished": unpublished}
        response_json = self.session.get(url, params=params).json()
        return pd.DataFrame(response_json)

    def metadata(self) -> dict:
        """
        Retrieves field choices for all animal models.

        Returns:
            dict: Model metadata
        """
        url = f"{self.session.root_url}/ani/api/metadata/"
        return self.session.get(url).json()
