# flake8: noqa

import json
import os

from ... import __version__
from .base import *

SERVER_ROLE = os.environ.get("HAWC_SERVER_ROLE", "staging")
SERVER_BANNER_COLOR = os.environ.get("HAWC_SERVER_BANNER_COLOR", "#EE8416")

HTTPS_ONLY = bool(os.environ.get("DJANGO_HTTPS_ONLY") == "True")
SESSION_COOKIE_SECURE = HTTPS_ONLY
CSRF_COOKIE_SECURE = HTTPS_ONLY
SECURE_SSL_REDIRECT = HTTPS_ONLY
if HTTPS_ONLY:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_HSTS_SECONDS = 0  # handle upstream in reverse proxy

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "").split("|")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

email_backend = os.environ["DJANGO_EMAIL_BACKEND"]
EMAIL_MESSAGEID_FQDN = None
if email_backend == "SMTP":
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.environ.get("DJANGO_EMAIL_HOST", None)
    EMAIL_HOST_USER = os.environ.get("DJANGO_EMAIL_USER", None)
    EMAIL_HOST_PASSWORD = os.environ.get("DJANGO_EMAIL_PASSWORD", None)
    EMAIL_PORT = int(os.environ.get("DJANGO_EMAIL_PORT", 25))
    EMAIL_USE_SSL = bool(os.environ.get("DJANGO_EMAIL_USE_SSL") == "True")
    EMAIL_MESSAGEID_FQDN = os.environ.get("DJANGO_EMAIL_MESSAGEID_FQDN")
elif email_backend == "MAILGUN":
    INSTALLED_APPS += ("anymail",)
    EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
    ANYMAIL = dict(
        MAILGUN_API_KEY=os.environ["MAILGUN_ACCESS_KEY"],
        MAILGUN_SENDER_DOMAIN=os.environ["MAILGUN_SERVER_NAME"],
    )
elif email_backend == "SENDGRID":
    INSTALLED_APPS += ("anymail",)
    EMAIL_BACKEND = "anymail.backends.sendgrid.EmailBackend"
    ANYMAIL = dict(
        SENDGRID_API_KEY=os.environ["SENDGRID_API_KEY"],
    )
elif email_backend == "CONSOLE":
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    raise ValueError(f"Unknown email backend: {email_backend}")

LOGGING["loggers"]["django"]["handlers"] = ["console", "file"]
LOGGING["loggers"]["hawc"]["handlers"] = ["console", "file"]
LOGGING["loggers"]["hawc.request"]["handlers"] = ["console", "hawc-request"]

ANYONE_CAN_CREATE_ASSESSMENTS = os.getenv("HAWC_ANYONE_CAN_CREATE_ASSESSMENTS", "True") == "True"
PM_CAN_MAKE_PUBLIC = os.getenv("HAWC_PM_CAN_MAKE_PUBLIC", "True") == "True"
ACCEPT_LICENSE_REQUIRED = os.getenv("HAWC_ACCEPT_LICENSE_REQUIRED", "True") == "True"

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = ("rest_framework.renderers.JSONRenderer",)

HAWC_LOAD_TEST_DB = int(os.environ.get("HAWC_LOAD_TEST_DB", 0))  # 0 = no; 1 = yes
if HAWC_LOAD_TEST_DB:
    PASSWORD_HASHERS = ("django.contrib.auth.hashers.MD5PasswordHasher",)
    TEST_DB_FIXTURE = "/app/test-db-fixture.yaml"


if email_backend == "SMTP" and EMAIL_MESSAGEID_FQDN is not None:
    """
    Monkey-patch the FQDN for SMTP to our desired name; by default picks up container ID
    Can be removed if this PR is merged:
    - https://code.djangoproject.com/ticket/6989
    - https://github.com/django/django/pull/13728/files
    """
    from django.core.mail.utils import DNS_NAME

    DNS_NAME._fqdn = EMAIL_MESSAGEID_FQDN

if SENTRY_DSN := os.environ.get("HAWC_SENTRY_DSN"):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    SENTRY_SETTINGS = json.loads(
        os.environ.get(
            "HAWC_SENTRY_SETTINGS", '{"traces_sample_rate": 1.0, "send_default_pii": false}'
        )
    )
    release = COMMIT.sha if "undefined" not in COMMIT.sha else __version__
    SENTRY_SETTINGS.setdefault("release", release)
    sentry_sdk.init(dsn=SENTRY_DSN, integrations=[DjangoIntegration()], **SENTRY_SETTINGS)
