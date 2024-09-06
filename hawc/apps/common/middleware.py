import logging
import re
import threading
from urllib.parse import urlparse

from django.http import HttpRequest, HttpResponse
from django.utils.http import is_same_domain

logger = logging.getLogger("hawc.request")


def get_assessment_id(response: HttpResponse) -> int:
    try:
        # TODO  - refactor DRF viewset to add assessment id
        return response.context_data["view"].assessment.id
    except Exception:
        return 0


def get_user_id(user) -> int:
    return 0 if user.is_anonymous else user.id


class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        response = self.get_response(request)
        message = "{} {} {} {} ip-{} user-{} assess-{}".format(
            request.method,
            request.path,
            response.status_code,
            len(getattr(response, "content", "")),
            request.META["REMOTE_ADDR"],
            get_user_id(request.user),
            get_assessment_id(response),
        )
        logger.info(message)
        return response


class MicrosoftOfficeLinkMiddleware:
    # https://support.microsoft.com/en-us/kb/899927
    # https://github.com/spilliton/fix_microsoft_links

    OFFICE_AGENTS = re.compile(r"(Word|Excel|PowerPoint|ms-office)")
    OUTLOOK_AGENTS = re.compile(r"(Microsoft Outlook)")
    RESPONSE_TEXT = (
        '<html><head><meta http-equiv="refresh" content="0"/></head><body></body></html>'
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        agent = request.headers.get("user-agent", "")
        if re.findall(self.OFFICE_AGENTS, agent) and not re.findall(self.OUTLOOK_AGENTS, agent):
            return HttpResponse(self.RESPONSE_TEXT)
        response = self.get_response(request)
        return response


class CsrfRefererCheckMiddleware:
    """
    Django has built-in middleware for CSRF checks for POST requests, but not for GET. This is
    by design and per RFC 7231 and "safe methods". For more information, see
    https://docs.djangoproject.com/en/3.1/ref/csrf/#how-it-works.

    To check "safe" methods, we validate that the Referer if one exists is from the same domain
    as our site. If not, we request a refresh of the page, which will set the Referer to the
    current site.  This would only be of importance if a SAFE method was modifying state and
    doing so with the Referer attribute, which we should not be doing anyways.
    """

    SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}
    REFRESH = b'<html><head><meta http-equiv="refresh" content="0"/></head><body></body></html>'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in self.SAFE_METHODS:
            this_host = request.get_host()
            for header in ["HTTP_REFERER", "HTTP_ORIGIN"]:
                value = request.META.get(header)
                if value:
                    parsed = urlparse(value)
                    if not is_same_domain(parsed.netloc, this_host):
                        return HttpResponse(self.REFRESH)

        # continue standard parsing; no need to redirect
        response = self.get_response(request)

        return response


_local_thread = threading.local()


class ThreadLocalMiddleware:
    """Allow fetching the current request and user from the current thread.

    Note that this may not be accurate given how the django WSGI application is deployed, but
    should work fine using gunicorn and standard workers.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        _local_thread.request = request
        return self.get_response(request)
