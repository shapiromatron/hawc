import pandas as pd
from requests import Response

from .client import BaseClient


class EpiClient(BaseClient):
    """
    Client class for epidemiology requests.
    """

    def metadata(self, assessment_id: int) -> dict:
        """
        Retrieves field choices for all epi models.

        Returns:
            dict: Model metadata
        """
        url = f"{self.session.root_url}/epi/api/metadata/{assessment_id}/"
        return self.session.get(url).json()

    def data(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves epidemiology data for the given assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            pd.DataFrame: Epidemiology data
        """
        url = f"{self.session.root_url}/epi/api/assessment/{assessment_id}/export/"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def endpoints(self, assessment_id: int) -> list[dict]:
        """
        Retrieves all of the epidemiology endpoints for the given assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            list[dict]: Epidemiology endpoints
        """
        payload = {"assessment_id": assessment_id}
        url = f"{self.session.root_url}/epi/api/outcome/"
        generator = self.session.iter_pages(url, payload)
        return [res for results in generator for res in results]

    def get_study_populations(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves all of the study populations for the given assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            pd.DataFrame: study population data
        """
        url = f"{self.session.root_url}/epi/api/study-population/?assessment_id={assessment_id}"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def get_study_population(self, study_population_id: int) -> dict:
        """
        Retrieves data for a single study population

        Args:
            study_population_id (int): Study Population ID

        Returns:
           dict: study population data
        """
        url = f"{self.session.root_url}/epi/api/study-population/{study_population_id}/"
        return self.session.get(url).json()

    def create_study_population(self, data: dict) -> dict:
        """
        Create a new study population.

        Args:
            data (dict): fields to create on the study population. Example keys:
                name (str): name of the study population
                study (int): id of the study to associate with this study population
                countries (list[str]): list of country codes to associate with the study pop
                design (str): Study Design (CO == Cohort, RT == Randomized controlled trial, etc.)
                etc.

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/epi/api/study-population/"
        return self.session.post(url, data).json()

    def update_study_population(self, study_population_id: int, data: dict) -> dict:
        """
        Update an existing study population.

        Args:
            study_population_id (int): Study Population ID

            data: fields to update in the study pop.
                See "create_study_population" docstring for example fields.

        Returns:
            dict: The resulting object, if update was successful
        """

        url = f"{self.session.root_url}/epi/api/study-population/{study_population_id}/"
        return self.session.patch(url, data).json()

    def delete_study_population(self, study_population_id: int) -> Response:
        """
        Delete a study population.

        Args:
            study_population_id (int): Study Population ID

        Returns:
            Response: The response object.
        """
        url = f"{self.session.root_url}/epi/api/study-population/{study_population_id}/"
        return self.session.delete(url)

    def get_criteria(self, criteria_id: int) -> dict:
        """
        Retrieves data for a single criteria

        Args:
            criteria_id (int): criteria ID

        Returns:
            dict: criteria data
        """
        url = f"{self.session.root_url}/epi/api/criteria/{criteria_id}/"
        return self.session.get(url).json()

    def create_criteria(self, data: dict) -> dict:
        """
        Create a new criteria

        Args:
            data (dict): fields to create on the criteria. Keys:
                description (str): description of the criteria
                assessment (int): id of the associated assessment

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/epi/api/criteria/"
        return self.session.post(url, data).json()

    def update_criteria(self, criteria_id: int, data: dict) -> dict:
        """
        Update an existing criteria

        Args:
            criteria_id (int): criteria ID

            data: fields to update in the criteria
                See "create_criteria" docstring for example fields.

        Returns:
            dict: The resulting object, if update was successful
        """

        url = f"{self.session.root_url}/epi/api/criteria/{criteria_id}/"
        return self.session.patch(url, data).json()

    def delete_criteria(self, criteria_id: int) -> Response:
        """
        Delete a criteria

        Args:
            criteria_id (int): criteria ID

        Returns:
            Response: The response object.
        """
        url = f"{self.session.root_url}/epi/api/criteria/{criteria_id}/"
        return self.session.delete(url)

    def get_comparison_set(self, comparison_set_id: int) -> dict:
        """
        Retrieves data for a single comparison set

        Args:
            comparison_set_id (int): comparison set ID

        Returns:
            dict: comparison set data
        """
        url = f"{self.session.root_url}/epi/api/comparison-set/{comparison_set_id}/"
        return self.session.get(url).json()

    def create_comparison_set(self, data: dict) -> dict:
        """
        Create a new comparison set

        Args:
            data (dict): fields to create on the comparison set. Keys:
                name (str): name of the comparison set
                description (str): description
                exposure (int): id of the associated exposure population
                study_population (int): id of the associated study population

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/epi/api/comparison-set/"
        return self.session.post(url, data).json()

    def update_comparison_set(self, comparison_set_id: int, data: dict) -> dict:
        """
        Update an existing comparison set

        Args:
            comparison_set_id (int): comparison set ID

            data: fields to update in the comparison set
                See "create_comparison_set" docstring for example fields.

        Returns:
            dict: The resulting object, if update was successful
        """

        url = f"{self.session.root_url}/epi/api/comparison-set/{comparison_set_id}/"
        return self.session.patch(url, data).json()

    def delete_comparison_set(self, comparison_set_id: int) -> Response:
        """
        Delete a comparison set

        Args:
            comparison_set_id (int): comparison set ID

        Returns:
            Response: The response object.
        """
        url = f"{self.session.root_url}/epi/api/comparison-set/{comparison_set_id}/"
        return self.session.delete(url)

    def get_group(self, group_id: int) -> dict:
        """
        Retrieves data for a single group

        Args:
            group_id (int): group ID

        Returns:
            dict: group data
        """
        url = f"{self.session.root_url}/epi/api/group/{group_id}/"
        return self.session.get(url).json()

    def create_group(self, data: dict) -> dict:
        """
        Create a new group

        Args:
            data (dict): fields to create on the group. Example keys:
                name (str): name of the group
                comparison_set (int): id of the associated comparison set
                ethnicities (list[Any]): list of id's/names of associated ethnicities
                etc.

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/epi/api/group/"
        return self.session.post(url, data).json()

    def update_group(self, group_id: int, data: dict) -> dict:
        """
        Update an existing group

        Args:
            group_id (int): group ID

            data: fields to update in the group
                See "create_group" docstring for example fields.

        Returns:
            dict: The resulting object, if update was successful
        """

        url = f"{self.session.root_url}/epi/api/group/{group_id}/"
        return self.session.patch(url, data).json()

    def delete_group(self, group_id: int) -> Response:
        """
        Delete a group

        Args:
            group_id (int): group ID

        Returns:
            Response: The response object.
        """
        url = f"{self.session.root_url}/epi/api/group/{group_id}/"
        return self.session.delete(url)

    def get_numerical_description(self, numerical_description_id: int) -> dict:
        """
        Retrieves data for a single numerical_description

        Args:
            numerical_description_id (int): numerical_description ID

        Returns:
            dict: numerical_description data
        """
        url = f"{self.session.root_url}/epi/api/numerical-descriptions/{numerical_description_id}/"
        return self.session.get(url).json()

    def create_numerical_description(self, data: dict) -> dict:
        """
        Create a new numerical description

        Args:
            data (dict): fields to create on the numerical description. Example keys:
                description (str): description
                group (int): id of the associated group
                mean (Number): mean value
                mean (Any): median, geometric mean, etc. readable name or underlying id
                etc.

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/epi/api/numerical-descriptions/"
        return self.session.post(url, data).json()

    def update_numerical_description(self, numerical_description_id: int, data: dict) -> dict:
        """
        Update an existing numerical description

        Args:
            numerical_description_id (int): numerical description ID

            data: fields to update in the numerical description
                See "create_numerical_description" docstring for example fields.

        Returns:
            dict: The resulting object, if update was successful
        """

        url = f"{self.session.root_url}/epi/api/numerical-descriptions/{numerical_description_id}/"
        return self.session.patch(url, data).json()

    def delete_numerical_description(self, numerical_description_id: int) -> Response:
        """
        Delete a numerical description

        Args:
            numerical_description_id (int): numerical description ID

        Returns:
            Response: The response object.
        """
        url = f"{self.session.root_url}/epi/api/numerical-descriptions/{numerical_description_id}/"
        return self.session.delete(url)

    def get_outcome(self, outcome_id: int) -> dict:
        """
        Retrieves data for a single outcome

        Args:
            outcome_id (int): outcome ID

        Returns:
            dict: outcome data
        """
        url = f"{self.session.root_url}/epi/api/outcome/{outcome_id}/"
        return self.session.get(url).json()

    def create_outcome(self, data: dict) -> dict:
        """
        Create a new outcome

        Args:
            data (dict): fields to create on the outcome. Example keys:
                name (str): name of the outcome
                assessment (int): id of the associated assessment
                study_population (int): id of the associated study population
                system (str): system
                etc.

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/epi/api/outcome/"
        return self.session.post(url, data).json()

    def update_outcome(self, outcome_id: int, data: dict) -> dict:
        """
        Update an existing outcome

        Args:
            outcome_id (int): outcome ID

            data: fields to update in the outcome
                See "create_outcome" docstring for example fields.

        Returns:
            dict: The resulting object, if update was successful
        """

        url = f"{self.session.root_url}/epi/api/outcome/{outcome_id}/"
        return self.session.patch(url, data).json()

    def delete_outcome(self, outcome_id: int) -> Response:
        """
        Delete an outcome

        Args:
            outcome_id (int): outcome ID

        Returns:
            Response: The response object.
        """
        url = f"{self.session.root_url}/epi/api/outcome/{outcome_id}/"
        return self.session.delete(url)

    def get_result(self, result_id: int) -> dict:
        """
        Retrieves data for a single result

        Args:
            result_id (int): result ID

        Returns:
            dict: result data
        """
        url = f"{self.session.root_url}/epi/api/result/{result_id}/"
        return self.session.get(url).json()

    def create_result(self, data: dict) -> dict:
        """
        Create a new result

        Args:
            data (dict): fields to create on the result. Example keys:
                name (str): name of the result
                comments (str): comments on this result
                outcome (int): id of the associated outcome
                comparison_set (int): id of the associated comparison_set
                factors_applied (list[str]): list of factor names to apply
                etc.

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/epi/api/result/"
        return self.session.post(url, data).json()

    def update_result(self, result_id: int, data: dict) -> dict:
        """
        Update an existing result

        Args:
            result_id (int): result ID

            data: fields to update in the result
                See "create_result" docstring for example fields.

        Returns:
            dict: The resulting object, if update was successful
        """

        url = f"{self.session.root_url}/epi/api/result/{result_id}/"
        return self.session.patch(url, data).json()

    def delete_result(self, result_id: int) -> Response:
        """
        Delete a result

        Args:
            result_id (int): result ID

        Returns:
            Response: The response object.
        """
        url = f"{self.session.root_url}/epi/api/result/{result_id}/"
        return self.session.delete(url)

    def get_group_result(self, group_result_id: int) -> dict:
        """
        Retrieves data for a single group result

        Args:
            group_result_id (int): group result ID

        Returns:
            dict: group result data
        """
        url = f"{self.session.root_url}/epi/api/group-result/{group_result_id}/"
        return self.session.get(url).json()

    def create_group_result(self, data: dict) -> dict:
        """
        Create a new group result

        Args:
            data (dict): fields to create on the group result. Example keys:
                name (str): name of the result
                group (int): id of the associated group
                result (int): id of the associated result
                etc.

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/epi/api/group-result/"
        return self.session.post(url, data).json()

    def update_group_result(self, group_result_id: int, data: dict) -> dict:
        """
        Update an existing group result

        Args:
            group_result_id (int): group result ID

            data: fields to update in the group result
                See "create_group_result" docstring for example fields.

        Returns:
            dict: The resulting object, if update was successful
        """

        url = f"{self.session.root_url}/epi/api/group-result/{group_result_id}/"
        return self.session.patch(url, data).json()

    def delete_group_result(self, group_result_id: int) -> Response:
        """
        Delete a group result

        Args:
            group_result_id (int): group result ID

        Returns:
            Response: The response object.
        """
        url = f"{self.session.root_url}/epi/api/group-result/{group_result_id}/"
        return self.session.delete(url)

    def get_exposure(self, exposure_id: int) -> dict:
        """
        Retrieves data for a single exposure

        Args:
            exposure_id (int): exposure ID

        Returns:
            dict: exposure data
        """
        url = f"{self.session.root_url}/epi/api/exposure/{exposure_id}/"
        return self.session.get(url).json()

    def create_exposure(self, data: dict) -> dict:
        """
        Create a new exposure

        Args:
            data (dict): fields to create on the exposure. Example keys:
                name (str): name of the exposure
                study_population (int): id of the associated study population
                dtxsid (str): e.g. "DTXSID1020190",
                central_tendendices (list[dict]): list of CT's with keys like "estimate", "estimate_type", "lower_ci", etc.
                etc.

        Returns:
            dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/epi/api/exposure/"
        return self.session.post(url, data).json()

    def update_exposure(self, exposure_id: int, data: dict) -> dict:
        """
        Update an existing exposure

        Args:
            exposure_id (int): exposure ID

            data: fields to update in the exposure
                See "create_exposure" docstring for example fields.

        Returns:
            dict: The resulting object, if update was successful
        """

        url = f"{self.session.root_url}/epi/api/exposure/{exposure_id}/"
        return self.session.patch(url, data).json()

    def delete_exposure(self, exposure_id: int) -> Response:
        """
        Delete an exposure

        Args:
            exposure_id (int): exposure ID

        Returns:
            Response: The response object.
        """
        url = f"{self.session.root_url}/epi/api/exposure/{exposure_id}/"
        return self.session.delete(url)
