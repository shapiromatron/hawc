import os
import sys
from datetime import datetime
from pathlib import Path
from subprocess import CalledProcessError

from django.urls import reverse_lazy

from hawc.constants import AuthProvider, FeatureFlags
from hawc.services.utils.git import Commit

PROJECT_PATH = Path(__file__).parents[2].absolute()
PROJECT_ROOT = PROJECT_PATH.parent
PUBLIC_DATA_ROOT = Path(os.environ.get("PUBLIC_DATA_ROOT", PROJECT_ROOT / "public"))
PRIVATE_DATA_ROOT = Path(os.environ.get("PRIVATE_DATA_ROOT", PROJECT_ROOT / "private"))
LOGS_ROOT = Path(os.environ.get("LOGS_PATH", PROJECT_ROOT))

DEBUG = False

# Basic setup
WSGI_APPLICATION = "hawc.main.wsgi.application"
SECRET_KEY = "io^^q^q1))7*r0u@6i+6kx&ek!yxyf6^5vix_6io6k4kdn@@5t"  # noqa: S105
LANGUAGE_CODE = "en-us"
SITE_ID = 1
TIME_ZONE = os.getenv("TIME_ZONE", "US/Eastern")
USE_I18N = False
USE_TZ = True

ADMINS: list[tuple[str, str]] = []
_admin_names = os.getenv("DJANGO_ADMIN_NAMES", "")
_admin_emails = os.getenv("DJANGO_ADMIN_EMAILS", "")
if len(_admin_names) > 0 and len(_admin_emails) > 0:
    ADMINS = list(zip(_admin_names.split("|"), _admin_emails.split("|"), strict=True))
MANAGERS = ADMINS

# add randomness to admin url
ADMIN_URL_PREFIX = os.getenv("ADMIN_URL_PREFIX", "f09ea0b8-c3d5-4ff9-86c4-27f00e8f643d")
ADMIN_ROOT = os.environ.get("ADMIN_ROOT", "")

# add randomness to healthcheck url
HEALTHCHECK_URL_PREFIX = os.getenv("HEALTHCHECK_URL_PREFIX", "4df02970-c4f8-4e16-8a75-e9eaf4dabac7")

# {PRIME, EPA}
HAWC_FLAVOR = os.getenv("HAWC_FLAVOR", "PRIME")

# Feature flags
HAWC_FEATURES = FeatureFlags.from_env("HAWC_FEATURE_FLAGS")

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
            "builtins": [
                "crispy_forms.templatetags.crispy_forms_tags",
                "hawc.apps.common.templatetags.bs4",
                "hawc.apps.common.templatetags.hawc",
            ],
        },
    },
]

# Middleware
MIDDLEWARE = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "hawc.apps.common.middleware.CsrfRefererCheckMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "reversion.middleware.RevisionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    "hawc.apps.common.middleware.MicrosoftOfficeLinkMiddleware",
    "hawc.apps.common.middleware.RequestLogMiddleware",
    "hawc.apps.common.middleware.ThreadLocalMiddleware",
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
    "dal",
    "dal_select2",
    "django.contrib.admin",
    "django.contrib.humanize",
    "django.contrib.postgres",
    "django_filters",
    # External apps
    "rest_framework",
    "rest_framework.authtoken",
    "reversion",
    "taggit",
    "treebeard",
    "crispy_forms",
    "crispy_bootstrap4",
    "webpack_loader",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail_draftail_anchors",
    "wagtail",
    "modelcluster",
    # Custom apps
    "hawc.apps.common",
    "hawc.apps.myuser",
    "hawc.apps.assessment",
    "hawc.apps.vocab",
    "hawc.apps.lit",
    "hawc.apps.riskofbias",
    "hawc.apps.study",
    "hawc.apps.animal",
    "hawc.apps.eco",
    "hawc.apps.epi",
    "hawc.apps.epimeta",
    "hawc.apps.invitro",
    "hawc.apps.bmd",
    "hawc.apps.summary",
    "hawc.apps.mgmt",
    "hawc.apps.hawc_admin",
    "hawc.apps.materialized",
    "hawc.apps.epiv2",
    "hawc.apps.udf",
    "hawc.apps.docs",
    "hawc.apps.animalv2",
)
# DB settings
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DJANGO_DB_NAME", "hawc"),
        "USER": os.getenv("DJANGO_DB_USER", "hawc"),
        "PASSWORD": os.getenv("DJANGO_DB_PW", ""),
        "HOST": os.getenv("DJANGO_DB_HOST", "localhost"),
        "PORT": os.getenv("DJANGO_DB_PORT", ""),
        "CONN_MAX_AGE": 300,
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Celery settings
CELERY_BROKER_URL = os.getenv("DJANGO_BROKER_URL")
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_RESULT_BACKEND = os.getenv("DJANGO_CELERY_RESULT_BACKEND")
CELERY_RESULT_EXPIRES = 60 * 60 * 5  # 5 hours
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_SOFT_TIME_LIMIT = 660
CELERY_TASK_TIME_LIMIT = 600
CELERY_WORKER_MAX_TASKS_PER_CHILD = 10
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

