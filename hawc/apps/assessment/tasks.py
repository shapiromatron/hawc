from datetime import timedelta

from celery import shared_task
from celery.utils.log import get_task_logger
from django.apps import apps
from django.utils import timezone

from ..common.svg import SVGConverter
from . import models

logger = get_task_logger(__name__)


@shared_task
def delete_old_jobs():
    # delete jobs where "last_updated" > 1 week old
    week_old = timezone.now() - timedelta(weeks=1)
    models.Job.objects.filter(last_updated__lte=week_old).delete()


@shared_task
def delete_orphan_relations(delete: bool = False):
    # remove orphan relations in cases where the db cannot do so directly
    Log = apps.get_model("assessment", "Log")
    RiskOfBiasScoreOverrideObject = apps.get_model("riskofbias", "RiskOfBiasScoreOverrideObject")
    message = RiskOfBiasScoreOverrideObject.get_orphan_relations(delete=delete)
    if message:
        Log.objects.create(message=message)


@shared_task(bind=True)
def run_job(self):
    job = models.Job.objects.get(pk=self.request.id)
    try:
        result = job.execute()
        job.set_success(result)
    except Exception as exc:
        job.set_failure(exc)
    job.save()


@shared_task
def convert_to_svg(svg, url, width, height):
    logger.info("Converting svg -> [css]+svg")
    conv = SVGConverter(svg, url, width, height)
    return conv.to_svg()


@shared_task
def convert_to_png(svg, url, width, height):
    logger.info("Converting svg -> html -> png")
    conv = SVGConverter(svg, url, width, height)
    return conv.to_png()


@shared_task
def convert_to_pdf(svg, url, width, height):
    logger.info("Converting svg -> html -> pdf")
    conv = SVGConverter(svg, url, width, height)
    return conv.to_pdf()


@shared_task
def convert_to_pptx(svg, url, width, height):
    logger.info("Converting svg -> html -> png -> pptx")
    conv = SVGConverter(svg, url, width, height)
    return conv.to_pptx()


@shared_task
def add_time_spent(cache_name, object_id, assessment_id, content_type_id):
    apps.get_model("assessment", "TimeSpentEditing").add_time_spent(
        cache_name, object_id, assessment_id, content_type_id
    )
