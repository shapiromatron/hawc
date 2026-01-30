import logging

from django.apps import apps
from django_tasks import task

logger = logging.getLogger(__name__)


@task
def execute(session_id: int):
    logger.info(f"BMD execution -> {session_id}")
    session = apps.get_model("bmd", "Session").objects.get(id=session_id)
    session.execute()
