from django.contrib.auth import login
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView


class SustainedAnon(AnonRateThrottle):
    rate = "100/day"


class BurstAnon(AnonRateThrottle):
    rate = "5/minute"


class HawcObtainAuthToken(ObtainAuthToken):
    throttle_classes = (BurstAnon, SustainedAnon)


hawc_obtain_auth_token = HawcObtainAuthToken.as_view()


class HawcValidateAuthToken(APIView):
    throttle_classes = (BurstAnon, SustainedAnon)
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        if "login" in request.query_params:
            login(request, request.user)
        return Response({"valid": True})
