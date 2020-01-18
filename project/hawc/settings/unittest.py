# flake8: noqa

"""
Update settings for rapid-unit-testing:

python manage.py test --settings=hawc.settings.unittest

"""
import logging

from .local import *  # noqa

DEBUG = False


DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "hawc_test",}}

PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)


logging.disable(logging.CRITICAL)
