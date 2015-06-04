from .base import *

import logging

DEBUG = True
TEMPLATE_DEBUG = DEBUG
SERVER_ROLE = "dev"

INSTALLED_APPS += ('debug_toolbar', 'django_extensions', 'django_coverage')

STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'project', 'static'),
)

# execute celery-tasks locally instead of sending to queue
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

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
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG'
        },
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['null'],
            'level': 'ERROR',
            'propagate': False,
        }
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 60*60*24  # seconds
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.db"


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
