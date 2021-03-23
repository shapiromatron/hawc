from celery import shared_task

from . import models


def refresh_view_by_cache(cls):
    if cls.get_refresh_view_cache():
        cls.refresh_view()
        cls.set_refresh_view_cache(False)


@shared_task
def refresh_views_by_cache():
    refresh_view_by_cache(models.Score)
