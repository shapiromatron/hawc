from .base import *

EMAIL_BACKEND = 'django_mailgun.MailgunBackend'
MAILGUN_ACCESS_KEY = os.environ.get('MAILGUN_ACCESS_KEY')
MAILGUN_SERVER_NAME = os.environ.get('MAILGUN_SERVER_NAME')

SERVER_ROLE = "staging"

LOGGING['handlers']['file']['filename'] = \
    os.path.join(os.getenv('LOGS_PATH'), 'hawc.log')

LOGGING['loggers']['django']['handlers'] = ['file']
