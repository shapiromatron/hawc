from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.throttling import AnonRateThrottle


class SustainedAnon(AnonRateThrottle):
    rate = "100/day"


class BurstAnon(AnonRateThrottle):
    rate = "5/minute"


class HawcObtainAuthToken(ObtainAuthToken):
    throttle_classes = (BurstAnon, SustainedAnon)


hawc_obtain_auth_token = HawcObtainAuthToken.as_view()
