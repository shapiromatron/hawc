from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail

from . import tasks


class IntentionalException(Exception):
    """
    An intentionally thrown exception, used for testing in various deployment environments.
    """

    pass


def diagnostic_500(modeladmin, request, queryset):
    message = f"User {request.user} intentionally threw a server error from the admin site."
    raise IntentionalException(message)


def diagnostic_celery_task(modeladmin, request, queryset):
    response = tasks.diagnostic_celery_task.delay(request.user.id).get()
    message = f"Celery task executed successfully: {response}"
    modeladmin.message_user(request, message)


def diagnostic_cache(modeladmin, request, queryset):
    cache.set("foo", "bar")
    if cache.get("foo") != "bar":
        raise RuntimeError("Cache did not successfully set variable.")

    cache.delete("foo")
    if cache.get("foo") is not None:
        raise RuntimeError("Cache did not successfully delete variable.")

    message = "Cache test executed successfully"
    modeladmin.message_user(request, message)


def diagnostic_email(modeladmin, request, queryset):
    to_email = request.user.email
    send_mail(
        "Test email", "Test message", settings.DEFAULT_FROM_EMAIL, [to_email], fail_silently=False,
    )

    message = f"Attempted to send email to {to_email}"
    modeladmin.message_user(request, message)


diagnostic_500.short_description = "Diagnostic server error (500)"
diagnostic_celery_task.short_description = "Diagnostic celery task test"
diagnostic_cache.short_description = "Diagnostic cache test"
diagnostic_email.short_description = "Diagnostic email test"
