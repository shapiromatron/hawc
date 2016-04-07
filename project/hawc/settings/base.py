import os
import subprocess
from django.core.urlresolvers import reverse_lazy


PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),
                               os.path.join(os.pardir, os.pardir)))
PROJECT_ROOT = os.path.abspath(os.path.join(PROJECT_PATH, os.pardir))

DEBUG = False

# Basic setup
WSGI_APPLICATION = 'hawc.wsgi.application'
SECRET_KEY = "io^^q^q1))7*r0u@6i+6kx&ek!yxyf6^5vix_6io6k4kdn@@5t"
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
TIME_ZONE = 'America/Chicago'
USE_I18N = False
USE_L10N = True
USE_TZ = True

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "").split("|")

ADMINS = []
_admin_names = os.getenv('DJANGO_ADMIN_NAMES', "")
_admin_emails = os.getenv('DJANGO_ADMIN_EMAILS', "")
if (len(_admin_names) > 0 and len(_admin_emails) > 0):
    ADMINS = zip(_admin_names.split("|"), _admin_emails.split("|"))
MANAGERS = ADMINS


# Template processors
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [
            os.path.join(PROJECT_PATH, 'templates'),
        ],
        'OPTIONS': {
            'context_processors': (
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request"
            ),
        }
    },
]


# Middleware
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'reversion.middleware.RevisionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'fix_ms_office_links.middleware.MicrosoftOfficeLinkMiddleware',
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
    'crispy_forms',
    'compressor',
    'rest_framework_extensions',
    'webpack_loader',

    # Custom apps
    'utils',
    'myuser',
    'assessment',
    'lit',
    'riskofbias',
    'study',
    'animal',
    'epi',
    'epimeta',
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
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('DJANGO_CACHE_SOCK'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient'
        },
        'TIMEOUT': None
    }
}


# Email settings
EMAIL_SUBJECT_PREFIX = '[HAWC] '
DEFAULT_FROM_EMAIL = 'webmaster@hawcproject.org'
SERVER_EMAIL = 'webmaster@hawcproject.org'


# Session and authentication
AUTH_USER_MODEL = 'myuser.HAWCUser'
PASSWORD_RESET_TIMEOUT_DAYS = 3
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'


# Server URL settings
ROOT_URLCONF = 'hawc.urls'
LOGIN_URL = reverse_lazy('user:login')
LOGOUT_URL = reverse_lazy('user:logout')
LOGIN_REDIRECT_URL = reverse_lazy('portal')


# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.getenv('DJANGO_STATIC_ROOT')
STATICFILES_DIRS = os.getenv("DJANGO_STATIC_DIRS", "").split("|")
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.getenv('DJANGO_MEDIA_ROOT')


# Filesystem settings
TEMP_PATH = os.getenv('DJANGO_TEMP_PATH')
INKSCAPE = os.getenv('DJANGO_INKSCAPE')


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
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'include_html': True
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'simple',
            'filename': os.path.join(PROJECT_ROOT, 'hawc.log'),
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 10,
        }
    },
    'loggers': {
        '': {
            'handlers': ['null'],
            'level': 'DEBUG',
        },
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


# commit information
def get_git_commit():
    path = PROJECT_ROOT
    cmd = "git log -1 --format=%H"
    return subprocess.check_output(cmd.split(), cwd=path).strip()

GIT_COMMIT = get_git_commit()
COMMIT_URL = "https://github.com/shapiromatron/hawc/commit/{0}/".format(GIT_COMMIT)


# BMD modeling settings
BMD_ROOT_PATH = os.getenv('DJANGO_BMD_ROOT_PATH', '')
BMD_PLOT = r'gnuplot'
BMD_EXTENSION = ''
BMD_SHELL = 'x11'


# Chemspider token details
CHEMSPIDER_TOKEN = os.getenv('DJANGO_CHEMSPIDER_TOKEN', '')


# Django rest framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny',),
    'PAGE_SIZE': 10,
    'COERCE_DECIMAL_TO_STRING': False
}


# Django pagedown settings
PAGEDOWN_WIDGET_CSS = ('pagedown/demo/browser/demo.css', "css/pagedown.css",)


# Django selectable settings
SELECTABLE_MAX_LIMIT = 10


# Django crispy-forms settings
CRISPY_TEMPLATE_PACK = 'bootstrap'


# Compressor settings
COMPRESS_ENABLED = True

# DRF-Extensions header requirement
REST_FRAMEWORK_EXTENSIONS = {
    'DEFAULT_BULK_OPERATION_HEADER_NAME': 'X-CUSTOM-BULK-OPERATION'
}

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'bundles/',
        'STATS_FILE': os.path.join(PROJECT_PATH, 'webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'IGNORE': ['.+/.map']
    }
}
