import json
import os
import sys
from pathlib import Path
from typing import List, Tuple

from django.core.urlresolvers import reverse_lazy

PROJECT_PATH = Path(__file__).parents[2].absolute()
PROJECT_ROOT = PROJECT_PATH.parent
PUBLIC_DATA_ROOT = Path(os.environ.get("PUBLIC_DATA_ROOT", PROJECT_ROOT / "public"))

DEBUG = False

# Basic setup
WSGI_APPLICATION = "hawc.main.wsgi.application"
SECRET_KEY = "io^^q^q1))7*r0u@6i+6kx&ek!yxyf6^5vix_6io6k4kdn@@5t"
LANGUAGE_CODE = "en-us"
SITE_ID = 1
TIME_ZONE = "America/Chicago"
USE_I18N = False
USE_L10N = True
USE_TZ = True

ADMINS: List[Tuple[str, str]] = []
_admin_names = os.getenv("DJANGO_ADMIN_NAMES", "")
_admin_emails = os.getenv("DJANGO_ADMIN_EMAILS", "")
if len(_admin_names) > 0 and len(_admin_emails) > 0:
    ADMINS = list(zip(_admin_names.split("|"), _admin_emails.split("|")))
MANAGERS = ADMINS

# add randomness to url prefix to prevent easy access
ADMIN_URL_PREFIX = os.getenv("ADMIN_URL_PREFIX", "f09ea0b8-c3d5-4ff9-86c4-27f00e8f643d")

# {PRIME, EPA}
HAWC_FLAVOR = os.getenv("HAWC_FLAVOR", "PRIME")

# Template processors
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "DIRS": [str(PROJECT_PATH / "templates")],
        "OPTIONS": {
            "context_processors": (
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
                "hawc.apps.common.context_processors.from_settings",
            ),
        },
    },
]


# Middleware
MIDDLEWARE_CLASSES = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.SessionAuthenticationMiddleware",
    "reversion.middleware.RevisionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "hawc.apps.common.middleware.MicrosoftOfficeLinkMiddleware",
)


# Install applications
INSTALLED_APPS = (
    # Django apps
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "django.contrib.humanize",
    # External apps
    "rest_framework",
    "rest_framework.authtoken",
    "reversion",
    "taggit",
    "treebeard",
    "selectable",
    "pagedown",
    "markdown_deux",
    "crispy_forms",
    "rest_framework_extensions",
    "webpack_loader",
    # Custom apps
    "hawc.apps.common",
    "hawc.apps.myuser",
    "hawc.apps.assessment",
    "hawc.apps.lit",
    "hawc.apps.riskofbias",
    "hawc.apps.study",
    "hawc.apps.animal",
    "hawc.apps.epi",
    "hawc.apps.epimeta",
    "hawc.apps.invitro",
    "hawc.apps.bmd",
    "hawc.apps.summary",
    "hawc.apps.mgmt",
)


# DB settings
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("DJANGO_DB_NAME", "hawc"),
        "USER": os.getenv("DJANGO_DB_USER", "postgres"),
        "PASSWORD": os.getenv("DJANGO_DB_PW", ""),
        "HOST": os.getenv("DJANGO_DB_HOST", "localhost"),
        "PORT": os.getenv("DJANGO_DB_PORT", ""),
        "CONN_MAX_AGE": 300,
    }
}


# Celery settings
CELERY_RESULT_BACKEND = os.getenv("DJANGO_CELERY_RESULT_BACKEND")
CELERY_BROKER_URL = os.getenv("DJANGO_BROKER_URL")
CELERY_RESULT_EXPIRES = 60 * 60 * 5  # 5 hours
CELERY_RESULT_SERIALIZER = "pickle"
CELERY_ACCEPT_CONTENT = ("json", "pickle")


# Cache settings
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("DJANGO_CACHE_LOCATION"),
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "TIMEOUT": None,
    }
}


