import json
import math
from io import StringIO
from typing import Any, Dict, Generator, List, Optional

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
        self, assessment_id: int, csv: str, operation: str = "append"
    ) -> pd.DataFrame:
        """
        Imports a CSV of reference IDs with corresponding tag IDs to the given assessment.

        Args:
            assessment_id (int): Assessment ID
            csv (str): Reference IDs to tag ID mapping. The header of this CSV string should be "reference_id,tag_id".
            operation (str, optional): Either add new references tags to existing (`append`), or replace current tag mappings (`replace`). Defaults to "append".

        Returns:
            pd.DataFrame: All tag mappings for the selected `assessment_id`, after the requested changes
        """
        payload = {"csv": csv, "operation": operation}
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
                                    + hawc.apps.riskofbias.models.RiskOfBiasAssessment.get_rob_response_values
                                    + hawc.apps.riskofbias.models.RiskOfBiasScore.RISK_OF_BIAS_SCORE_CHOICES
                                    + hawc.apps.riskofbias.models.RiskOfBiasScore.SCORE_SYMBOLS
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


class EpiClient(BaseClient):
    """
    Client class for epidemiology requests.
    """

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

    def create(
        self,
        reference_id: int,
        short_citation: str,
        full_citation: str,
        data: Optional[Dict] = None,
    ) -> Dict:
        """
        Creates a study using a given reference ID.

        Args:
            reference_id (int): Reference ID to create study from.
            short_citation (str): Short study citation, can be used as identifier.
            full_citation (str): Complete study citation.
            data (Dict, optional): Dict containing any additional field/value pairings for the study.
                Possible pairings are:
                    bioassay: bool (study contains animal bioassay data)
                    epi: bool (study contains epidemiology data)
                    epi_meta: bool (study contains epidemiology meta-analysis data)
                    in_vitro: bool (study contains in-vitro data)
                    coi_reported: int (COI reported, see
                        hawc.apps.study.models.Study.COI_REPORTED_CHOICES for choices )
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
        data["short_citation"] = short_citation
        data["full_citation"] = full_citation

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

    def authenticate(self, email: str, password: str):
        """
        Authenticate a user session

        Args:
            email (str): email to authenticate
            password (str): password to authenticate
        """

        self.session.authenticate(email, password)
