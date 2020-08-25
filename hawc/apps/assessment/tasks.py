from celery import shared_task
from celery.utils.log import get_task_logger
from django.apps import apps
from django.core.cache import cache

from ..common.dsstox import fetch_dsstox, get_cache_name
from ..common.svg import SVGConverter
from . import models

logger = get_task_logger(__name__)


@shared_task(bind=True)
def run_job(self):
    job = models.Job.objects.get(pk=self.request.id)
    try:
        result = job.get_func()(**job.kwargs)
        job.set_result(result)
    except Exception as exc:
        job.set_exception(exc)


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
