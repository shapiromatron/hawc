from .base import *  # noqa

SERVER_ROLE = 'staging'
SERVER_BANNER_COLOR = '#EE8416'

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '').split('|')

EMAIL_BACKEND = 'django_mailgun.MailgunBackend'
MAILGUN_ACCESS_KEY = os.environ.get('MAILGUN_ACCESS_KEY')
MAILGUN_SERVER_NAME = os.environ.get('MAILGUN_SERVER_NAME')

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

LOGGING['handlers']['file']['filename'] = \
    os.path.join(os.getenv('LOGS_PATH'), 'hawc.log')

LOGGING['loggers']['django']['handlers'] = ['file']
