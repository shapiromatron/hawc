from __future__ import absolute_import

from celery import Celery
from celery.utils.log import get_task_logger

from django.conf import settings


logger = get_task_logger(__name__)
app = Celery('hawc')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    logger.info('Running the debug_task task.')
    print('Request: {0!r}'.format(self.request))
