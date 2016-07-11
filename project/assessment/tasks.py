from __future__ import absolute_import

from django.core.cache import cache

from celery import shared_task
from celery.utils.log import get_task_logger

from utils.chemspider import fetch_chemspider
from utils.svg import SVGConverter


logger = get_task_logger(__name__)


@shared_task
def convert_to_svg(svg, url, width, height):
    logger.info('Converting svg -> [css]+svg')
    conv = SVGConverter(svg, url, width, height)
    return conv.to_svg()


@shared_task
def convert_to_png(svg, url, width, height):
    logger.info('Converting svg -> html -> png')
    conv = SVGConverter(svg, url, width, height)
    return conv.to_png()


@shared_task
def convert_to_pdf(svg, url, width, height):
    logger.info('Converting svg -> html -> pdf')
    conv = SVGConverter(svg, url, width, height)
    return conv.to_pdf()


@shared_task
def convert_to_pptx(svg, url, width, height):
    logger.info('Converting svg -> html -> png -> pptx')
    conv = SVGConverter(svg, url, width, height)
    return conv.to_pptx()


@shared_task
def get_chemspider_details(cas_number):
    cache_name = 'chemspider-{}'.format(cas_number.replace(' ', '_'))
    d = cache.get(cache_name)
    if d is None:
        d = {"status": "failure"}
        if cas_number:
            d = fetch_chemspider(cas_number)
            if d['status'] == 'success':
                logger.info('setting cache: {}'.format(cache_name))
                cache.set(cache_name, d)
    return d
