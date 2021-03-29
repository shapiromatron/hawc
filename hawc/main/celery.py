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
    print(f"Request: {self.request!r}")


app.conf.beat_schedule = {
    "lit-schedule_topic_model_reruns-10-min": {
        "task": "hawc.apps.lit.tasks.schedule_topic_model_reruns",
        "schedule": timedelta(minutes=10),
    },
    "lit-update_pubmed_content-1-day": {
        "task": "hawc.apps.lit.tasks.update_pubmed_content",
        "schedule": timedelta(days=1),
    },
    "assessment-delete_old_jobs-1-day": {
        "task": "hawc.apps.assessment.tasks.delete_old_jobs",
        "schedule": timedelta(days=1),
    },
    "delete-orphan-relations": {
        "task": "hawc.apps.assessment.tasks.delete_orphan_relations",
        "schedule": timedelta(hours=6),
        "kwargs": dict(delete=False),
    },
    "refresh_all_mvs": {
        "task": "hawc.apps.materialized.tasks.refresh_all_mvs",
        "schedule": timedelta(minutes=5),
    },
}

# optional; only if service is available and service is real
has_bmds_service_url = "example" not in os.environ.get("BMDS_SUBMISSION_URL", "example")
if has_bmds_service_url:
    app.conf.beat_schedule["bmds2-healthcheck"] = {
        "task": "hawc.apps.bmd.tasks.bmds2_healthcheck",
        "schedule": timedelta(hours=12),
    }
