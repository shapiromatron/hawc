from .dev import *  # noqa


# DATABASE SETTINGS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'hawc',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': '',
        'PORT': '',
    }
}

# BMD MODELING SETTINGS
BMD_HOST = 'http://example.com'  # optional; used for BMD module

# MODELING TEMP PATH
TEMP_PATH = r'/path/to/temp'

# PHANTOMJS SETTINGS
PHANTOMJS_PATH = r'/path/to/phantomjs'

# API keys
CHEMSPIDER_TOKEN = r'get-chemspider-token-online'
