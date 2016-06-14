from .dev import *


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
BMD_ROOT_PATH = r'/path/to/bmds'
BMD_PLOT = r'gnuplot'
BMD_EXTENSION = ''
BMD_SHELL = 'x11'

# MODELING TEMP PATH
TEMP_PATH = r'/path/to/temp'

# PHANTOMJS SETTINGS
PHANTOMJS_PATH = r'/path/to/phantomjs'

# API keys
CHEMSPIDER_TOKEN = r'get-chemspider-token-online'
