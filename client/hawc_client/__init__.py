import json
import math
from io import StringIO
from typing import Any, Dict, Generator, List, Optional, Tuple

import pandas as pd
from requests import Response, Session
from tqdm import tqdm

__all__ = ["HawcClient"]
__version__ = "2020.10"


class HawcException(Exception):
    def __init__(self, status_code: int, message: Any):
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return f"<{self.status_code}> {self.message}"


class HawcClientException(HawcException):
    """An exception occurred in the HAWC client module."""


class HawcServerException(HawcException):
    """An exception occurred on the HAWC server."""


class HawcSession:
    """
    A session that handles HAWC requests and responses.

    Allows user authentication and keeps track of root url.
    """

    def __init__(self, root_url: str = "https://hawcproject.org"):
        self.root_url = root_url
        self._session = Session()

    def _handle_hawc_response(self, response: Response) -> None:
        """
        Handle standard hawc API response

        Args:
            response (Response): A response object

        Raises:
            HawcClientException: If error occurs in data submission
            HawcServerException: If error orccurs on server
        """
        try:
            content = response.json()
        except json.JSONDecodeError:
            content = response.text
        if response.status_code >= 400 and response.status_code < 500:
            raise HawcClientException(response.status_code, content)
        elif response.status_code >= 500 and response.status_code < 600:
            raise HawcServerException(response.status_code, "no additional information provided")

    def get(self, url: str, params: Optional[Dict] = None) -> Response:
        """
        Sends a GET request using the session instance

        Args:
            url (str): URL for request.
            params (Dict, optional): Additional parameters to include. Defaults to None.

        Returns:
            Response: The response.
        """
        response = self._session.get(url=url, params=params)
        self._handle_hawc_response(response)
        return response

    def delete(self, url: str, params: Optional[Dict] = None) -> Response:
        """
        Sends a DELETE request using the session instance

        Args:
            url (str): URL for request.
            params (Dict, optional): Additional parameters to include. Defaults to None.

        Returns:
            Response: The response.
        """
        response = self._session.delete(url=url, params=params)
        self._handle_hawc_response(response)
        return response

    def post(self, url: str, data: Optional[Dict] = None) -> Response:
        """
        Sends a POST request using the session instance

        Args:
            url (str): URL for request.
            data (Dict, optional): Payload for the request.

        Returns:
            Response: The response.
        """
        response = self._session.post(url=url, json=data)
        self._handle_hawc_response(response)
        return response

    def patch(self, url: str, data: Optional[Dict] = None) -> Response:
        """
        Sends a PATCH request using the session instance

        Args:
            url (str): URL for request.
            data (Dict, optional): Payload for the request.

        Returns:
            Response: The response.
        """
        response = self._session.patch(url=url, json=data)
        self._handle_hawc_response(response)
        return response

    def authenticate(self, email: str, password: str):
        """
        Authenticate a user session

        Args:
            email (str): email to authenticate
            password (str): password to authenticate
        """

        url = f"{self.root_url}/user/api/token-auth/"
        data = {"username": email, "password": password}
        response = self._session.post(url, json=data)
        self._handle_hawc_response(response)
        token = response.json()["token"]
        self._session.headers.update(Authorization=f"Token {token}")

    def set_authentication_token(self, token: str):
        """
        Set authentication token (browser session specific)

        Args:
            token (str): authentication token from your user profile
        """
        self._session.headers.update(Authorization=f"Token {token}")

    def iter_pages(self, url: str, params: Dict = None) -> Generator:
        """
        Generator that crawls paginated HAWC responses.

        Args:
            url (str): URL for GET request.
            params (Dict, optional): GET parameters to include. Defaults to None.

        Returns:
            Generator: Generator for paginated response

        Yields:
            Generator: Results for a page of response
        """
        response_json = self.get(url, params).json()
        yield response_json["results"]
        # Prevents divide by zero if there are no results
        if len(response_json["results"]) == 0:
            return
        num_pages = math.ceil(response_json["count"] / len(response_json["results"]))
        with tqdm(desc="Iterating pages", initial=1, total=num_pages) as progress_bar:
            while response_json["next"] is not None:
                response_json = self.get(response_json["next"]).json()
                progress_bar.update(1)
                yield response_json["results"]


