"""
Utility toolbelt for testing HAWC.
"""

import json
from pathlib import Path

from django.http import HttpResponse
from django.test.client import Client
from rest_framework.response import Response
from rest_framework.test import APIClient

from hawc.apps.assessment.models import Log

DATA_ROOT = Path(__file__).parents[2] / "data/api"


def check_details_of_last_log_entry(obj_id: int, start_of_msg: str):
    """
    retrieve the latest log entry and check that the object_id/message look right.
    """
    log_entry = Log.objects.latest("id")
    assert log_entry.object_id == int(obj_id) and log_entry.message.startswith(start_of_msg)


def check_api_json_data(data: dict, key: str, rewrite_data_files: bool):
    fn = Path(DATA_ROOT / key)
    if rewrite_data_files:
        fn.write_text(json.dumps(data, indent=2, sort_keys=True))
    assert json.loads(fn.read_text()) == data


def get_client(role: str = "", api: bool = False) -> Client | APIClient:
    """Return a client with specified user role

    Args:
        role (str): One of the following: {'', 'pm', 'team', 'rev', 'admin'}. If empty, anonymous.
        api (bool): Returns rest_framework.test.APIClient if True, else django.test.Client

    Returns:
        Client | APIClient
    """
    client = APIClient() if api else Client()
    if role:
        assert client.login(username=f"{role}@hawcproject.org", password="pw") is True
    return client


def check_403(
    client: Client | APIClient, url: str, kw: dict | None = None
) -> HttpResponse | Response:
    """Check that a GET request with the given client returns a 403

    Args:
        client (Client | APIClient): A client object
        url (str): The URL to request
        kw (dict | None, optional): Any additional kwargs to pass to the client.

    Returns:
        A response instance
    """
    if kw is None:
        kw = {}
    if isinstance(client, APIClient):
        kw.setdefault("format", "json")
    response = client.get(url, **kw)
    assert response.status_code == 403
    return response


def check_200(
    client: Client | APIClient, url: str, kw: dict | None = None
) -> HttpResponse | Response:
    """Check that a GET request with the given client returns a 200

    Args:
        client (Client | APIClient): A client object
        url (str): The URL to request
        kw (dict | None, optional): Any additional kwargs to pass to the client.

    Returns:
        A response instance
    """
    if kw is None:
        kw = {}
    if isinstance(client, APIClient):
        kw.setdefault("format", "json")
    response = client.get(url, **kw)
    assert response.status_code == 200
    return response
