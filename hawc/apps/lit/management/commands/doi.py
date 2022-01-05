from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction

from hawc.apps.assessment.models import Assessment
from hawc.apps.lit.constants import ReferenceDatabase, DOI_EXACT
from hawc.apps.lit.models import Identifiers, Reference
from hawc.services.utils.doi import get_doi_from_identifier, try_get_doi


class Command(BaseCommand):
    help = """Clean doi IDs and attempt to create doi ids for references without one"""

    def add_arguments(self, parser):
        parser.add_argument(
            "--assessment",
            type=int,
            help="Assessment ID to modify; defaults to all assessments",
            default=-1,
        )
        parser.add_argument(
            "--validate_existing",
            action="store_true",
            help="Validate existing DOIs; do not create new ones",
        )
        parser.add_argument(
            "--create_from_existing",
            action="store_true",
            help="Create DOIs from existing metadata",
        )
        parser.add_argument(
            "--full_text",
            action="store_true",
            help="Attempt to extract DOI ids from all content fields",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["assessment"] > 0:
            assessments = Assessment.objects.filter(id=options["assessment"])
        else:
            assessments = Assessment.objects.all().order_by("id")
        if options["validate_existing"]:
            for assessment in assessments:
                validate_existing(self.stdout, assessment)
        if options["create_from_existing"]:
            for assessment in assessments:
                create_from_existing(self.stdout, assessment, options["full_text"])


def validate_existing(logger, assessment):
    """Checks all existing doi IDs for valid doi ids, which are stored as a unique_id for doi identifiers
    Attempts to clean all the failing dois, merges duplicate doi IDs, and deletes invalid doi IDs that cannot be cleaned
    """
    doi_identifiers = Identifiers.objects.filter(
        database=ReferenceDatabase.DOI, references__assessment=assessment
    )
    n = doi_identifiers.count()
    logger.write(f"Assessment {assessment.id}; validating {n} DOIs")
    if n == 0:
        return

    existing_dois = {}
    doi_idents_updated = []
    # duplicate_doi_ids: stores unclean DOIs that have a clean duplicate for updating later
    duplicate_doi_ids = defaultdict(list)
    # invalid DOI IDs cannot be cleaned/validated (ex: '10')
    invalid_doi_idents = []

    # loop through once and add all valid dois to saved list to check for dupes as we go
    for ident in doi_identifiers.prefetch_related("references"):
        if DOI_EXACT.fullmatch(ident.unique_id):
            existing_dois[ident.unique_id] = ident
        else:
            doi = try_get_doi(ident.unique_id, full_text=True)
            if doi:
                if doi in existing_dois:
                    # DOI exists already; save identifier as a duplicate
                    duplicate_doi_ids[doi].append(ident)
                else:
                    # TODO - logic fails here; we need to query to check again to see if an existing doi exits. And, this gets more complicated, because we dont want to duplicates w/ the bulk_update
                    # DOI validation resulted in a new DOI
                    ident.unique_id = doi
                    doi_idents_updated.append(ident)
                    existing_dois[doi] = ident
            else:
                # DOI is invalid, save to be deleted below
                invalid_doi_idents.append(ident.id)

    logger.write(f"{len(existing_dois):8} DOI unchanged")

    # deleted
    logger.write(
        f"{len(doi_idents_updated):8} DOI deleted; invalid IDs -> {','.join(str(id) for id in invalid_doi_idents)}"
    )
    Identifiers.objects.filter(id__in=invalid_doi_idents).delete()

    # bulk-update new DOIs terms which need to be created
    Identifiers.objects.bulk_update(doi_idents_updated, ["unique_id"])
    logger.write(
        f"{len(doi_idents_updated):8} DOI updated; changed to valid DOI-> {','.join(str(doi_idents_updated.id) for id in doi_idents_updated)}"
    )

    # pull references with incorrect DOI id and replace that ID with the correct duplicate doi ID
    logger.write(f"{len(duplicate_doi_ids):8} DOI merged; duplicate DOI")
    creates = []
    deletes = []
    RefIdentM2M = Reference.identifiers.through
    for doi, old_identifiers in duplicate_doi_ids.items():
        new_identifier_id = existing_dois[doi].id
        for identifier in old_identifiers:
            for reference in identifier.references.all():
                creates.append(
                    RefIdentM2M(reference_id=reference.id, identifier_id=new_identifier_id)
                )
            deletes.append(identifier.id)

    RefIdentM2M.objects.bulk_create(creates)
    Identifiers.objects.filter(id__in=deletes).delete()


def create_from_existing(logger, full_text: bool):
    """Attempt to create new DOIs from existing reference identifier metadata

    Args:
        logger (file): A logger instance with the write method
        full_text (bool): use full text instad of structured content
    """
    qs_dois = Identifiers.objects.filter(database=ReferenceDatabase.DOI)
    qs_ref_with_doi = Reference.objects.filter(identifiers__database=ReferenceDatabase.DOI)
    qs_refs_without_doi = Reference.objects.exclude(identifiers__database=ReferenceDatabase.DOI)

    logger.write(f"Total DOI in HAWC: {qs_dois.count()}")
    logger.write(f"References with DOI: {qs_ref_with_doi.count()}")
    logger.write(f"References without DOI {qs_refs_without_doi.count()}")

    create_dois(logger, qs_refs_without_doi, full_text=full_text)

    logger.write(f"Total DOI in HAWC: {qs_dois.count()}")
    logger.write(f"References with DOI: {qs_ref_with_doi.count()}")
    logger.write(f"References without DOI {qs_refs_without_doi.count()}")


def create_dois(logger, refs, full_text: bool = False):
    """Attempt to find a DOI for each reference given other identifier metadata

    Args:
        logger (file): A logger instance with the write method
        refs (References): a list of references without doi identifiers
        full_text (bool, optional): Determines whether to search full text (True) of field (False; default)
    """
    n = refs.count()
    for i, ref in enumerate(refs.prefetch_related("identifiers")):
        if i % 1000 == 0:
            logger.write(f"Processing {i+1:10} of {n}")
        doi = None
        for ids in ref.identifiers.all():
            if full_text:
                doi = try_get_doi(ids.content, full_text=True)
            elif ids.content:
                doi = get_doi_from_identifier(ids)

            if doi:
                doi_identifier, _ = Identifiers.objects.get_or_create(
                    unique_id=doi, database=ReferenceDatabase.DOI
                )
                ref.identifiers.add(doi_identifier)
                break
