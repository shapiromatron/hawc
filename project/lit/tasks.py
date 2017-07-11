

from datetime import timedelta
import json

from celery import shared_task
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger
from django.apps import apps

from litter_getter import pubmed

from . import constants


logger = get_task_logger(__name__)


@shared_task
def update_pubmed_content(ids):
    """Fetch the latest data from Pubmed and update identifier object."""
    Identifiers = apps.get_model('lit', 'identifiers')
    fetcher = pubmed.PubMedFetch(ids)
    contents = fetcher.get_content()
    for d in contents:
        content = json.dumps(d)
        Identifiers.objects\
            .filter(
                unique_id=d['PMID'],
                database=constants.PUBMED
            )\
            .update(content=content)


@periodic_task(run_every=timedelta(hours=1))
def fix_pubmed_without_content():
    # Try getting pubmed data without content
    Identifiers = apps.get_model('lit', 'identifiers')
    ids = Identifiers.objects.filter(content='None', database=constants.PUBMED)
    Identifiers.update_pubmed_content(ids)
