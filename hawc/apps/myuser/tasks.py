from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone

from .models import HAWCUser

logger = get_task_logger(__name__)


@shared_task
def diagnostic_celery_task(user_id):
    user = HAWCUser.objects.get(id=user_id)
    logger.info(f"Diagnostic celery task triggered by: {user}")
    return dict(success=True, when=str(timezone.now()), user=user.get_full_name())
