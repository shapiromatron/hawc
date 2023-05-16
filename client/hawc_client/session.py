import json
import math
from collections.abc import Generator

from requests import Response, Session
from tqdm import tqdm

from .exceptions import HawcClientException, HawcServerException


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

    def get(self, url: str, params: dict | None = None) -> Response:
        """
        Sends a GET request using the session instance

        Args:
            url (str): URL for request.
            params (dict, optional): Additional parameters to include. Defaults to None.

        Returns:
            Response: The response.
        """
        response = self._session.get(url=url, params=params)
        self._handle_hawc_response(response)
        return response

    def delete(self, url: str, params: dict | None = None) -> Response:
        """
        Sends a DELETE request using the session instance

        Args:
            url (str): URL for request.
            params (dict, optional): Additional parameters to include. Defaults to None.

        Returns:
            Response: The response.
        """
        response = self._session.delete(url=url, params=params)
        self._handle_hawc_response(response)
        return response

    def post(self, url: str, data: dict | None = None) -> Response:
        """
        Sends a POST request using the session instance

        Args:
            url (str): URL for request.
            data (dict, optional): Payload for the request.

        Returns:
            Response: The response.
        """
        response = self._session.post(url=url, json=data)
        self._handle_hawc_response(response)
        return response

    def patch(self, url: str, data: dict | None = None) -> Response:
        """
        Sends a PATCH request using the session instance

        Args:
            url (str): URL for request.
            data (dict, optional): Payload for the request.

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

    def set_authentication_token(self, token: str, login: bool = False) -> bool:
        """
        Set authentication token for hawc client session.

        Args:
            token (str): authentication token from your user profile
            login (bool, default False): if True, creates a django cookie-based session for HAWC
                similar to a standard web-browser. If False (default), creates a token-
                based django session for using the API. Requests using cookie-based sessions
                require CSRF tokens, so form functionality will be limited.

        Returns
            bool: Returns true if session is valid
        """
        params = {}
        if login:
            params["login"] = 1
        self._session.headers.update(Authorization=f"Token {token}")
        url = f"{self.root_url}/user/api/validate-token/"
        response = self.get(url, params).json()
        if login:
            self._session.headers.pop("Authorization")
        return response["valid"]

    def iter_pages(self, url: str, params: dict | None = None) -> Generator:
        """
        Generator that crawls paginated HAWC responses.

        Args:
            url (str): URL for GET request.
            params (dict, optional): GET parameters to include. Defaults to None.

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
