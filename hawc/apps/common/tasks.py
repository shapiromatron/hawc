from celery import task
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model
from django.utils import timezone

logger = get_task_logger(__name__)


@task
def diagnostic_celery_task(id_: str):
    user = get_user_model().objects.get(id=id_)
    logger.info(f"Diagnostic celery task triggered by: {user}")
    return dict(success=True, when=str(timezone.now()), user=user.email)


@task
def worker_healthcheck():
    from .diagnostics import worker_healthcheck

    worker_healthcheck.push()
