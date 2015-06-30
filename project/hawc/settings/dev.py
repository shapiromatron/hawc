from .base import *

import logging

DEBUG = True
for tmp in TEMPLATES:
    tmp['OPTIONS']['debug'] = True

SERVER_ROLE = "dev"

INSTALLED_APPS += ('debug_toolbar', 'django_extensions', 'django_coverage')

STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'project', 'static'),
)

# execute celery-tasks locally instead of sending to queue
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 60*60*24  # seconds
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

LOGGING['loggers']['']['handlers'] = ['console']


# Compressor settings
COMPRESS_ENABLED = False


if 'test' in sys.argv[1:]:

    class DisableMigrations(object):

        def __contains__(self, item):
            return True

        def __getitem__(self, item):
            return "notmigrations"

    DEBUG = False
    DATABASES['default'] = {'ENGINE': 'django.db.backends.sqlite3'}
    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
    )
    logging.disable(logging.CRITICAL)
    MIGRATION_MODULES = DisableMigrations()
