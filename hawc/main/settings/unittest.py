# flake8: noqa

import logging

from .dev import *  # noqa

DEBUG = False

DATABASES["default"]["NAME"] = f"{DATABASES['default']['NAME']}-test"

PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)

logging.disable(logging.CRITICAL)
