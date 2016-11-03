from .base import *  # noqa


DEBUG = True

SERVER_ROLE = "dev"

INSTALLED_APPS += ('debug_toolbar', 'django_extensions', 'django_coverage')

STATICFILES_DIRS += (
    os.path.join(PROJECT_ROOT, 'project', 'static'),
)

# use console for email
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# execute celery-tasks locally instead of sending to queue
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

DEBUG_TOOLBAR_CONFIG = dict(
    JQUERY_URL='/static/debug/jquery/1.9.1/jquery.js',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'hawc_cache_table',
        'TIMEOUT': 60*60*24  # seconds
    }
}


LOGGING['loggers']['']['handlers'] = ['console']


COMPRESS_ENABLED = False
