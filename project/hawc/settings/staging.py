from .base import *

SERVER_ROLE = "staging"

LOGGING['handlers']['file']['filename'] = os.path.join(os.getenv('LOGS_PATH'), 'hawc.log')
LOGGING['loggers']['django']['handlers'] = ['file']

SESSION_COOKIE_SECURE = True
