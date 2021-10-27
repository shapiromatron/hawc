from enum import Enum


class AuthProvider(str, Enum):
    django = "django"
    external = "external"
