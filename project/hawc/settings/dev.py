from .base import *  # noqa


DEBUG = True

SERVER_ROLE = 'dev'
SERVER_BANNER_COLOR = '#707070'

INSTALLED_APPS += (
    'debug_toolbar',
    'django_extensions',
)

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INTERNAL_IPS = [
    '127.0.0.1',
]

# use console for email
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# execute celery-tasks locally instead of sending to queue
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

DEBUG_TOOLBAR_CONFIG = dict(
    JQUERY_URL='/static/debug/jquery/1.9.1/jquery.js',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'hawc_cache_table',
        'TIMEOUT': 60 * 60 * 24  # seconds
    }
}


LOGGING['loggers']['']['handlers'] = ['console']


COMPRESS_ENABLED = False
