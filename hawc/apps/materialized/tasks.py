from celery import shared_task

from . import models


@shared_task
def refresh_views_by_cache():
    models.FinalRiskOfBiasScore.refresh_view_by_cache()
