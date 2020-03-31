# flake8: noqa

from .dev import *  # noqa

# DATABASE SETTINGS
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "hawc",
        "USER": "hawc",
        "PASSWORD": "",
        "HOST": "localhost",
        "PORT": "",
    }
}

# BMD MODELING SETTINGS
BMD_HOST = "http://example.com"  # optional; used for BMD module

# SET HAWC FLAVOR (see docs)
HAWC_FLAVOR = "PRIME"
