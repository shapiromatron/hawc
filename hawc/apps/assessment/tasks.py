from celery import shared_task
from celery.utils.log import get_task_logger
from django.apps import apps
from django.core.cache import cache

from ..common.dsstox import fetch_dsstox
from ..common.svg import SVGConverter

logger = get_task_logger(__name__)


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
def get_dsstox_details(cas_number):
    cache_name = f"dsstox-{cas_number.replace(' ', '_')}"
    d = cache.get(cache_name)
    if d is None:
        d = {"status": "failure"}
        if cas_number:
            d = fetch_dsstox(cas_number)
            if d.get("status") == "success":
                logger.info(f"setting cache: {cache_name}")
                cache.set(cache_name, d)
    return d


@shared_task
def add_time_spent(cache_name, object_id, assessment_id, content_type_id):
    apps.get_model("assessment", "TimeSpentEditing").add_time_spent(
        cache_name, object_id, assessment_id, content_type_id
    )
