import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hawc.settings')
os.environ['LC_ALL'] = 'en_US.UTF-8'

from django.core.wsgi import get_wsgi_application  # noqa
application = get_wsgi_application()
