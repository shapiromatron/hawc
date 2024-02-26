from typing import Any


class HawcException(Exception):
    def __init__(self, status_code: int, message: Any):
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return f"<{self.status_code}> {self.message}"


class HawcClientException(HawcException):
    """An exception occurred in the HAWC client module."""


class HawcServerException(HawcException):
    """An exception occurred on the HAWC server."""


class ContentUnavailable(HawcClientException):
    """Expected content is not available."""
