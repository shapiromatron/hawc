import requests
from django.conf import settings


def get_session(headers: dict | None = None):
    _headers = {"User-Agent": settings.USER_AGENT, "Content-Type": "application/json"}
    _headers.update(headers or {})
    session = requests.Session()
    session.headers.update(**_headers)
    return session
