import os

from django.core.wsgi import get_wsgi_application  # noqa

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hawc.main.settings.dev")
os.environ["LC_ALL"] = "en_US.UTF-8"


application = get_wsgi_application()
