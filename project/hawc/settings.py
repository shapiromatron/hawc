"""
By default these are the settings used in the production environment. To run a
local environment, add an environment variable DJANGO_ENVIRONMENT=development.
Then, add a settings file named settings_local.py and add any overridden settings
in the local file.
"""

import os
import sys
from django.core.urlresolvers import reverse_lazy


PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
PROJECT_ROOT = os.path.abspath(os.path.join(PROJECT_PATH, os.pardir))

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ("hawcproject.org",
                 "hawcproject.com",
                 "www.hawcproject.org",
                 "www.hawcproject.com")

ADMINS = (
    ('Andy Shapiro', 'shapiromatron@gmail.com'),
)

MANAGERS = ADMINS

# Email settings
EMAIL_HOST = os.getenv('DJANGO_EMAIL_HOST')
EMAIL_HOST_USER = os.getenv('DJANGO_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('DJANGO_EMAIL_HOST_PASSWORD')
EMAIL_SUBJECT_PREFIX = '[HAWC] '
DEFAULT_FROM_EMAIL = 'webmaster@hawcproject.org'
SERVER_EMAIL = 'webmaster@hawcproject.org'

# DB settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DJANGO_DB_NAME'),
        'USER': os.getenv('DJANGO_DB_USER'),
        'PASSWORD': os.getenv('DJANGO_DB_PW'),
        'HOST': '',
        'PORT': '',
    }
}

# Cache settings. Reference:
# http://docs.webfaction.com/software/django/config.html#django-memcached
CACHES = {
    'default': {
        'BACKEND': 'redis_cache.cache.RedisCache',
        'LOCATION': os.getenv('DJANGO_CACHE_SOCK'),
        'OPTIONS': {
            'CLIENT_CLASS': 'redis_cache.client.DefaultClient'
        },
        'TIMEOUT': None  # no timeout
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# datetime settings
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
TIME_ZONE = 'America/Chicago'
USE_I18N = False  # load international machinery?
USE_L10N = True  # format dates and calendars according to current locale?
USE_TZ = True    # use timezone-aware datetimes?

# Absolute path to the directory that will hold user-uploaded files
MEDIA_ROOT = os.getenv('DJANGO_MEDIA_ROOT')

# URL that handles the media served from MEDIA_ROOT. Include trailing /.
MEDIA_URL = '/media/'

# Absolute path to place collected static files. Include trailing /.
STATIC_ROOT = os.getenv('DJANGO_STATIC_ROOT')

# URL prefix for serving static files. Include trailing /.
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.getenv('DJANGO_STATIC_DIR1'),
    os.getenv('DJANGO_STATIC_DIR2'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
                               "django.core.context_processors.debug",
                               "django.core.context_processors.i18n",
                               "django.core.context_processors.media",
                               "django.core.context_processors.static",
                               "django.core.context_processors.tz",
                               "django.contrib.messages.context_processors.messages",
                               'django.core.context_processors.request')

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'reversion.middleware.RevisionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

LOGIN_URL = reverse_lazy('user:login')
LOGOUT_URL = reverse_lazy('user:logout')
LOGIN_REDIRECT_URL = reverse_lazy('portal')
ROOT_URLCONF = 'hawc.urls'
AUTH_USER_MODEL = 'myuser.HAWCUser'
PASSWORD_RESET_TIMEOUT_DAYS = 2

WSGI_APPLICATION = 'hawc.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates'),
)

INSTALLED_APPS = (
    # Django apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',

    # External apps
    'rest_framework',
    'reversion',
    'taggit',
    'treebeard',
    'selectable',

    # Custom apps
    'utils',
    'myuser',
    'assessment',
    'lit',
    'study',
    'animal',
    'epi',
    'invitro',
    'bmd',
    'api',
    'summary',
    'comments',
    'data_pivot'
)

# Logging configuration
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
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True
        }
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        }
    }
}

# Server application filesystem settings
TEMP_PATH = os.getenv('DJANGO_TEMP_PATH')

# BMD modeling settings
BMD_ROOT_PATH = os.getenv('DJANGO_BMD_ROOT_PATH')
BMD_PLOT = r'gnuplot'
BMD_EXTENSION = ''
BMD_SHELL = 'x11'

# SVG to PNG settings
RSVG_CONVERT = os.getenv('DJANGO_RSVG_CONVERT_PATH')  # optional
INKSCAPE = os.getenv('DJANGO_INKSCAPE')  # required

# chemspider token details
CHEMSPIDER_TOKEN = os.getenv('DJANGO_CHEMSPIDER_TOKEN')

# Celery settings
CELERY_RESULT_BACKEND = os.getenv('DJANGO_CELERY_RESULT_BACKEND')
BROKER_URL = os.getenv('DJANGO_BROKER_URL')
CELERY_TASK_RESULT_EXPIRES = 18000  # 5 hours.
CELERYD_CONCURRENCY = 3

# Django rest framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny',),
    'PAGINATE_BY': 10
}

# Django selectable settings
SELECTABLE_MAX_LIMIT = 10

# Change database-location in testing phase; special case in case user does not
# have ability to create new databases on webserver
if ((not DEBUG) and
    (('test' in sys.argv) or
     ('test_coverage' in sys.argv))):
    #http://docs.webfaction.com/software/private-databases.html#private-postgresql-instances
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'django_test_db',
            'USER': 'django_test_user',
            'PASSWORD': 'passsword',
            'HOST': 'localhost',
            'PORT': '32410',
        }
    }

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Overwrite settings for local environment
if os.getenv('DJANGO_ENVIRONMENT', 'not_development') == 'development':
    from hawc.settings_local import *
