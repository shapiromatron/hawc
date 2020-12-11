# flake8: noqa

import logging

from .dev import *  # noqa

DEBUG = True

# remove toolbar for selenium tests
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "debug_toolbar"]
MIDDLEWARE = [middleware for middleware in MIDDLEWARE if "debug_toolbar" not in middleware]

HAWC_FLAVOR = "PRIME"

DATABASES["default"]["NAME"] = "hawc-fixture-test"

PRIVATE_DATA_ROOT = PROJECT_ROOT / "tests/data/private-data"

PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)

logging.disable(logging.CRITICAL)
