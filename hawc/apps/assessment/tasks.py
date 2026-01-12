import logging

from django.apps import apps
from django_tasks import task

logger = logging.getLogger(__name__)


@task
def delete_orphan_relations(delete: bool = False):
    # remove orphan relations in cases where the db cannot do so directly
    Log = apps.get_model("assessment", "Log")
    RiskOfBiasScoreOverrideObject = apps.get_model("riskofbias", "RiskOfBiasScoreOverrideObject")
    message = RiskOfBiasScoreOverrideObject.get_orphan_relations(delete=delete)
    if message:
        Log.objects.create(message=message)


@task
def add_time_spent(cache_name: str, object_id: int, assessment_id: int, content_type_id: int):
    apps.get_model("assessment", "TimeSpentEditing").add_time_spent(
        cache_name, object_id, assessment_id, content_type_id
    )
