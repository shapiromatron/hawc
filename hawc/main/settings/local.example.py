# flake8: noqa

from .dev import *

# DATABASE SETTINGS
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "hawc-fixture",
        "USER": "hawc",
        "PASSWORD": "",
        "HOST": "localhost",
        "PORT": "",
    }
}

# use fast hasher for fixture database
if DATABASES["default"]["NAME"] == "hawc-fixture":
    PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)

# # disable cache (comment to use cache; uncomment to disable)
# CACHES["default"] = {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}

# to show lots of debugging:
# LOGGING["loggers"]["hawc"]["level"] = "DEBUG"

# view all database queries in console
# LOGGING["loggers"]["django.db.backends"] = {"handlers": ["console"], "level": "DEBUG"}

# BMD MODELING SETTINGS
BMD_HOST = "http://example.com"  # optional; used for BMD module

# SET HAWC FLAVOR (see docs)
HAWC_FLAVOR = "PRIME"

# override feature flags
HAWC_FEATURES.THIS_IS_AN_EXAMPLE = True
