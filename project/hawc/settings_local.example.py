from settings import INSTALLED_APPS

DEBUG = True
TEMPLATE_DEBUG = DEBUG
FORCE_SCRIPT_NAME = ''

SERVE_MEDIA = True

TEMP_PATH = r'/path/to/temp'
MEDIA_ROOT = r'/path/to/temp/media'
STATIC_ROOT = r'/path/to/temp/static'

STATICFILES_DIRS = (
    r'/path/to/hawc/project/static',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'reversion.middleware.RevisionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

lst = list(INSTALLED_APPS)
lst.extend(['debug_toolbar', 'django_extensions', 'django_coverage'])
INSTALLED_APPS = tuple(lst)
DEBUG_TOOLBAR_CONFIG = {'INTERCEPT_REDIRECTS': False}

INTERNAL_IPS = ('127.0.0.1',)

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

BMD_ROOT_PATH = r'/path/to/bmds'
BMD_PLOT = r'gnuplot'
BMD_EXTENSION = ''
BMD_SHELL = 'x11'

INKSCAPE = r'/path/to/inkscape'

# API keys
CHEMSPIDER_TOKEN = r'get-chemspider-token-online'

# Celery settings
BROKER_URL = 'amqp://guest:guest@localhost//'
CELERY_RESULT_BACKEND = 'amqp'

# Setup Gmail for email testing
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'hiking.fan@gmail.com'
EMAIL_HOST_PASSWORD = 'password'
EMAIL_USE_TLS = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG'
        },
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['null'],
            'level': 'ERROR',
            'propagate': False,
        }
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'dev_cache_table',
        'TIMEOUT': 60*60*24  # number of seconds
    }
}
