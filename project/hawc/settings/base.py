import os
import sys
from django.core.urlresolvers import reverse_lazy

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname( __file__ ),
                               os.path.join(os.pardir, os.pardir)))
PROJECT_ROOT = os.path.abspath(os.path.join(PROJECT_PATH, os.pardir))

DEBUG = False
TEMPLATE_DEBUG = DEBUG


# Basic setup
WSGI_APPLICATION = 'hawc.wsgi.application'
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
TIME_ZONE = 'America/Chicago'
USE_I18N = False
USE_L10N = True
USE_TZ = True

ALLOWED_HOSTS = ("hawcproject.org",
                 "hawcproject.com",
                 "www.hawcproject.org",
                 "www.hawcproject.com")

ADMINS = (
    ('Andy Shapiro', 'shapiromatron@gmail.com'),
)
MANAGERS = ADMINS


# Template processors
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request"
)


# Middleware
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


# Install applications
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
    'pagedown',
    'markdown_deux',
    'static_precompiler',
    'crispy_forms',

    # Custom apps
    'utils',
    'myuser',
    'assessment',
    'api',
    'lit',
    'study',
    'animal',
    'epi',
    'invitro',
    'bmd',
    'summary',
    'comments',
)


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


# Celery settings
CELERY_RESULT_BACKEND = os.getenv('DJANGO_CELERY_RESULT_BACKEND')
BROKER_URL = os.getenv('DJANGO_BROKER_URL')
CELERY_TASK_RESULT_EXPIRES = 18000  # 5 hours.
CELERYD_CONCURRENCY = 3


# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'redis_cache.cache.RedisCache',
        'LOCATION': os.getenv('DJANGO_CACHE_SOCK'),
        'OPTIONS': {
            'CLIENT_CLASS': 'redis_cache.client.DefaultClient'
        },
        'TIMEOUT': None
    }
}


# Email settings
EMAIL_HOST = os.getenv('DJANGO_EMAIL_HOST')
EMAIL_HOST_USER = os.getenv('DJANGO_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('DJANGO_EMAIL_HOST_PASSWORD')
EMAIL_SUBJECT_PREFIX = '[HAWC] '
DEFAULT_FROM_EMAIL = 'webmaster@hawcproject.org'
SERVER_EMAIL = 'webmaster@hawcproject.org'


# Session and authentication
AUTH_USER_MODEL = 'myuser.HAWCUser'
PASSWORD_RESET_TIMEOUT_DAYS = 3
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'


# Server URL settings
ROOT_URLCONF = 'hawc.urls'
MEDIA_URL = '/media/'
STATIC_URL = '/static/'
LOGIN_URL = reverse_lazy('user:login')
LOGOUT_URL = reverse_lazy('user:logout')
LOGIN_REDIRECT_URL = reverse_lazy('portal')


# Filesystem settings
MEDIA_ROOT = os.getenv('DJANGO_MEDIA_ROOT')
STATIC_ROOT = os.getenv('DJANGO_STATIC_ROOT')
TEMP_PATH = os.getenv('DJANGO_TEMP_PATH')
BMD_ROOT_PATH = os.getenv('DJANGO_BMD_ROOT_PATH')
INKSCAPE = os.getenv('DJANGO_INKSCAPE')
RSVG_CONVERT = os.getenv('DJANGO_RSVG_CONVERT_PATH')

STATICFILES_DIRS = (
    os.getenv('DJANGO_STATIC_DIR1'),
    os.getenv('DJANGO_STATIC_DIR2'),
)

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'static_precompiler.finders.StaticPrecompilerFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
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


# BMD modeling settings
BMD_PLOT = r'gnuplot'
BMD_EXTENSION = ''
BMD_SHELL = 'x11'


# Chemspider token details
CHEMSPIDER_TOKEN = os.getenv('DJANGO_CHEMSPIDER_TOKEN')


# Django rest framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny',),
    'PAGINATE_BY': 10,
    'COERCE_DECIMAL_TO_STRING': False
}


# Django pagedown settings
PAGEDOWN_WIDGET_CSS = ('pagedown/demo/browser/demo.css', "css/pagedown.css",)


# Django selectable settings
SELECTABLE_MAX_LIMIT = 10

# Django-static-precompiler settings
STATIC_PRECOMPILER_COMPILERS = (
    'static_precompiler.compilers.CoffeeScript',
)

STATIC_PRECOMPILER_OUTPUT_DIR = 'compiled'

# Django crispy-forms settings
CRISPY_TEMPLATE_PACK = 'bootstrap'

# Testing settings
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
if ((not DEBUG) and
    (('test' in sys.argv) or
     ('test_coverage' in sys.argv))):

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

