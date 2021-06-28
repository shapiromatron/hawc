# flake8: noqa

from .base import *

DEBUG = True

SERVER_ROLE = "dev"
SERVER_BANNER_COLOR = "#707070"
ADMIN_URL_PREFIX = ""

INSTALLED_APPS += (
    "debug_toolbar",
    "django_extensions",
)

MIDDLEWARE += ("debug_toolbar.middleware.DebugToolbarMiddleware",)

INTERNAL_IPS = [
    "127.0.0.1",
]

# use console for email
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# execute celery-tasks locally instead of sending to queue
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "TIMEOUT": 60 * 10,  # 10 minutes (in seconds)
    }
}

LOGGING["loggers"][""]["handlers"] = ["console"]
LOGGING["loggers"]["django"]["handlers"] = ["console"]
LOGGING["loggers"]["hawc"]["handlers"] = ["console"]


COMPRESS_ENABLED = False

try:
    # load local settings from `local.py` if they exist
    from .local import *
except ModuleNotFoundError:
    pass
