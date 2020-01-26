# flake8: noqa

import logging

from .dev import *  # noqa

DEBUG = False

DATABASES["default"]["NAME"] = f"{DATABASES['default']['NAME']}-test"

PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)

TEST_DB_FIXTURE = PROJECT_ROOT / "tests/data/fixtures/db.yaml"

logging.disable(logging.CRITICAL)
