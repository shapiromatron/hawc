import os

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
