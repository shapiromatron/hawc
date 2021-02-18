# flake8: noqa

import os

from .base import *

EXTRA_BRANDING = os.getenv("HAWC_EXTRA_BRANDING", "True") == "True"

SERVER_ROLE = "staging"
SERVER_BANNER_COLOR = "#EE8416"

SESSION_COOKIE_SECURE = bool(os.environ.get("DJANGO_HTTPS_ONLY") == "True")
CSRF_COOKIE_SECURE = bool(os.environ.get("DJANGO_HTTPS_ONLY") == "True")

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "").split("|")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

if os.environ.get("DJANGO_EMAIL_BACKEND") == "SMTP":
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.environ.get("DJANGO_EMAIL_HOST", None)
    EMAIL_HOST_USER = os.environ.get("DJANGO_EMAIL_USER", None)
    EMAIL_HOST_PASSWORD = os.environ.get("DJANGO_EMAIL_PASSWORD", None)
    EMAIL_PORT = int(os.environ.get("DJANGO_EMAIL_PORT", 25))
    EMAIL_USE_SSL = bool(os.environ.get("DJANGO_EMAIL_USE_SSL") == "True")
elif os.environ.get("DJANGO_EMAIL_BACKEND") == "MAILGUN":
    INSTALLED_APPS += ("anymail",)
    EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
    ANYMAIL = dict(
        MAILGUN_API_KEY=os.environ["MAILGUN_ACCESS_KEY"],
        MAILGUN_SENDER_DOMAIN=os.environ["MAILGUN_SERVER_NAME"],
    )
else:
    raise ValueError("Unknown email backend")

LOGGING["loggers"]["django"]["handlers"] = ["file"]

ANYONE_CAN_CREATE_ASSESSMENTS = os.getenv("HAWC_ANYONE_CAN_CREATE_ASSESSMENTS", "True") == "True"
