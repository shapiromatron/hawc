import json
from typing import List

from celery import shared_task
from celery.utils.log import get_task_logger
from django.apps import apps
from django.db.models import F
from django.db.models.aggregates import Count, Max
from django.utils import timezone
from litter_getter import hero, pubmed

from . import constants

logger = get_task_logger(__name__)


@shared_task
def update_hero_content(ids: List[int]):
    """Fetch the latest data from HERO and update identifier object."""

    Identifiers = apps.get_model("lit", "identifiers")

    fetcher = hero.HEROFetch(ids)
    contents = fetcher.get_content()
    for d in contents.get("success"):

        content = json.dumps(d)
        Identifiers.objects.filter(unique_id=str(d["HEROID"]), database=constants.HERO).update(
            content=content
        )
    ids_str = [str(id) for id in ids]
    Identifiers.objects.filter(unique_id__in=ids_str, database=constants.HERO, content="").update(
        content='{"status": "failed"}'
    )


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


@shared_task
def fix_pubmed_without_content():
    # Try getting pubmed data without content
    Identifiers = apps.get_model("lit", "identifiers")
    ids = Identifiers.objects.filter(content="", database=constants.PUBMED)
    num_ids = ids.count()
    logger.info(f"Attempting to update pubmed content for {num_ids} identifiers")
    if num_ids > 0:
        Identifiers.update_pubmed_content(ids)


@shared_task
def schedule_topic_model_reruns():
    # schedule which topic models which require a refresh
    LiteratureAssessment = apps.get_model("lit", "LiteratureAssessment")

    # if topic model doesn't exist have a model with minimum references
    qs1 = (
        LiteratureAssessment.objects.filter(
            topic_tsne_refresh_requested__isnull=True, topic_tsne_last_refresh__isnull=True
        )
        .annotate(num_refs=Count("assessment__references"))
        .filter(num_refs__gte=LiteratureAssessment.TOPIC_MODEL_MIN_REFERENCES)
    )
    logger.info(f"Scheduling {qs1.count()} new assessments for topic modeling")

    # if model execution datetime < max(reference.last_updated)
    qs2 = (
        LiteratureAssessment.objects.filter(topic_tsne_last_refresh__isnull=False)
        .annotate(ref_last_updated=Max("assessment__references__last_updated"))
        .filter(topic_tsne_last_refresh__lte=F("ref_last_updated"))
    )
    logger.info(f"Scheduling {qs2.count()} assessments for topic modeling refresh")

    # schedule refreshes
    qs1.update(topic_tsne_refresh_requested=timezone.now())
    qs2.update(topic_tsne_refresh_requested=timezone.now())

    qs = LiteratureAssessment.objects.filter(topic_tsne_refresh_requested__isnull=False)
    logger.info(f"Scheduling {qs.count()} assessments for topic model rerun")
    for settings in qs:
        rerun_topic_model.apply_async((settings.assessment_id,), ignore_result=True)

    logger.info("Task complete.")


@shared_task
def rerun_topic_model(assessment_id):
    logger.info(f"Topic model rerun reqest scheduled for assessment {assessment_id}")

    # rerun a topic model
    LiteratureAssessment = apps.get_model("lit", "LiteratureAssessment")
    settings = LiteratureAssessment.objects.get(assessment_id=assessment_id)

    if (
        settings.topic_tsne_last_refresh is not None
        and settings.topic_tsne_last_refresh > settings.topic_tsne_refresh_requested
    ):
        logger.info(f"Refresh for {settings.assessment_id} cancelled; data is up to date.")
        settings.topic_tsne_refresh_requested = None
        settings.save()
        return

    if settings.assessment.references.count() < LiteratureAssessment.TOPIC_MODEL_MIN_REFERENCES:
        logger.info(f"Refresh for {settings.assessment_id} cancelled; not enough references")
        settings.topic_tsne_data = None
        settings.topic_tsne_refresh_requested = None
        settings.save()
        return

    # otherwise re-run model
    logger.info(f"Updating {settings.assessment_id} topic model")
    settings.create_topic_tsne_data()
    logger.info("Task complete.")
