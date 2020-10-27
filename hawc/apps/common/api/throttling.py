from rest_framework.throttling import UserRateThrottle


class OncePerMinuteThrottle(UserRateThrottle):
    rate = "1/min"