class BaseClient:
    """
    Base client class.

    Initiates with a given HawcSession object.
    """

    def __init__(self, session: HawcSession):
        self.session = session

    def _csv_to_df(self, csv: str) -> pd.DataFrame:
        """
        Takes a CSV string and returns the pandas DataFrame representation of it.

        Args:
            csv (str): CSV string

        Returns:
            pd.DataFrame: DataFrame from CSV
        """
        csv_io = StringIO(csv)
        return pd.read_csv(csv_io)


class LiteratureClient(BaseClient):
    """
    Client class for literature requests.
    """

    def import_hero(self, assessment_id: int, title: str, description: str, ids: List[int]) -> Dict:
        """
        Imports a list of HERO IDs as literature references for the given assessment.

        Args:
            assessment_id (int): Assessment ID
            title (str): Title of import
            description (str): Description of import
            ids (List[int]): HERO IDs

        Returns:
            Dict: JSON response
        """
        payload = {
            "assessment": assessment_id,
            "search_type": "i",
            "source": 2,
            "title": title,
            "description": description,
            "search_string": ",".join(str(id_) for id_ in ids),
        }
        url = f"{self.session.root_url}/lit/api/search/"
        return self.session.post(url, payload).json()

    def tags(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves all of the tags for the given assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            pd.DataFrame: Assessment tags
        """
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/tags/"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def get_tagtree(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves the nested tag tree for the given assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            Dict: JSON representation of the tag tree
        """
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/tagtree/"
        response_json = self.session.get(url).json()
        return response_json["tree"]

    def clone_tagtree(self, source_assessment_id: int, target_assessment_id: int) -> pd.DataFrame:
        """
        Copies the tag tree from one assessment to another.

        Args:
            source_assessment_id (int): Assessment ID to copy tag tree from
            target_assessment_id (int): Assessment ID to copy tag tree to

        Returns:
            Dict: JSON representation of the new tag tree
        """
        fetch_url = f"{self.session.root_url}/lit/api/assessment/{source_assessment_id}/tagtree/"
        tree = self.session.get(fetch_url).json()

        update_url = f"{self.session.root_url}/lit/api/assessment/{target_assessment_id}/tagtree/"
        update_response_json = self.session.post(update_url, tree).json()

        return update_response_json["tree"]

    def update_tagtree(self, assessment_id: int, tags: List[Dict]) -> pd.DataFrame:
        """
        Updates the tag tree.

        Args:
            assessment_id (int): Assessment ID to update
            tags (List[Dict]): tag definitions. For each tag Dict element, "name" is required. "slug" is
               optional. "children" is optional and should contain a recursive List containing valid tags.

        Returns:
            Dict: JSON representation of the new tag tree. If errors, a JSON list containing details.
        """
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/tagtree/"
        response_json = self.session.post(url, {"tree": tags}).json()
        return response_json["tree"]

    def reference_tags(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves the literature references and their corresponding tags for a given assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            pd.DataFrame: References with corresponding tags
        """
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/reference-tags/"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def import_reference_tags(
        self, assessment_id: int, csv: str, operation: str = "append", dry_run: bool = False
    ) -> pd.DataFrame:
        """
        Imports a CSV of reference IDs with corresponding tag IDs to the given assessment.

        Args:
            assessment_id (int): Assessment ID
            csv (str): Reference IDs to tag ID mapping. The header of this CSV string should be "reference_id,tag_id".
            operation (str, optional): Either add new references tags to existing (`append`), or replace current tag mappings (`replace`). Defaults to "append".
            dry_run (bool, optional): If set to True, runs validation checks but does not execute

        Returns:
            pd.DataFrame: All tag mappings for the selected `assessment_id`, after the requested changes
        """
        payload = {"csv": csv, "operation": operation, "dry_run": dry_run}
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/reference-tags/"
        response_json = self.session.post(url, payload).json()
        return pd.DataFrame(response_json)

    def reference_ids(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves the reference IDs and corresponding HERO/PubMed/etc IDs for the given assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            pd.DataFrame: Reference IDs and HERO/PubMed/etc IDs
        """
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/reference-ids/"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def references(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves all references for the given assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            pd.DataFrame: References data
        """
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/references-download/"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def reference(self, reference_id: int) -> Dict:
        """
        Retrieves the selected reference.

        Args:
            reference_id (int): ID of the reference to retrieve

        Returns:
            Dict: JSON representation of the reference
        """
        url = f"{self.session.root_url}/lit/api/reference/{reference_id}/"
        response_json = self.session.get(url).json()
        return response_json

    def update_reference(self, reference_id: int, **kwargs) -> Dict:
        """
        Updates reference with given values. Fields not passed as parameters
        are unchanged.

        Args:
            reference_id (int): ID of reference to update
            **kwargs (optional): Named parameters of fields to update in reference. Example parameters:
                title (str): title of the reference
                abstract (str): reference abstract
                tags (List[int]): tag IDs to apply to reference;
                    replaces the existing tags

        Example Usage:
            updated_reference_json = client.lit.update_reference(
                reference_id = 1,
                title = "reference",
                tags = [1,2,3]
            )

        Returns:
            Dict: JSON representation of the updated reference.
        """
        url = f"{self.session.root_url}/lit/api/reference/{reference_id}/"
        response_json = self.session.patch(url, kwargs).json()
        return response_json

    def delete_reference(self, reference_id: int) -> None:
        """
        Deletes the selected reference. This also removes the reference from any
        searches/imports which may have included the reference. If data was
        extracted with this reference and it is associated with bioassay or epi
        extractions they will also be removed.

        Args:
            reference_id (int): ID of reference to delete

        Returns:
            None: If the operation is successful there is no return value.
            If the operation is unsuccessful, an error will be raised.
        """
        url = f"{self.session.root_url}/lit/api/reference/{reference_id}/"
        self.session.delete(url)

    def replace_hero(self, assessment_id: int, replace: List[List[int]]) -> None:
        """
        Replace HERO ID associated with each reference with a new HERO ID. Reference
        fields are updated using the new HERO ID's reference metadata.  This request is
        throttled; can only be executed once per minute.

        This method schedules a task to be executed when workers are available; task completion
        therefore is not guaranteed even with a successful response.

        Args:
            assessment_id (int): Assessment ID for all references in the list.
            replace (List[List[int]]): List of reference ID / new HERO ID pairings, both values
                should be integers, ex., [[reference_id, hero_id], ... ]

        Returns:
            None: If the operation is successful there is no return value.
            If the operation is unsuccessful, an error will be raised.
        """
        body = {"replace": replace}
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/replace-hero/"
        self.session.post(url, body)

    def update_references_from_hero(self, assessment_id: int) -> None:
        """
        Updates the fields of all HERO references in an assessment with the most recent metadata
        from HERO. This request is throttled; can only be executed once per minute.

        This method schedules a task to be executed when workers are available; task completion
        therefore is not guaranteed even with a successful response.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            None: If the operation is successful there is no return value.
            If the operation is unsuccessful, an error will be raised.
        """
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/update-reference-metadata-from-hero/"
        self.session.post(url)


class RiskOfBiasClient(BaseClient):
    """
    Client class for risk of bias requests.
    """

    def data(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves risk of bias data for the given assessment.
        This includes only final reviews.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            pd.DataFrame: Risk of bias data
        """
        url = f"{self.session.root_url}/rob/api/assessment/{assessment_id}/export/"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def full_data(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves full risk of bias data for the given assessment.
        This includes user-level reviews.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            pd.DataFrame: Full risk of bias data
        """
        url = f"{self.session.root_url}/rob/api/assessment/{assessment_id}/full-export/"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def create(
        self, study_id: int, author_id: int, active: bool, final: bool, scores: List[Dict]
    ) -> Dict:
        """
        Create a Risk of Bias review for a study. The review must be complete and contain answers for
        all required metrics.

        Args:
            study_id (int): id of study.
            author_id (int): id of author of the Risk of Bias data.
            active (bool): create the new Risk of Bias data as active or not
            final (bool): create the new Risk of Bias data as final or not
            scores (List[Dict]): List of scores. Each element of the List is a Dict containing the following
                                 string keys / expected values:
                * "metric_id" (int): the id of the metric for this score
                * "is_default" (bool): create this score as default or not
                * "label" (str): label for this score
                * "notes" (str): notes for this core
                * "score" (int): numeric score value. Actual legal values for this are dependent on the value
                                 of the HAWC_FLAVOR setting for this instance of HAWC and correspond to readable
                                 values like "Critically deficient" or "++". See also:
                                    hawc.apps.riskofbias.constants.SCORE_CHOICES
                                    + hawc.apps.riskofbias.constants.SCORE_SYMBOLS
                * bias_direction (int, optional): bias direction
                * "overridden_objects" (List[Dict], optional): a list of overrides for this particular score. Optional.
                                                     Each element of this List is a Dict containing the
                                                     following string keys / expected values:
                    * "content_type_name" (str): the name of the data type relevant to this override.
                    * "object_id" (int): the id of the particular instance of that data type relevant to this override.
        """
        payload = {
            "study_id": study_id,
            "author_id": author_id,
            "active": active,
            "final": final,
            "scores": scores,
        }
        url = f"{self.session.root_url}/rob/api/review/"
        return self.session.post(url, payload).json()

    def bulk_rob_copy(
        self,
        src_assessment_id: int,
        dst_assessment_id: int,
        src_dst_study_ids: List[Tuple[int, int]],
        src_dst_metric_ids: List[Tuple[int, int]],
        copy_mode: int,
        author_mode: int,
        dst_author_id: Optional[int] = None,
    ):
        """
        Copy final scores from a subset of studies from one assessment as the scores in a
        different assessment. Useful when an assessment is cloned or repurposed and existing
        evaluations should be used in a new evaluation.

        Args:
            src_assessment_id (int): source assessment
            dst_assessment_id (int): destination assessment
            src_dst_study_ids (List[Tuple[int, int]]): source study id, destination study id pairings
            src_dst_metric_ids (List[Tuple[int, int]]): source metric id, destination metric id pairings
            copy_mode (int): enum for copy mode
                1 = src active riskofbias -> dest active risk of bias
                2 = src final riskofbias -> dest initial risk of bias
            author_mode (int): enum for author mode
                1: original authors are preserved
                2: authors are overwritten by given dst_author_id
            dst_author_id (Optional[int]): author for destination RoBs when author_mode = 2.

        Returns:
            Dict: Log information and mapping of all source ids to destination ids
        """

        payload = {
            "src_assessment_id": src_assessment_id,
            "dst_assessment_id": dst_assessment_id,
            "src_dst_study_ids": src_dst_study_ids,
            "src_dst_metric_ids": src_dst_metric_ids,
            "copy_mode": copy_mode,
            "author_mode": author_mode,
        }
        if dst_author_id is not None:
            payload["dst_author_id"] = dst_author_id

        url = f"{self.session.root_url}/rob/api/assessment/bulk_rob_copy/"
        return self.session.post(url, payload).json()


class EpiClient(BaseClient):
    """
    Client class for epidemiology requests.
    """

    def metadata(self, assessment_id: int) -> Dict:
        """
        Retrieves field choices for all epi models.

        Returns:
            Dict: Model metadata
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

    def endpoints(self, assessment_id: int) -> List[Dict]:
        """
        Retrieves all of the epidemiology endpoints for the given assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            List[Dict]: Epidemiology endpoints
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

    def get_study_population(self, study_population_id: int) -> Dict:
        """
        Retrieves data for a single study population

        Args:
            study_population_id (int): Study Population ID

        Returns:
           Dict: study population data
        """
        url = f"{self.session.root_url}/epi/api/study-population/{study_population_id}/"
        return self.session.get(url).json()

    def create_study_population(self, data: Dict) -> Dict:
        """
        Create a new study population.

        Args:
            data (Dict): fields to create on the study population. Example keys:
                name (str): name of the study population
                study (int): id of the study to associate with this study population
                countries (List[str]): list of country codes to associate with the study pop
                design (str): Study Design (CO == Cohort, RT == Randomized controlled trial, etc.)
                etc.

        Returns:
            Dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/epi/api/study-population/"
        return self.session.post(url, data).json()

    def update_study_population(self, study_population_id: int, data: Dict) -> Dict:
        """
        Update an existing study population.

        Args:
            study_population_id (int): Study Population ID

            data: fields to update in the study pop.
                See "create_study_population" docstring for example fields.

        Returns:
            Dict: The resulting object, if update was successful
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

    def get_criteria(self, criteria_id: int) -> Dict:
        """
        Retrieves data for a single criteria

        Args:
            criteria_id (int): criteria ID

        Returns:
            Dict: criteria data
        """
        url = f"{self.session.root_url}/epi/api/criteria/{criteria_id}/"
        return self.session.get(url).json()

    def create_criteria(self, data: Dict) -> Dict:
        """
        Create a new criteria

        Args:
            data (Dict): fields to create on the criteria. Keys:
                description (str): description of the criteria
                assessment (int): id of the associated assessment

        Returns:
            Dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/epi/api/criteria/"
        return self.session.post(url, data).json()

    def update_criteria(self, criteria_id: int, data: Dict) -> Dict:
        """
        Update an existing criteria

        Args:
            criteria_id (int): criteria ID

            data: fields to update in the criteria
                See "create_criteria" docstring for example fields.

        Returns:
            Dict: The resulting object, if update was successful
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

    def get_comparison_set(self, comparison_set_id: int) -> Dict:
        """
        Retrieves data for a single comparison set

        Args:
            comparison_set_id (int): comparison set ID

        Returns:
            Dict: comparison set data
        """
        url = f"{self.session.root_url}/epi/api/comparison-set/{comparison_set_id}/"
        return self.session.get(url).json()

    def create_comparison_set(self, data: Dict) -> Dict:
        """
        Create a new comparison set

        Args:
            data (Dict): fields to create on the comparison set. Keys:
                name (str): name of the comparison set
                description (str): description
                exposure (int): id of the associated exposure population
                study_population (int): id of the associated study population

        Returns:
            Dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/epi/api/comparison-set/"
        return self.session.post(url, data).json()

    def update_comparison_set(self, comparison_set_id: int, data: Dict) -> Dict:
        """
        Update an existing comparison set

        Args:
            comparison_set_id (int): comparison set ID

            data: fields to update in the comparison set
                See "create_comparison_set" docstring for example fields.

        Returns:
            Dict: The resulting object, if update was successful
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

    def get_group(self, group_id: int) -> Dict:
        """
        Retrieves data for a single group

        Args:
            group_id (int): group ID

        Returns:
            Dict: group data
        """
        url = f"{self.session.root_url}/epi/api/group/{group_id}/"
        return self.session.get(url).json()

    def create_group(self, data: Dict) -> Dict:
        """
        Create a new group

        Args:
            data (Dict): fields to create on the group. Example keys:
                name (str): name of the group
                comparison_set (int): id of the associated comparison set
                ethnicities (List[Any]): list of id's/names of associated ethnicities
                etc.

        Returns:
            Dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/epi/api/group/"
        return self.session.post(url, data).json()

    def update_group(self, group_id: int, data: Dict) -> Dict:
        """
        Update an existing group

        Args:
            group_id (int): group ID

            data: fields to update in the group
                See "create_group" docstring for example fields.

        Returns:
            Dict: The resulting object, if update was successful
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

    def get_numerical_description(self, numerical_description_id: int) -> Dict:
        """
        Retrieves data for a single numerical_description

        Args:
            numerical_description_id (int): numerical_description ID

        Returns:
            Dict: numerical_description data
        """
        url = f"{self.session.root_url}/epi/api/numerical-descriptions/{numerical_description_id}/"
        return self.session.get(url).json()

    def create_numerical_description(self, data: Dict) -> Dict:
        """
        Create a new numerical description

        Args:
            data (Dict): fields to create on the numerical description. Example keys:
                description (str): description
                group (int): id of the associated group
                mean (Number): mean value
                mean (Any): median, geometric mean, etc. readable name or underlying id
                etc.

        Returns:
            Dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/epi/api/numerical-descriptions/"
        return self.session.post(url, data).json()

    def update_numerical_description(self, numerical_description_id: int, data: Dict) -> Dict:
        """
        Update an existing numerical description

        Args:
            numerical_description_id (int): numerical description ID

            data: fields to update in the numerical description
                See "create_numerical_description" docstring for example fields.

        Returns:
            Dict: The resulting object, if update was successful
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

    def get_outcome(self, outcome_id: int) -> Dict:
        """
        Retrieves data for a single outcome

        Args:
            outcome_id (int): outcome ID

        Returns:
            Dict: outcome data
        """
        url = f"{self.session.root_url}/epi/api/outcome/{outcome_id}/"
        return self.session.get(url).json()

    def create_outcome(self, data: Dict) -> Dict:
        """
        Create a new outcome

        Args:
            data (Dict): fields to create on the outcome. Example keys:
                name (str): name of the outcome
                assessment (int): id of the associated assessment
                study_population (int): id of the associated study population
                system (str): system
                etc.

        Returns:
            Dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/epi/api/outcome/"
        return self.session.post(url, data).json()

    def update_outcome(self, outcome_id: int, data: Dict) -> Dict:
        """
        Update an existing outcome

        Args:
            outcome_id (int): outcome ID

            data: fields to update in the outcome
                See "create_outcome" docstring for example fields.

        Returns:
            Dict: The resulting object, if update was successful
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

    def get_result(self, result_id: int) -> Dict:
        """
        Retrieves data for a single result

        Args:
            result_id (int): result ID

        Returns:
            Dict: result data
        """
        url = f"{self.session.root_url}/epi/api/result/{result_id}/"
        return self.session.get(url).json()

    def create_result(self, data: Dict) -> Dict:
        """
        Create a new result

        Args:
            data (Dict): fields to create on the result. Example keys:
                name (str): name of the result
                comments (str): comments on this result
                outcome (int): id of the associated outcome
                comparison_set (int): id of the associated comparison_set
                factors_applied (List[str]): list of factor names to apply
                etc.

        Returns:
            Dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/epi/api/result/"
        return self.session.post(url, data).json()

    def update_result(self, result_id: int, data: Dict) -> Dict:
        """
        Update an existing result

        Args:
            result_id (int): result ID

            data: fields to update in the result
                See "create_result" docstring for example fields.

        Returns:
            Dict: The resulting object, if update was successful
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

    def get_group_result(self, group_result_id: int) -> Dict:
        """
        Retrieves data for a single group result

        Args:
            group_result_id (int): group result ID

        Returns:
            Dict: group result data
        """
        url = f"{self.session.root_url}/epi/api/group-result/{group_result_id}/"
        return self.session.get(url).json()

    def create_group_result(self, data: Dict) -> Dict:
        """
        Create a new group result

        Args:
            data (Dict): fields to create on the group result. Example keys:
                name (str): name of the result
                group (int): id of the associated group
                result (int): id of the associated result
                etc.

        Returns:
            Dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/epi/api/group-result/"
        return self.session.post(url, data).json()

    def update_group_result(self, group_result_id: int, data: Dict) -> Dict:
        """
        Update an existing group result

        Args:
            group_result_id (int): group result ID

            data: fields to update in the group result
                See "create_group_result" docstring for example fields.

        Returns:
            Dict: The resulting object, if update was successful
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

    def get_exposure(self, exposure_id: int) -> Dict:
        """
        Retrieves data for a single exposure

        Args:
            exposure_id (int): exposure ID

        Returns:
            Dict: exposure data
        """
        url = f"{self.session.root_url}/epi/api/exposure/{exposure_id}/"
        return self.session.get(url).json()

    def create_exposure(self, data: Dict) -> Dict:
        """
        Create a new exposure

        Args:
            data (Dict): fields to create on the exposure. Example keys:
                name (str): name of the exposure
                study_population (int): id of the associated study population
                dtxsid (str): e.g. "DTXSID1020190",
                central_tendendices (List[Dict]): list of CT's with keys like "estimate", "estimate_type", "lower_ci", etc.
                etc.

        Returns:
            Dict: The resulting object, if create was successful
        """
        url = f"{self.session.root_url}/epi/api/exposure/"
        return self.session.post(url, data).json()

    def update_exposure(self, exposure_id: int, data: Dict) -> Dict:
        """
        Update an existing exposure

        Args:
            exposure_id (int): exposure ID

            data: fields to update in the exposure
                See "create_exposure" docstring for example fields.

        Returns:
            Dict: The resulting object, if update was successful
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


class EpiMetaClient(BaseClient):
    """
    Client class for epidemiology metadata requests.
    """

    def data(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves epidemiology metadata for the given assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            pd.DataFrame: Epidemiology metadata
        """
        url = f"{self.session.root_url}/epi-meta/api/assessment/{assessment_id}/export/"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)


class InvitroClient(BaseClient):
    """
    Client class for in-vitro requests.
    """

    def data(self, assessment_id: int) -> pd.DataFrame:
        """
        Retrieves in-vitro data for the given assessment.

        Args:
            assessment_id (int): Assessment ID

        Returns:
            pd.DataFrame: In-vitro data
        """
        url = f"{self.session.root_url}/in-vitro/api/assessment/{assessment_id}/full-export/"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)


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


class StudyClient(BaseClient):
    """
    Client class for study requests.
    """

    def create(self, reference_id: int, data: Optional[Dict] = None) -> Dict:
        """
        Creates a study using a given reference ID.

        Args:
            reference_id (int): Reference ID to create study from.
            data (Dict, optional): Dict containing any additional field/value pairings for the study.
                Possible pairings are:
                    short_citation (str): Short study citation, can be used as identifier.
                    full_citation (str): Complete study citation.
                    bioassay: bool (study contains animal bioassay data)
                    epi: bool (study contains epidemiology data)
                    epi_meta: bool (study contains epidemiology meta-analysis data)
                    in_vitro: bool (study contains in-vitro data)
                    coi_reported: int (COI reported, see
                        hawc.apps.study.constants.CoiReported for choices )
                    coi_details: str (COI details; use the COI declaration when available)
                    funding_source: str (any funding source information)
                    study_identifier: str (reference descriptor for assessment-tracking,
                        for example, "{Author, year, #EndNoteNumber}")
                    contact_author: bool (was the author contacted for clarification/additional data)
                    ask_author: str (correspondence details)
                    published: bool (study, evaluation, and extraction details may be visible to permitted users)
                    summary: str (often left blank, used to add comments on data extration)
                    editable: bool (project-managers/team-members allowed to edit this study)
                Defaults to {empty}.

        Returns:
            Dict: JSON of the created study
        """
        if data is None:
            data = {}
        data["reference_id"] = reference_id

        url = f"{self.session.root_url}/study/api/study/"
        return self.session.post(url, data).json()


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

    def bioassay_ml_dataset(self) -> pd.DataFrame:
        """
        Retrieves anonymized bioassay data and their related study identification for all eligible assessments, designed for training of machine learning algorithms.

        Returns:
            pd.DataFrame: Anonymized bioassay data
        """
        url = f"{self.session.root_url}/assessment/api/assessment/bioassay_ml_dataset/?format=csv"
        response = self.session.get(url)
        return self._csv_to_df(response.text)


class VocabClient(BaseClient):
    """
    Client class for vocabulary requests.
    """

    def bulk_create(self, terms: List[Dict]) -> List[Dict]:
        """
        Bulk creates a list of terms.

        Args:
            terms (List[Dict]): List of serialized terms.

        Returns:
            List[Dict]: List of created, serialized terms.
        """
        url = f"{self.session.root_url}/vocab/api/term/bulk-create/"
        return self.session.post(url, terms).json()

    def bulk_update(self, terms: List[Dict]) -> List[Dict]:
        """
        Bulk updates a list of terms.

        Args:
            terms (List[Dict]): List of serialized terms.

        Returns:
            List[Dict]: List of updated, serialized terms.
        """
        url = f"{self.session.root_url}/vocab/api/term/bulk-update/"
        return self.session.patch(url, terms).json()

    def uids(self) -> List[Tuple[int, int]]:
        """
        Get all term ids and uids.

        Returns:
            List[Tuple[int,int]]: List of id, uid tuples for all terms.
        """
        url = f"{self.session.root_url}/vocab/api/term/uids/"
        return self.session.get(url).json()


class HawcClient(BaseClient):
    """
    HAWC Client.

    Usage:
        client = HawcClient("https://hawcproject.org")
        # If authentication is needed...
        client.authenticate("username","password")
        # To make requests...
        client.<namespace>.<method>()

    Below are the available namespaces:
        animal, epi, epimeta, invitro, lit, riskofbias, summary
    """

    def __init__(self, root_url: str = "https://hawcproject.org"):
        super().__init__(HawcSession(root_url))

        self.animal = AnimalClient(self.session)
        self.assessment = AssessmentClient(self.session)
        self.epi = EpiClient(self.session)
        self.epimeta = EpiMetaClient(self.session)
        self.invitro = InvitroClient(self.session)
        self.lit = LiteratureClient(self.session)
        self.riskofbias = RiskOfBiasClient(self.session)
        self.summary = SummaryClient(self.session)
        self.study = StudyClient(self.session)
        self.vocab = VocabClient(self.session)

    def authenticate(self, email: str, password: str):
        """
        Authenticate a user session

        Args:
            email (str): email to authenticate
            password (str): password to authenticate
        """

        self.session.authenticate(email, password)
