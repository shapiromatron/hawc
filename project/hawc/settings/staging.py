from .base import *  # noqa

SERVER_ROLE = 'staging'
SERVER_BANNER_COLOR = '#EE8416'

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '').split('|')

if os.environ.get('DJANGO_EMAIL_BACKEND') == 'SMTP':
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
elif os.environ.get('DJANGO_EMAIL_BACKEND') == 'MAILGUN':
    INSTALLED_APPS += 'anymail'
    EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'
    ANYMAIL = {
        'MAILGUN_API_KEY': os.environ.get('MAILGUN_ACCESS_KEY'),
        'MAILGUN_SENDER_DOMAIN': os.environ.get('MAILGUN_SERVER_NAME'),
    }

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

LOGGING['handlers']['file']['filename'] = \
    os.path.join(os.getenv('LOGS_PATH'), 'hawc.log')

LOGGING['loggers']['django']['handlers'] = ['file']