# Cache settings
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("DJANGO_CACHE_LOCATION"),
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "TIMEOUT": 60 * 60 * 24 * 10,  # 10 days
    }
}
CACHE_1_HR = 60 * 60
CACHE_10_MIN = 60 * 10

# Email settings
EMAIL_SUBJECT_PREFIX = os.environ.get("EMAIL_SUBJECT_PREFIX", "[HAWC] ")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "admin@hawcproject.org")
SERVER_EMAIL = os.environ.get("SERVER_EMAIL", "admin@hawcproject.org")

# External page handlers
EXTERNAL_CONTACT_US = os.getenv("HAWC_EXTERNAL_CONTACT_US", "")
EXTERNAL_ABOUT = os.getenv("HAWC_EXTERNAL_ABOUT", "")
EXTERNAL_HOME = os.getenv("HAWC_EXTERNAL_HOME", "")
EXTERNAL_RESOURCES = os.getenv("HAWC_EXTERNAL_RESOURCES", "")

# Session and authentication
AUTH_USER_MODEL = "myuser.HAWCUser"
AUTH_PROVIDERS = {AuthProvider(p) for p in os.getenv("HAWC_AUTH_PROVIDERS", "django").split("|")}
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "hawc.apps.common.auth.TokenBackend",
]
PASSWORD_RESET_TIMEOUT = 259200  # 3 days, in seconds
CSRF_TRUSTED_ORIGINS = os.getenv("HAWC_CSRF_TRUSTED_ORIGINS", "https://").split("|")
SESSION_COOKIE_AGE = int(os.getenv("HAWC_SESSION_DURATION", "604800"))  # 1 week
SESSION_COOKIE_DOMAIN = os.getenv("HAWC_SESSION_COOKIE_DOMAIN", None)
SESSION_COOKIE_NAME = os.getenv("HAWC_SESSION_COOKIE_NAME", "sessionid")
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_CACHE_ALIAS = "default"
TURNSTILE_SITE = os.environ.get("TURNSTILE_SITE", "")
TURNSTILE_KEY = os.environ.get("TURNSTILE_KEY", "")
INCLUDE_ADMIN = bool(os.environ.get("HAWC_INCLUDE_ADMIN", "True") == "True")
EMAIL_VERIFICATION_REQUIRED = bool(os.environ.get("EMAIL_VERIFICATION_REQUIRED", "False") == "True")

# Server URL settings
ROOT_URLCONF = "hawc.main.urls"
LOGIN_URL = reverse_lazy("user:login")
LOGIN_REDIRECT_URL = reverse_lazy("portal")
LOGOUT_REDIRECT_URL = os.getenv("HAWC_LOGOUT_REDIRECT", reverse_lazy("home"))
DISABLED_LOGIN_HOSTS = os.getenv("HAWC_DISABLED_LOGIN_HOSTS", "").split("|")

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

