import re
from urllib.parse import urlparse

from django.http import HttpResponse
from django.utils.http import is_same_domain


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
        agent = request.META.get("HTTP_USER_AGENT", "")
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
    RESPONSE_TEXT = (
        '<html><head><meta http-equiv="refresh" content="0"/></head><body></body></html>'
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in self.SAFE_METHODS:
            this_host = request.get_host()
            for header in ["referer", "origin"]:
                value = request.headers.get(header)
                if value:
                    parsed = urlparse(value)
                    if not is_same_domain(parsed.netloc, this_host):
                        return HttpResponse(self.RESPONSE_TEXT)

        # continue standard parsing; no need to redirect
        response = self.get_response(request)

        return response
