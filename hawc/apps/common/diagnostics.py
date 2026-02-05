from datetime import UTC, datetime, timedelta

import pandas as pd
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django_redis import get_redis_connection

from . import tasks


class IntentionalException(Exception):
    """
    An intentionally thrown exception, used for testing in various deployment environments.
    """

    pass


def diagnostic_500(modeladmin, request, queryset):
    message = f"User {request.user} intentionally threw a server error from the admin site."
    raise IntentionalException(message)


def diagnostic_task_test(modeladmin, request, queryset):
    result = tasks.diagnostic_task.enqueue(request.user.id)
    message = f"Task enqueued successfully with ID: {result.id}"
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


def clear_cache(modeladmin, request, queryset):
    cache.clear()
    message = "Cache cleared successfully"
    modeladmin.message_user(request, message)


def diagnostic_email(modeladmin, request, queryset):
    to_email = request.user.email
    send_mail(
        "Test email",
        "Test message",
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        fail_silently=False,
    )
    message = f"Attempted to send email to {to_email}"
    modeladmin.message_user(request, message)


class WorkerHealthcheck:
    KEY = "worker-healthcheck"
    MAX_SIZE = 60 * 24 // 5  # 1 day of data at a 5 minute-interval
    MAX_WAIT = timedelta(minutes=15)  # check is a failure if no task has run in X minutes

    def _get_conn(self):
        return get_redis_connection()

    def clear(self):
        """
        Clear worker healthcheck array
        """
        conn = self._get_conn()
        conn.delete(self.KEY)

    def push(self):
        """
        Push the latest successful time and trim the size of the array to max size
        """
        conn = self._get_conn()
        pipeline = conn.pipeline()
        pipeline.lpush(self.KEY, datetime.now(UTC).timestamp())
        pipeline.ltrim(self.KEY, 0, self.MAX_SIZE - 1)
        pipeline.execute()

    def healthy(self) -> bool:
        """Check if an item in the array has executed with the MAX_WAIT time from now"""
        conn = self._get_conn()
        last_push = conn.lindex(self.KEY, 0)
        if last_push is None:
            return False
        last_ping = datetime.fromtimestamp(float(last_push), UTC)
        return datetime.now(UTC) - last_ping < self.MAX_WAIT

    def series(self) -> pd.Series:
        """Return a pd.Series of last successful times"""
        conn = self._get_conn()
        data = conn.lrange(self.KEY, 0, -1)
        return pd.to_datetime(pd.Series(data, dtype=float), unit="s", utc=True)


worker_healthcheck = WorkerHealthcheck()


diagnostic_500.short_description = "Diagnostic server error (500)"
diagnostic_task_test.short_description = "Diagnostic task test"
diagnostic_cache.short_description = "Diagnostic cache test"
diagnostic_email.short_description = "Diagnostic email test"
