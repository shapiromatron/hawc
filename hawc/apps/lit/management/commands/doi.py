from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Prefetch

from .....services.utils.doi import try_get_doi
from ....assessment.models import Assessment
from ....lit.constants import DOI_EXACT, ReferenceDatabase
from ....lit.models import Identifiers, Reference


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
            validate_existing(self.stdout)
        if options["create_from_existing"]:
            for assessment in assessments:
                self.stdout.write(f"Reviewing references in {assessment.id}: {assessment}")
                qs = Reference.objects.filter(assessment=assessment)
                Reference.extract_dois(qs, self.stdout, options["full_text"])


def validate_existing(logger):
    """Checks all existing doi IDs for valid doi ids, which are stored as a unique_id for doi identifiers
    Attempts to clean all the failing dois, merges duplicate doi IDs, and deletes invalid doi IDs that cannot be cleaned
    """
    doi_identifiers = Identifiers.objects.filter(database=ReferenceDatabase.DOI)
    n = doi_identifiers.count()
    logger.write(f"Validating {n} DOIs")
    if n == 0:
        return

    existing_dois = 0
    invalid_doi_idents = []
    new_candidates_ids = []
    new_candidates_dois = []

    # loop through once and add all valid DOIs to saved list to check for dupes as we go
    for ident in doi_identifiers.iterator():
        if DOI_EXACT.fullmatch(ident.unique_id):
            existing_dois += 1
        else:
            doi = try_get_doi(ident.unique_id, full_text=True)
            if doi:
                new_candidates_dois.append(doi)
                new_candidates_ids.append(ident.id)
            else:
                # DOI is invalid, save to be deleted below
                invalid_doi_idents.append(ident)

    # unchanged
    logger.write(f"{existing_dois:8} DOI unchanged")

    # deleted
    ids = [ident.id for ident in invalid_doi_idents]
    dois = "\n".join([f"\t\t{ident.unique_id}" for ident in invalid_doi_idents])
    logger.write(f"{len(invalid_doi_idents):8} DOI deleted; invalid IDs:\n{dois}")
    Identifiers.objects.filter(id__in=ids).delete()

    # update or merge
    logger.write(f"{len(new_candidates_dois):8} new DOI candidates extracted from bad DOIs")

    # get existing dois that may already match
    existing_dois = Identifiers.existing_doi_map(new_candidates_dois)
    new_candidates_idents = Identifiers.objects.filter(id__in=new_candidates_ids).prefetch_related(
        Prefetch("references", queryset=Reference.objects.all().only("id"))
    )
    ident_deletes = []
    ident_updates = []
    m2m_creates = []
    RefIdentM2M = Reference.identifiers.through
    for ident in new_candidates_idents:
        doi = try_get_doi(ident.unique_id, full_text=True)
        if doi in existing_dois:
            # mark this identifier for deletion
            ident_deletes.append(ident.id)
            # update m2m relations to existing identifier
            new_ident_id = existing_dois[doi]
            for ref in ident.references.all():
                m2m_creates.append(RefIdentM2M(identifiers_id=new_ident_id, reference_id=ref.id))
        else:
            # update this identifier
            ident.unique_id = doi
            existing_dois[doi] = ident.id
            ident_updates.append(ident)

    logger.write(f"{len(ident_deletes):8} DOIs deleted from candidates (merged w/ existing)")
    logger.write(f"{len(ident_updates):8} DOIs updated from candidates (new valid DOI)")
    logger.write(f"{len(m2m_creates):8} new Identifier-Reference relations created (post-merge)")

    Identifiers.objects.filter(id__in=ident_deletes).delete()
    Identifiers.objects.bulk_update(ident_updates, ["unique_id"])
    RefIdentM2M.objects.bulk_create(m2m_creates)
