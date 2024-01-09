# flake8: noqa

from .base import *

DEBUG = True

SERVER_ROLE = "dev"
SERVER_BANNER_COLOR = "#6495ED"
ADMIN_URL_PREFIX = ""

INSTALLED_APPS += (
    "debug_toolbar",
    "django_extensions",
    "django_browser_reload",
)

MIDDLEWARE += (
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
)

INTERNAL_IPS = [
    "127.0.0.1",
]

# use console for email
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# execute celery-tasks locally instead of sending to queue
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# use a memory cache if no redis location specified
CACHES["default"]["TIMEOUT"] = 60 * 10  # 10 minutes (in seconds)
if CACHES["default"]["LOCATION"] is None:
    CACHES["default"]["BACKEND"] = "django.core.cache.backends.locmem.LocMemCache"
    del CACHES["default"]["OPTIONS"]

LOGGING["loggers"][""]["handlers"] = ["console"]
LOGGING["loggers"]["hawc.request"]["handlers"] = ["console"]
LOGGING["loggers"]["hawc"]["handlers"] = ["console"]

COMPRESS_ENABLED = False

HAWC_FEATURES.ENABLE_DOCS_LINK = True

try:
    # load local settings from `local.py` if they exist
    from .local import *
except ModuleNotFoundError:
    pass
