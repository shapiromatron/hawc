import math
from io import StringIO
from typing import Dict, Generator, List

import pandas as pd
from requests import Response, Session
from tqdm import tqdm

__all__ = ["HawcClient"]


class HawcClientException(Exception):
    """An exception occurred in the HAWC client module."""

    pass


class HawcServerException(Exception):
    """An exception occurred on the HAWC server."""

    pass


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
        if response.status_code >= 400 and response.status_code < 500:
            raise HawcClientException(response.status_code, response.json())
        elif response.status_code == 500:
            raise HawcServerException(response)

    def get(self, url: str, params: Dict = None) -> Response:
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

    def post(self, url: str, data: Dict) -> Response:
        """
        Sends a POST request using the session instance

        Args:
            url (str): URL for request.
            data (Dict): Payload for the request.

        Returns:
            Response: The response.
        """
        response = self._session.post(url=url, data=data)
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
            raise StopIteration
        num_pages = math.ceil(response_json["count"] / len(response_json["results"]))
        with tqdm(desc="Iterating pages", initial=1, total=num_pages) as progress_bar:
            while response_json["next"] is not None:
                response_json = self.get(response_json["next"])
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
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/tags/"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def reference_tags(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/reference-tags/"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def import_reference_tags(self, assessment_id: int, csv: str, operation: str = "append") -> pd.DataFrame:
        payload = {"csv": csv, "operation": operation}
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/reference-tags/"
        response_json = self.session.post(url, payload).json()
        return pd.DataFrame(response_json)

    def reference_ids(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/reference-ids/"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def references(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/references-download/"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)


class RiskOfBiasClient(BaseClient):
    """
    Client class for risk of bias requests.
    """

    def data(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.session.root_url}/rob/api/assessment/{assessment_id}/export/"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)

    def full_data(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.session.root_url}/rob/api/assessment/{assessment_id}/full-export/"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)


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
        url = f"{self.session.root_url}/in-vitro/api/assessment/{assessment_id}/full-export/"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)


class SummaryClient(BaseClient):
    """
    Client class for summary requests.
    """

    def visual_list(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.session.root_url}/summary/api/visual/?assessment_id={assessment_id}"
        response_json = self.session.get(url).json()
        return pd.DataFrame(response_json)


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
        Retrieves anonymized bioassay data for all eligible assessments.

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
        client = HawcClient("http://hawc_url.example")
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

    def authenticate(self, email: str, password: str):
        """
        Authenticate a user session

        Args:
            email (str): email to authenticate
            password (str): password to authenticate
        """

        self.session.authenticate(email, password)
