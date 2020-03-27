from typing import Dict, List

import pandas as pd
from requests import Response, Session


class HawcClientException(Exception):
    """An exception occurred in the HAWC client module."""

    pass


class HawcServerException(Exception):
    """An exception occurred on the HAWC server."""

    pass


class Client:
    def __init__(self, root_url: str = "https://hawcproject.org"):
        self.root_url = root_url
        self.session = Session()

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

    def authenticate(self, email: str, password: str) -> Session:
        """
        Authenticate a user session

        Args:
            email (str): email to authenticate
            password (str): password to authenticate
        """

        url = f"{self.root_url}/user/api/token-auth/"
        data = {"username": email, "password": password}
        response = self.session.post(url, json=data)
        token = self._handle_hawc_response(response)["token"]
        self.session.headers.update(Authorization=f"Token {token}")

    def _get(self, url: str) -> Dict:
        response = self.session.get(url)
        return self._handle_hawc_response(response)

    def _post(self, url: str, payload: Dict) -> Dict:
        response = self.session.post(url, payload)
        return self._handle_hawc_response(response)

    def lit_import_hero(self, assessment_id: int, title: str, description: str, ids: List[int]) -> Dict:
        payload = {
            "assessment": assessment_id,
            "search_type": "i",
            "source": 2,
            "title": title,
            "description": description,
            "search_string": ",".join(str(id_) for id_ in ids),
        }
        url = f"{self.root_url}/lit/api/search/"
        return self._post(url, payload)

    def lit_tags(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.root_url}/lit/api/assessment/{assessment_id}/tags/"
        response_json = self._get(url)
        return pd.DataFrame(response_json)

    def lit_reference_tags(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.root_url}/lit/api/assessment/{assessment_id}/reference-tags/"
        response_json = self._get(url)
        return pd.DataFrame(response_json)

    def lit_import_reference_tags(self, assessment_id: int, csv: str, operation: str = "append") -> pd.DataFrame:
        payload = {"csv": csv, "operation": operation}
        url = f"{self.root_url}/lit/api/assessment/{assessment_id}/reference-tags/"
        response_json = self._post(url, payload)
        return pd.DataFrame(response_json)

    def lit_reference_ids(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.root_url}/lit/api/assessment/{assessment_id}/reference-ids/"
        response_json = self._get(url)
        return pd.DataFrame(response_json)

    def lit_references(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.root_url}/lit/api/assessment/{assessment_id}/references-download/"
        response_json = self._get(url)
        return pd.DataFrame(response_json)

    def rob_data(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.root_url}/rob/api/assessment/{assessment_id}/export/"
        response_json = self._get(url)
        return pd.DataFrame(response_json)

    def rob_full_data(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.root_url}/rob/api/assessment/{assessment_id}/full-export/"
        response_json = self._get(url)
        return pd.DataFrame(response_json)

    def ani_data(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.root_url}/ani/api/assessment/{assessment_id}/full-export/"
        response_json = self._get(url)
        return pd.DataFrame(response_json)

    def ani_data_summary(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.root_url}/ani/api/assessment/{assessment_id}/endpoint-export/"
        response_json = self._get(url)
        return pd.DataFrame(response_json)

    def epi_data(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.root_url}/epi/api/assessment/{assessment_id}/export/"
        response_json = self._get(url)
        return pd.DataFrame(response_json)

    def epimeta_data(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.root_url}/epi-meta/api/assessment/{assessment_id}/export/"
        response_json = self._get(url)
        return pd.DataFrame(response_json)

    def invitro_data(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.root_url}/in-vitro/api/assessment/{assessment_id}/full-export/"
        response_json = self._get(url)
        return pd.DataFrame(response_json)

    def visual_list(self, assessment_id: int) -> pd.DataFrame:
        url = f"{self.root_url}/summary/api/visual/?assessment_id={assessment_id}"
        response_json = self._get(url)
        return pd.DataFrame(response_json)

    def public_assessments(self) -> Dict:
        url = f"{self.root_url}/assessment/api/public/"
        return self._get(url)
