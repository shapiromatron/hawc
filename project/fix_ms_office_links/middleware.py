from django.http import HttpResponse
import re


class MicrosoftOfficeLinkMiddleware(object):
    # https://support.microsoft.com/en-us/kb/899927
    # https://github.com/spilliton/fix_microsoft_links

    OFFICE_AGENTS = re.compile(r"(Word|Excel|PowerPoint|ms-office)")
    OUTLOOK_AGENTS = re.compile(r"(Microsoft Outlook)")
    RESPONSE_TEXT = (
        """<html><head><meta http-equiv="refresh" content="0"/></head><body></body></html>"""
    )

    def process_request(self, request):
        agent = request.META.get("HTTP_USER_AGENT", "")
        if re.findall(self.OFFICE_AGENTS, agent) and not re.findall(self.OUTLOOK_AGENTS, agent):
            return HttpResponse(self.RESPONSE_TEXT)
