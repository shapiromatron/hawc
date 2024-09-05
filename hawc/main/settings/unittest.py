# flake8: noqa

import logging

from ...constants import AuthProvider

from .dev import *

DEBUG = True

# enable feature flags for tests
HAWC_FEATURES.ENABLE_BMDS_33 = True
HAWC_FEATURES.ENABLE_UDF = True
HAWC_FEATURES.ENABLE_DOCS_LINK = True

# remove toolbar for integration tests
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "debug_toolbar"]
MIDDLEWARE = [middleware for middleware in MIDDLEWARE if "debug_toolbar" not in middleware]

AUTH_PROVIDERS = {AuthProvider.django, AuthProvider.external}

HAWC_FLAVOR = "PRIME"
ANYONE_CAN_CREATE_ASSESSMENTS = True

# default database name; this is used when managing fixtures
DATABASES["default"]["NAME"] = "hawc-fixture"
# default test database name; this is used when the test suite is ran
DATABASES["default"]["TEST"] = {"NAME": "hawc-test"}

IS_TESTING = True

PRIVATE_DATA_ROOT = PROJECT_ROOT / "tests/data/private-data"

PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)

ANYONE_CAN_CREATE_ASSESSMENTS = True
PM_CAN_MAKE_PUBLIC = True
ACCEPT_LICENSE_REQUIRED = True

EXTERNAL_CONTACT_US = None
EXTERNAL_ABOUT = None
EXTERNAL_RESOURCES = None

if HERO_API_KEY is None:
    HERO_API_KEY = "secret"

logging.disable(logging.CRITICAL)
