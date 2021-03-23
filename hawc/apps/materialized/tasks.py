from celery import shared_task

from . import models


@shared_task
def refresh_score_view():
    if models.Score.get_refresh_cache():
        models.Score.refresh_view()
        models.Score.set_refresh_cache(False)
