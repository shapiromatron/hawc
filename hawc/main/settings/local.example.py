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

# disable cache (comment to use cache; uncomment to disable)
CACHES["default"]["BACKEND"] = "django.core.cache.backends.dummy.DummyCache"

# to show lots of debugging:
# LOGGING["loggers"]["hawc"]["level"] = "DEBUG"

# view all database queries in console
# LOGGING["loggers"]["django.db.backends"] = {"handlers": ["console"], "level": "DEBUG"}

# BMD MODELING SETTINGS
BMD_HOST = "http://example.com"  # optional; used for BMD module

# SET HAWC FLAVOR (see docs)
HAWC_FLAVOR = "PRIME"
