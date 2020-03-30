from typing import Dict, Generator, List

import pandas as pd
from requests import Response, Session


class HawcClientException(Exception):
    """An exception occurred in the HAWC client module."""

    pass


class HawcServerException(Exception):
    """An exception occurred on the HAWC server."""

    pass


class _Session:
    """
    A session that handles HAWC requests and responses.

    Allows user authentication and keeps track of root url.
    """

    def __init__(self, root_url: str = "https://hawcproject.org"):
        self.root_url = root_url
        self._session = Session()

    def _handle_hawc_response(self, response: Response) -> Dict:
        """
        Handle standard hawc API response

        Args:
            response (Response): A response object

        Raises:
            HawcClientException: If error occurs in data submission
            HawcServerException: If error orccurs on server

        Returns:
            Dict: The JSON response, if exists
        """
        if response.status_code >= 400 and response.status_code < 500:
            raise HawcClientException(response.status_code, response.json())
        elif response.status_code == 500:
            raise HawcServerException(response)
        else:
            return response.json()

    def _get(self, url: str, params: Dict = None) -> Dict:
        """
        Sends a GET request using the session instance

        Args:
            url (str): URL for request.
            params (Dict, optional): Additional parameters to include. Defaults to None.

        Returns:
            Dict: The JSON response as a dictionary.
        """
        response = self._session.get(url=url, params=params)
        return self._handle_hawc_response(response)

    def _post(self, url: str, data: Dict) -> Dict:
        """
        Sends a POST request using the session instance

        Args:
            url (str): URL for request.
            data (Dict): Payload for the request.

        Returns:
            Dict: The JSON response as a dictionary.
        """
        response = self._session.post(url=url, data=data)
        return self._handle_hawc_response(response)

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
        token = self._handle_hawc_response(response)["token"]
        self._session.headers.update(Authorization=f"Token {token}")

    def _page_gen(self, url: str, params: Dict = None) -> Generator:
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
        response_json = self._get(url, params)
        yield response_json["results"]
        while response_json["next"] is not None:
            response_json = self._get(response_json["next"])
            yield response_json["results"]


class _BaseClient:
    """
    Base client class.

    Initiates with a given _Session object.
    """

    def __init__(self, session: _Session):
        self.session = session


class _LiteratureClient(_BaseClient):
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
        return self.session._post(url, payload)

    def tags(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/tags/"
        response_json = self.session._get(url)
        return pd.DataFrame(response_json)

    def reference_tags(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/reference-tags/"
        response_json = self.session._get(url)
        return pd.DataFrame(response_json)

    def import_reference_tags(
        self, assessment_id: int, csv: str, operation: str = "append"
    ) -> pd.DataFrame:
        payload = {"csv": csv, "operation": operation}
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/reference-tags/"
        response_json = self.session._post(url, payload)
        return pd.DataFrame(response_json)

    def reference_ids(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/reference-ids/"
        response_json = self.session._get(url)
        return pd.DataFrame(response_json)

    def references(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.session.root_url}/lit/api/assessment/{assessment_id}/references-download/"
        response_json = self.session._get(url)
        return pd.DataFrame(response_json)


class _RiskOfBiasClient(_BaseClient):
    """
    Client class for risk of bias requests.
    """

    def data(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.session.root_url}/rob/api/assessment/{assessment_id}/export/"
        response_json = self.session._get(url)
        return pd.DataFrame(response_json)

    def full_data(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.session.root_url}/rob/api/assessment/{assessment_id}/full-export/"
        response_json = self.session._get(url)
        return pd.DataFrame(response_json)


class _EpiClient(_BaseClient):
    """
    Client class for epidemiology requests.
    """

    def data(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.session.root_url}/epi/api/assessment/{assessment_id}/export/"
        response_json = self.session._get(url)
        return pd.DataFrame(response_json)

    def endpoints(self, assessment_id: int) -> List[Dict]:
        payload = {"assessment_id": assessment_id}
        url = f"{self.session.root_url}/epi/api/outcome/"
        generator = self.session._page_gen(url, payload)
        return [res for results in generator for res in results]


class _AnimalClient(_BaseClient):
    """
    Client class for animal experiment requests.
    """

    def data(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.session.root_url}/ani/api/assessment/{assessment_id}/full-export/"
        response_json = self.session._get(url)
        return pd.DataFrame(response_json)

    def data_summary(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.session.root_url}/ani/api/assessment/{assessment_id}/endpoint-export/"
        response_json = self.session._get(url)
        return pd.DataFrame(response_json)

    def endpoints(self, assessment_id: int) -> List[Dict]:
        payload = {"assessment_id": assessment_id}
        url = f"{self.session.root_url}/ani/api/endpoint/"
        generator = self.session._page_gen(url, payload)
        return [res for results in generator for res in results]


class _EpiMetaClient(_BaseClient):
    """
    Client class for epidemiology metadata requests.
    """

    def data(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.session.root_url}/epi-meta/api/assessment/{assessment_id}/export/"
        response_json = self.session._get(url)
        return pd.DataFrame(response_json)


class _InvitroClient(_BaseClient):
    """
    Client class for in-vitro requests.
    """

    def data(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.session.root_url}/in-vitro/api/assessment/{assessment_id}/full-export/"
        response_json = self.session._get(url)
        return pd.DataFrame(response_json)


class _SummaryClient(_BaseClient):
    """
    Client class for summary requests.
    """

    def visual_list(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.session.root_url}/summary/api/visual/?assessment_id={assessment_id}"
        response_json = self.session._get(url)
        return pd.DataFrame(response_json)


class _AssessmentClient(_BaseClient):
    """
    Client class for assessment requests.
    """

    def public(self) -> Dict:
        url = f"{self.session.root_url}/assessment/api/public/"
        return self.session._get(url)


class HawcClient(_BaseClient):
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
        super().__init__(_Session(root_url))

        self.animal = _AnimalClient(self.session)
        self.assessment = _AssessmentClient(self.session)
        self.epi = _EpiClient(self.session)
        self.epimeta = _EpiMetaClient(self.session)
        self.invitro = _InvitroClient(self.session)
        self.lit = _LiteratureClient(self.session)
        self.riskofbias = _RiskOfBiasClient(self.session)
        self.summary = _SummaryClient(self.session)

    def authenticate(self, email: str, password: str):
        """
        Authenticate a user session

        Args:
            email (str): email to authenticate
            password (str): password to authenticate
        """

        self.session.authenticate(email, password)
