import requests
from django.conf import settings


def get_session(headers: dict | None = None):
    _headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": settings.USER_AGENT,
    }
    _headers.update(headers or {})
    session = requests.Session()
    session.headers.update(**_headers)
    return session
