from celery import shared_task, Task
from celery.utils.log import get_task_logger
from django.apps import apps
from django.core.cache import cache

from ..common.dsstox import fetch_dsstox, get_cache_name
from ..common.svg import SVGConverter

logger = get_task_logger(__name__)


class JobTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):

        if kwargs.get("job"):
            from .models import Job

            job = Job.objects.get(task_id=task_id)
            # set status and exception
            job.status = Job.FAILURE
            job.exception = exc
            job.save()

    def on_retry(self, exc, task_id, args, kwargs, einfo):

        if kwargs.get("job"):
            from .models import Job

            job = Job.objects.get(task_id=task_id)
            # set status and exception
            job.status = Job.RETRY
            job.exception = exc
            job.save()

    def on_success(self, retval, task_id, args, kwargs):

        if kwargs.get("job"):
            from .models import Job

            job = Job.objects.get(task_id=task_id)
            # set status and result
            job.status = Job.SUCCESS
            job.result = retval
            job.save()


@shared_task(bind=True, base=JobTask)
def test_task(self, retry=False, fail=False, job=False):
    if retry:
        self.retry(exc=Exception("RETRY"), kwargs={"retry": False, "fail": fail, "job": job})
    if fail:
        raise Exception("FAILURE")
    return "SUCCESS"


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
def get_dsstox_details(casrn: str):
    cache_name = get_cache_name(casrn)
    result = fetch_dsstox(casrn)
    cache.set(cache_name, result, timeout=60 * 60 * 24)


@shared_task
def add_time_spent(cache_name, object_id, assessment_id, content_type_id):
    apps.get_model("assessment", "TimeSpentEditing").add_time_spent(
        cache_name, object_id, assessment_id, content_type_id
    )
