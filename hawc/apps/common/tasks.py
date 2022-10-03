from datetime import timedelta

from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.utils.timezone import now
from rest_framework.authtoken.models import Token

logger = get_task_logger(__name__)


@shared_task
def diagnostic_celery_task(id_: str):
    user = get_user_model().objects.get(id=id_)
    logger.info(f"Diagnostic celery task triggered by: {user}")
    return dict(success=True, when=str(now()), user=user.email)


@shared_task
def worker_healthcheck():
    from .diagnostics import worker_healthcheck

    worker_healthcheck.push()


@shared_task
def destroy_old_api_tokens():
    deletion_date = now() - timedelta(seconds=settings.SESSION_COOKIE_AGE)
    qs = Token.objects.filter(created__lt=deletion_date)
    logger.info(f"Destroying {qs.count()} old tokens")
    qs.delete()


@shared_task
def create_initial_revisions():
    """
    Most apis/views should create initial revisions; however if we're importing data from
    other non-standard sources and we may have missed the initial revision, this task will ensure
    that the revision has been created. We would lose the user who created it, but this is our
    best effort as a fallback mechanism.
    """
    call_command("createinitialrevisions", "reversion")
