import requests
from django.conf import settings


def get_session(headers: dict | None = None):
    overrides = headers if headers is not None else {}
    headers = {
        "User-Agent": settings.USER_AGENT,
        "Content-Type": "application/json",
    } | overrides
    session = requests.Session()
    session.headers.update(headers)
    return session
