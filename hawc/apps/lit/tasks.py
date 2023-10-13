import json

from celery import shared_task
from celery.utils.log import get_task_logger
from django.apps import apps
from django.db import transaction
from django.db.models import Model

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
    Identifiers = apps.get_model("lit", "identifiers")
    with transaction.atomic():
        references = Reference.objects.filter(id__in=ref_ids).prefetch_related("identifiers")
        hero_identifiers = Identifiers.objects.filter(
            database=constants.ReferenceDatabase.HERO, references__in=ref_ids
        )
        doi_map = hero_identifiers.associated_doi(create=True)
        pubmed_map = hero_identifiers.associated_pubmed(create=True)

        for reference in references:
            hero_identifier = reference.identifiers.get(database=constants.ReferenceDatabase.HERO)

            # update reference fields
            content = hero_identifier.get_content()
            reference.update_from_hero_content(content, save=True)

            # update reference identifiers
            reference.identifiers.set(
                [
                    identifier
                    for identifier in [
                        hero_identifier,
                        doi_map.get(hero_identifier),
                        pubmed_map.get(hero_identifier),
                    ]
                    if identifier
                ]
            )


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
    ref_ids, new_hero_ids = zip(*replace, strict=True)
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
