# flake8: noqa

from .dev import *  # noqa

# DATABASE SETTINGS
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "hawc",
        "USER": "postgres",
        "PASSWORD": "password",
        "HOST": "localhost",
        "PORT": "",
    }
}

# BMD MODELING SETTINGS
BMD_HOST = "http://example.com"  # optional; used for BMD module

# API keys
CHEMSPIDER_TOKEN = r"get-chemspider-token-online"

# SET HAWC FLAVOR (see docs)
HAWC_FLAVOR = "PRIME"
