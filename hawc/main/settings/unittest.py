# flake8: noqa

import logging

from .dev import *  # noqa

DEBUG = True

# remove toolbar for selenium tests
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "debug_toolbar"]
MIDDLEWARE = [middleware for middleware in MIDDLEWARE if "debug_toolbar" not in middleware]

HAWC_FLAVOR = "PRIME"
ANYONE_CAN_CREATE_ASSESSMENTS = True

# default database name; this is used when managing fixtures
DATABASES["default"]["NAME"] = "hawc-fixture"
# default test database name; this is used when the test suite is ran
DATABASES["default"]["TEST"] = {"NAME": "hawc-test"}

IS_TESTING = True

PRIVATE_DATA_ROOT = PROJECT_ROOT / "tests/data/private-data"

PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)

logging.disable(logging.CRITICAL)
