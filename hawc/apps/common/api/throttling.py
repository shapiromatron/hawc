from rest_framework.throttling import UserRateThrottle


class OncePerMinuteThrottle(UserRateThrottle):
    rate = "1/min"


class FivePerMinuteThrottle(UserRateThrottle):
    rate = "5/min"
