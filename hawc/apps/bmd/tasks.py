from celery import shared_task
from celery.utils.log import get_task_logger
from django.apps import apps

logger = get_task_logger(__name__)


@shared_task
def execute(session_id: int):
    logger.info(f"BMD execution -> {session_id}")
    session = apps.get_model("bmd", "Session").objects.get(id=session_id)
    session.execute()
