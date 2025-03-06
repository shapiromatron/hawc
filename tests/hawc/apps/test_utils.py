"""
Utility toolbelt for testing HAWC.
"""

import json
from io import BytesIO
from pathlib import Path
from typing import TypeVar

import pandas as pd
from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.handlers.wsgi import WSGIRequest
from django.db import models
from django.http import HttpResponse
from django.test import RequestFactory
from django.test.client import Client
from rest_framework.response import Response
from rest_framework.test import APIClient

from hawc.apps.assessment.models import Log, TimeSpentEditing
from hawc.apps.myuser.models import HAWCUser

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


def get_client(role: str = "", api: bool = False, htmx: bool = False) -> Client | APIClient:
    """Return a client with specified user role

    Args:
        role (str): One of the following: {'', 'pm', 'team', 'reviewer', 'admin'}. If empty, anonymous.
        api (bool): Returns rest_framework.test.APIClient if True, else django.test.Client
        htmx (bool): Returns proper headers for HTMX requests

    Returns:
        Client | APIClient
    """
    kw = {}
    if htmx:
        kw["headers"] = {"hx-request": "true"}
    client = APIClient() if api else Client(**kw)
    if role:
        assert client.login(username=f"{role}@hawcproject.org", password="pw") is True
    return client


def get_user(role: str = "") -> AnonymousUser | HAWCUser:
    """Return a user with specified user role

    Args:
        role (str): One of the following: {'', 'pm', 'team', 'reviewer', 'admin'}. If empty, anonymous.
    """

    if not role:
        return AnonymousUser()
    return HAWCUser.objects.get(email=f"{role}@hawcproject.org")


def mock_request(verb: str = "get", role: str = "", path: str = "/") -> WSGIRequest:
    factory = RequestFactory()
    request = getattr(factory, verb)(path)
    request.user = get_user(role)
    return request


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


def check_404(
    client: Client | APIClient, url: str, kw: dict | None = None
) -> HttpResponse | Response:
    """Check that a GET request with the given client returns a 404

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
    assert response.status_code == 404
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


def check_302(client: Client, url: str, redirect_url: str, **kw) -> HttpResponse:
    """Check that visiting this URL returns a 302 redirect to the specified redirect url."""
    response = client.get(url, **kw)
    assert response.status_code == 302
    assert response.url.startswith(redirect_url)
    return response


def df_to_form_data(key: str, df: pd.DataFrame) -> dict:
    f = BytesIO()
    df.to_excel(f, index=False)
    return {key: SimpleUploadedFile("test.xlsx", f.getvalue())}


ModelType = TypeVar("ModelType", bound=models.Model)


def get_first(model_class: type[ModelType]) -> ModelType:
    """Return first instance of  model class"""
    first_obj = model_class.objects.all().first()
    if first_obj is None:
        raise ValueError(f"get_first failed; no instances of '{model_class}' found")
    return first_obj


def get_timespent() -> TimeSpentEditing:
    """Get latest timespent"""
    return TimeSpentEditing.objects.all().order_by("-id")[0]


def check_timespent(obj: models.Model) -> TimeSpentEditing:
    """Check latest timespent object is the same content object; return timespent object"""
    timespent = get_timespent()
    assert isinstance(timespent.content_object, type(obj))
    assert timespent.content_object.pk == obj.pk
    return timespent
