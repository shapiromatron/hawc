from datetime import timedelta

from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from rest_framework.authtoken.models import Token

from ...services.utils.rasterize import SVGConverter

logger = get_task_logger(__name__)


@shared_task
def diagnostic_celery_task(id_: str):
    user = get_user_model().objects.get(id=id_)
    logger.info(f"Diagnostic celery task triggered by: {user}")
    return dict(success=True, when=str(now()), user=user.email)


@shared_task
def worker_healthcheck():
    from .diagnostics import worker_healthcheck

    worker_healthcheck.push()


@shared_task
def destroy_old_api_tokens():
    deletion_date = now() - timedelta(seconds=settings.SESSION_COOKIE_AGE)
    qs = Token.objects.filter(created__lt=deletion_date)
    logger.info(f"Destroying {qs.count()} old tokens")
    qs.delete()


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