# Wagtail setup
WAGTAIL_SITE_NAME = "HAWC"
WAGTAILADMIN_BASE_URL = ""
WAGTAIL_FRONTEND_LOGIN_URL = LOGIN_URL
DRAFTAIL_ANCHORS_RENDERER = "wagtail_draftail_anchors.rich_text.render_span"
WAGTAIL_PASSWORD_MANAGEMENT_ENABLED = False
WAGTAILUSERS_PASSWORD_ENABLED = False
WAGTAIL_EMAIL_MANAGEMENT_ENABLED = False
WAGTAIL_ENABLE_UPDATE_CHECK = False
WAGTAIL_ALLOW_UNICODE_SLUGS = False

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
        },
        "simple": {"format": "%(levelname)s %(asctime)s %(name)s %(message)s"},
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
        "file_500s": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "simple",
            "filename": str(LOGS_ROOT / "hawc_500s.log"),
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 10,
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "simple",
            "filename": str(LOGS_ROOT / "hawc.log"),
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 10,
        },
        "hawc-request": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "simple",
            "filename": str(LOGS_ROOT / "hawc-request.log"),
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 10,
        },
    },
    "loggers": {
        "": {"handlers": ["null"], "level": "INFO"},
        "django": {"handlers": ["null"], "propagate": False, "level": "INFO"},
        "django.request": {
            "handlers": ["console", "file_500s", "mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
        "hawc": {"handlers": ["null"], "propagate": False, "level": "INFO"},
        "hawc.request": {"handlers": ["null"], "propagate": False, "level": "INFO"},
    },
}


# commit information
def get_git_commit() -> Commit:
    if GIT_COMMIT_FILE.exists():
        return Commit.model_validate_json(GIT_COMMIT_FILE.read_text())
    try:
        return Commit.current(str(PROJECT_ROOT))
    except (CalledProcessError, FileNotFoundError):
        return Commit(sha="<undefined>", dt=datetime.now())


GIT_COMMIT_FILE = PROJECT_PATH / "gitcommit.json"
COMMIT = get_git_commit()

# Google Tag Manager settings
GTM_ID = os.getenv("GTM_ID")

# PubMed settings
PUBMED_API_KEY = os.getenv("PUBMED_API_KEY")
PUBMED_MAX_QUERY_SIZE = 10000

# CCTE API key
CCTE_API_KEY = os.getenv("CCTE_API_KEY")

# increase allowable fields in POST for updating reviewers
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

# Django rest framework settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
    "PAGE_SIZE": 50,
    "COERCE_DECIMAL_TO_STRING": False,
}
REST_FRAMEWORK_EXTENSIONS = {"DEFAULT_BULK_OPERATION_HEADER_NAME": "X-CUSTOM-BULK-OPERATION"}

# Django crispy-forms settings
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = "bootstrap4"

WEBPACK_LOADER = {
    "DEFAULT": {
        "BUNDLE_DIR_NAME": "bundles/",
        "STATS_FILE": str(PROJECT_PATH / "webpack-stats.json"),
        "POLL_INTERVAL": 0.1,
        "IGNORE": [".+/.map"],
    }
}

# can anyone create a new assessment; or can only those in the group `can-create-assessments`
ANYONE_CAN_CREATE_ASSESSMENTS = True

# can project-managers for an assessment make that assessments public, or only administrators?
PM_CAN_MAKE_PUBLIC = True

# are users required to accept a license
ACCEPT_LICENSE_REQUIRED = True

MODIFY_HELP_TEXT = "makemigrations" not in sys.argv

IS_TESTING = False

TEST_DB_FIXTURE = PROJECT_ROOT / "tests/data/fixtures/db.yaml"

DISCLAIMER_TEXT = ""

FORMS_URLFIELD_ASSUME_HTTPS = True
