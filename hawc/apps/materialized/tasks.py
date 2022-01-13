from celery import shared_task

from . import models


@shared_task
def refresh_all_mvs(force: bool = False):
    models.refresh_all_mvs(force)