# Email settings
EMAIL_SUBJECT_PREFIX = os.environ.get("EMAIL_SUBJECT_PREFIX", "[HAWC] ")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "webmaster@hawcproject.org")
SERVER_EMAIL = os.environ.get("SERVER_EMAIL", "webmaster@hawcproject.org")


# Session and authentication
AUTH_USER_MODEL = "myuser.HAWCUser"
PASSWORD_RESET_TIMEOUT_DAYS = 3
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_CACHE_ALIAS = "default"


# Server URL settings
ROOT_URLCONF = "hawc.main.urls"
LOGIN_URL = reverse_lazy("user:login")
LOGOUT_URL = reverse_lazy("user:logout")
LOGIN_REDIRECT_URL = reverse_lazy("portal")


# Static files
STATIC_URL = "/static/"
STATIC_ROOT = str(PUBLIC_DATA_ROOT / "static")
STATICFILES_DIRS = (str(PROJECT_PATH / "static"),)
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)


# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = str(PUBLIC_DATA_ROOT / "media")
FILE_UPLOAD_PERMISSIONS = 0o755


# Phantom JS settings
PHANTOMJS_ENV = json.loads(os.getenv("PHANTOMJS_ENV", "{}"))
PHANTOMJS_PATH = os.getenv("PHANTOMJS_PATH", "phantomjs")

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "handlers": {
        "null": {"level": "DEBUG", "class": "logging.NullHandler"},
        "console": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "simple"},
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "filters": ["require_debug_false"],
            "include_html": True,
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "simple",
            "filename": str(PROJECT_ROOT / "hawc.log"),
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 10,
        },
    },
    "loggers": {
        "": {"handlers": ["null"], "level": "DEBUG"},
        "django": {"handlers": ["null"], "propagate": True, "level": "INFO"},
        "django.request": {"handlers": ["mail_admins"], "level": "ERROR", "propagate": False},
    },
}


# commit information
GIT_COMMIT_FILE = str(PROJECT_ROOT / ".gitcommit")


def get_git_commit():
    if os.path.exists(GIT_COMMIT_FILE):
        with open(GIT_COMMIT_FILE, "r") as f:
            return f.read()
    return None


GIT_COMMIT = get_git_commit()
COMMIT_URL = "https://github.com/shapiromatron/hawc/"
if GIT_COMMIT:
    COMMIT_URL = COMMIT_URL + f"commit/{GIT_COMMIT}/"


# PubMed settings
PUBMED_API_KEY = os.getenv("PUBMED_API_KEY")

# BMD modeling settings
BMDS_SUBMISSION_URL = os.getenv("BMDS_SUBMISSION_URL", "http://example.com/api/dfile/")
BMDS_TOKEN = os.getenv("BMDS_TOKEN", "token")

# increase allowable fields in POST for updating reviewers
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

# Chemspider token details
CHEMSPIDER_TOKEN = os.getenv("CHEMSPIDER_TOKEN", "")

# Django rest framework settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
    "PAGE_SIZE": 10,
    "COERCE_DECIMAL_TO_STRING": False,
}
REST_FRAMEWORK_EXTENSIONS = {"DEFAULT_BULK_OPERATION_HEADER_NAME": "X-CUSTOM-BULK-OPERATION"}


# Django pagedown settings
PAGEDOWN_WIDGET_CSS = (
    "pagedown/demo/browser/demo.css",
    "css/pagedown.css",
)

# Django selectable settings
SELECTABLE_MAX_LIMIT = 10

# Django crispy-forms settings
CRISPY_TEMPLATE_PACK = "bootstrap"

WEBPACK_LOADER = {
    "DEFAULT": {
        "BUNDLE_DIR_NAME": "bundles/",
        "STATS_FILE": str(PROJECT_ROOT / "webpack-stats.json"),
        "POLL_INTERVAL": 0.1,
        "IGNORE": [".+/.map"],
    }
}

MODIFY_HELP_TEXT = "makemigrations" not in sys.argv
