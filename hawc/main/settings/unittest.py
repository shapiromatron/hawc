# flake8: noqa

import logging

from .dev import *  # noqa

DEBUG = True

HAWC_FLAVOR = "PRIME"

DATABASES["default"]["NAME"] = f"hawc-fixture-test"

PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)

TEST_DB_FIXTURE = PROJECT_ROOT / "tests/data/fixtures/db.yaml"

logging.disable(logging.CRITICAL)
