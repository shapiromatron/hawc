import os
from datetime import timedelta

from celery import Celery
from celery.utils.log import get_task_logger

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hawc.main.settings.dev")
logger = get_task_logger(__name__)
app = Celery("hawc")

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    logger.info("Running the debug_task task.")


app.conf.beat_schedule = {
    "worker-healthcheck": {
        "task": "hawc.apps.common.tasks.worker_healthcheck",
        "schedule": timedelta(minutes=5),
        "options": {"expires": timedelta(minutes=5).total_seconds()},
    },
    "destroy-api-tokens": {
        "task": "hawc.apps.common.tasks.destroy_old_api_tokens",
        "schedule": timedelta(minutes=10),
        "options": {"expires": timedelta(minutes=10).total_seconds()},
    },
    "create-initial-revisions": {
        "task": "hawc.apps.common.tasks.create_initial_revisions",
        "schedule": timedelta(days=1),
        "options": {"expires": timedelta(days=1).total_seconds()},
    },
    "lit-update_pubmed_content-1-day": {
        "task": "hawc.apps.lit.tasks.update_pubmed_content",
        "schedule": timedelta(days=1),
        "options": {"expires": timedelta(days=1).total_seconds()},
    },
    "assessment-delete_old_jobs-1-day": {
        "task": "hawc.apps.assessment.tasks.delete_old_jobs",
        "schedule": timedelta(days=1),
        "options": {"expires": timedelta(days=1).total_seconds()},
    },
    "delete-orphan-relations": {
        "task": "hawc.apps.assessment.tasks.delete_orphan_relations",
        "schedule": timedelta(hours=6),
        "kwargs": dict(delete=False),
        "options": {"expires": timedelta(hours=6).total_seconds()},
    },
    "check-refresh-mvs": {
        "task": "hawc.apps.materialized.tasks.refresh_all_mvs",
        "schedule": timedelta(minutes=5),
        "options": {"expires": timedelta(minutes=5).total_seconds()},
    },
    "refresh-mvs": {
        "task": "hawc.apps.materialized.tasks.refresh_all_mvs",
        "schedule": timedelta(days=1),
        "kwargs": dict(force=True),
        "options": {"expires": timedelta(days=1).total_seconds()},
    },
}
