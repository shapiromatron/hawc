from celery import shared_task
from celery.utils.log import get_task_logger
from django.apps import apps

logger = get_task_logger(__name__)


@shared_task
def delete_orphan_relations(delete: bool = False):
    # remove orphan relations in cases where the db cannot do so directly
    Log = apps.get_model("assessment", "Log")
    RiskOfBiasScoreOverrideObject = apps.get_model("riskofbias", "RiskOfBiasScoreOverrideObject")
    message = RiskOfBiasScoreOverrideObject.get_orphan_relations(delete=delete)
    if message:
        Log.objects.create(message=message)


@shared_task
def add_time_spent(cache_name: str, object_id: int, assessment_id: int, content_type_id: int):
    apps.get_model("assessment", "TimeSpentEditing").add_time_spent(
        cache_name, object_id, assessment_id, content_type_id
    )
