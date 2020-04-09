import json
from datetime import timedelta
from typing import List

from celery import shared_task
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger
from django.apps import apps
from django.db.models import F
from django.db.models.aggregates import Max, Count
from django.utils import timezone
from litter_getter import pubmed

from . import constants


logger = get_task_logger(__name__)


@shared_task
def update_pubmed_content(ids: List[int]):
    """Fetch the latest data from Pubmed and update identifier object."""
    Identifiers = apps.get_model("lit", "identifiers")
    fetcher = pubmed.PubMedFetch(ids)
    contents = fetcher.get_content()
    for d in contents:
        content = json.dumps(d)
        Identifiers.objects.filter(unique_id=str(d["PMID"]), database=constants.PUBMED).update(
            content=content
        )
    ids_str = [str(id) for id in ids]
    Identifiers.objects.filter(unique_id__in=ids_str, database=constants.PUBMED, content="").update(
        content='{"status": "failed"}'
    )


@periodic_task(run_every=timedelta(hours=1))
def fix_pubmed_without_content():
    # Try getting pubmed data without content
    Identifiers = apps.get_model("lit", "identifiers")
    ids = Identifiers.objects.filter(content="", database=constants.PUBMED)
    Identifiers.update_pubmed_content(ids)


@periodic_task(run_every=timedelta(hours=1))
def schedule_topic_model_reruns():
    # schedule which topic models which require a refresh
    LiteratureAssessment = apps.get_model("lit", "LiteratureAssessment")

    # if topic model doesn't exist have a model with minimum references
    qs1 = (
        LiteratureAssessment.objects.filter(topic_tsne_last_refresh__isnull=True)
        .annotate(num_refs=Count("assessment__references"))
        .filter(num_refs__gte=LiteratureAssessment.TOPIC_MODEL_MIN_REFERENCES)
    )

    # if model execution datetime < max(reference.last_updated)
    qs2 = (
        LiteratureAssessment.objects.filter(topic_tsne_last_refresh__isnull=False)
        .annotate(ref_last_updated=Max("assessment__references__last_updated"))
        .filter(topic_tsne_last_refresh__lte=F("ref_last_updated"))
    )

    # schedule refreshes
    qs1.union(qs2).update(topic_tsne_refresh_requested=timezone.now())

    # schedule rerun
    for settings in LiteratureAssessment.objects.filter(
        topic_tsne_refresh_requested__not_null=True
    ):
        rerun_topic_model.apply_async((settings.assessment_id,), ignore_result=True)


@shared_task
def rerun_topic_model(assessment_id):
    # rerun a topic model
    LiteratureAssessment = apps.get_model("lit", "LiteratureAssessment")
    settings = LiteratureAssessment.objects.get(assessment_id=assessment_id)

    # exit early conditions w/o re-running model:
    # 1) if the model has been updated after the refresh request (duplicate tasks on queue?)
    # 2) if there aren't enough references
    if settings.topic_tsne_last_refresh > settings.topic_tsne_refresh_requested:
        settings.topic_tsne_refresh_requested = None
        settings.save()
        return

    if settings.assessment.references.count() < LiteratureAssessment.TOPIC_MODEL_MIN_REFERENCES:
        settings.topic_tsne_data = None
        settings.topic_tsne_refresh_requested = None
        settings.save()
        return

    # otherwise re-run model
    settings.create_topic_tsne_data()
