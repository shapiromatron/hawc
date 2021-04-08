import re

from django.http import HttpResponse


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
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response._headers.pop("Referer", None)
        response._headers.pop("Origin", None)
        return response
