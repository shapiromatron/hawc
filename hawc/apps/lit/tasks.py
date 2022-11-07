import json

from celery import shared_task
from celery.utils.log import get_task_logger
from django.apps import apps
from django.db import transaction
from django.db.models import F, Model
from django.db.models.aggregates import Count, Max
from django.utils import timezone

from ...services.epa import hero
from ...services.nih import pubmed
from . import constants

logger = get_task_logger(__name__)


@shared_task
def update_hero_content(ids: list[int]):
    """Fetch the latest data from HERO and update identifier object."""

    Identifiers = apps.get_model("lit", "identifiers")

    fetcher = hero.HEROFetch(sorted(ids))
    contents = fetcher.get_content()
    with transaction.atomic():
        for d in contents.get("success"):
            content = json.dumps(d)
            Identifiers.objects.filter(
                unique_id=str(d["HEROID"]), database=constants.ReferenceDatabase.HERO
            ).update(content=content)
        ids_str = [str(id) for id in ids]
        Identifiers.objects.filter(
            unique_id__in=ids_str, database=constants.ReferenceDatabase.HERO, content=""
        ).update(content='{"status": "failed"}')


@shared_task
def update_hero_fields(ref_ids: list[int]):
    """
    Updates the reference fields with most recent content from HERO

    Args:
        ref_ids (list[int]): List of references IDs to update
    """

    Reference = apps.get_model("lit", "reference")
    with transaction.atomic():
        references = Reference.objects.filter(id__in=ref_ids).prefetch_related("identifiers")
        for reference in references:
            content = reference.identifiers.get(
                database=constants.ReferenceDatabase.HERO
            ).get_content()
            reference.update_from_hero_content(content, save=True)


@shared_task
def replace_hero_ids(replace: list[list[int]]):
    """
    Replace the identifier on each reference with the given HERO ID

    Args:
        replace (list[list[int]]): List of reference ID / HERO ID pairings
    """
    Reference = apps.get_model("lit", "reference")
    Identifiers = apps.get_model("lit", "identifiers")

    # build map of HERO ID -> Identifier.id
    ref_ids, new_hero_ids = zip(*replace)
    identifier_map: dict[int, int] = {
        int(ident.unique_id): ident.id
        for ident in Identifiers.objects.filter(
            database=constants.ReferenceDatabase.HERO, unique_id__in=new_hero_ids
        )
    }
    if len(identifier_map) != len(new_hero_ids):
        raise ValueError("Identifiers map length != HERO ID length length")

    # build map of reference.id -> reference object
    reference_map: dict[int, Model] = {
        ref.id: ref
        for ref in Reference.objects.filter(id__in=ref_ids).prefetch_related("identifiers")
    }
    if len(reference_map) != len(ref_ids):
        raise ValueError("Reference map length != reference ID list length")

    # update identifier references to substitute old HERO id for new HERO id
    with transaction.atomic():
        for ref_id, hero_id in replace:
            reference = reference_map[ref_id]
            identifier_ids = [
                ident.id
                for ident in reference.identifiers.all()
                if ident.database != constants.ReferenceDatabase.HERO
            ]
            identifier_ids.append(identifier_map[hero_id])
            reference.identifiers.set(identifier_ids)


@shared_task
def update_pubmed_content(ids: list[int]):
    """Fetch the latest data from Pubmed and update identifier object."""
    Identifiers = apps.get_model("lit", "identifiers")
    fetcher = pubmed.PubMedFetch(ids)
    contents = fetcher.get_content()
    for d in contents:
        content = json.dumps(d)
        Identifiers.objects.filter(
            unique_id=str(d["PMID"]), database=constants.ReferenceDatabase.PUBMED
        ).update(content=content)
    ids_str = [str(id) for id in ids]
    Identifiers.objects.filter(
        unique_id__in=ids_str, database=constants.ReferenceDatabase.PUBMED, content=""
    ).update(content='{"status": "failed"}')


@shared_task
def fix_pubmed_without_content():
    # Try getting pubmed data without content
    Identifiers = apps.get_model("lit", "identifiers")
    ids = Identifiers.objects.filter(content="", database=constants.ReferenceDatabase.PUBMED)
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

    # if model execution datetime < max(reference.last_updated), and has minimum references
    qs2 = (
        LiteratureAssessment.objects.filter(topic_tsne_last_refresh__isnull=False)
        .annotate(ref_last_updated=Max("assessment__references__last_updated"))
        .filter(topic_tsne_last_refresh__lte=F("ref_last_updated"))
        .annotate(num_refs=Count("assessment__references"))
        .filter(num_refs__gte=LiteratureAssessment.TOPIC_MODEL_MIN_REFERENCES)
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
def rerun_topic_model(assessment_id: int):
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
