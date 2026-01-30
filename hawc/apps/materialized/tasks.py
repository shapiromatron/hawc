from django_tasks import task

from . import models


@task
def refresh_all_mvs(force: bool = False):
    models.refresh_all_mvs(force)
