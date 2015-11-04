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

# EMAIL SETTINGS
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'hiking.fan@gmail.com'
EMAIL_HOST_PASSWORD = 'password'
EMAIL_USE_TLS = True

# BMD MODELING SETTINGS
BMD_ROOT_PATH = r'/path/to/bmds'
BMD_PLOT = r'gnuplot'
BMD_EXTENSION = ''
BMD_SHELL = 'x11'

# MODELING TEMP PATH
TEMP_PATH = r'/path/to/temp'

# INKSCAPE SETTINGS
INKSCAPE = r'/path/to/inkscape'

# API keys
CHEMSPIDER_TOKEN = r'get-chemspider-token-online'
