from __future__ import absolute_import

import json

from celery import shared_task
from celery.utils.log import get_task_logger
from django.apps import apps

from .fetchers import pubmed

logger = get_task_logger(__name__)


@shared_task
def update_pubmed_content(ids):
    """
    For each pubmed_id, fetch the latest data from Pubmed, then parse and save
    the parsed data for each identifier. Next, update existing records in the
    database with the revised content.
    """
    Identifiers = apps.get_model('lit', 'identifiers')
    fetcher = pubmed.PubMedFetch(ids)
    contents = fetcher.get_content()
    for d in contents:
        Identifiers.objects\
            .filter(unique_id=d['PMID'], database=1)\
            .update(content=json.dumps(d, encoding='utf-8'))
