# flake8: noqa

import logging

from .local import *  # noqa

DEBUG = False

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "hawc_test",}}

PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)

logging.disable(logging.CRITICAL)
