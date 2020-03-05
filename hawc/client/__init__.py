from typing import Dict, Optional, List

from requests import Session, Response


class HawcClientException(Exception):
    """An exception occurred in the HAWC client module."""

    pass


class HawcServerException(Exception):
    """An exception occurred on the HAWC server."""

    pass


class Client:
    def __init__(self, email: str, password: str, root_url: str = "https://hawcproject.org"):
        self.root_url = root_url
        self.session = self.authenticate(email, password)

    def _handle_hawc_response(self, response: Response) -> Optional[Dict]:
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

        Returns:
            Session: a requests.Session object
        """
        session = Session()

        url = f"{self.root_url}/user/api/token-auth/"
        data = {"username": email, "password": password}
        response = session.post(url, json=data)
        token = self._handle_hawc_response(response)["token"]
        session.headers.update(Authorization=f"Token {token}")
        return session

    def lit_import_hero(
        self, assessment_id: int, title: str, description: str, ids: List[int]
    ) -> Dict:
        payload = {
            "assessment": assessment_id,
            "search_type": "i",
            "source": 2,
            "title": title,
            "description": description,
            "search_string": ",".join(str(id_) for id_ in ids),
        }
        url = f"{self.root_url}/lit/api/search/"
        response = self.session.post(url, payload)
        return self._handle_hawc_response(response)
