# flake8: noqa

from .dev import *  # noqa

# DATABASE SETTINGS
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "hawc-fixture-test",
        "USER": "hawc",
        "PASSWORD": "",
        "HOST": "localhost",
        "PORT": "",
    }
}

# view all database queries in console
# LOGGING["loggers"]["django.db.backends"] = {"handlers": ["console"], "level": "DEBUG"}

# BMD MODELING SETTINGS
BMD_HOST = "http://example.com"  # optional; used for BMD module

# SET HAWC FLAVOR (see docs)
HAWC_FLAVOR = "PRIME"

# cache for 1 sec instead
CACHE_1_HR = 1
