from typing import DefaultDict

from django.core.management.base import BaseCommand
from django.db import transaction

from hawc.apps.lit import constants
from hawc.apps.lit.models import Identifiers, Reference
from hawc.services.utils.doi import get_doi_from_hero, get_doi_from_pubmed_or_ris, get_doi_if_valid


class Command(BaseCommand):
    help = """Clean doi IDs and attempt to create doi ids for references without one"""

    def add_arguments(self, parser):
        parser.add_argument(
            "--extensive",
            action="store_true",
            help="Attempt to extract DOI ids from all content fields",
        )
        parser.add_argument(
            "--skip_create",
            action="store_true",
            help="Only validate existing DOIs; do not create new ones",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        doi_identifiers = Identifiers.objects.filter(database=constants.DOI)
        doi_id_initial = doi_identifiers.count()
        validate_dois(self, doi_identifiers)
        if not options["skip_create"]:
            refs = Reference.objects.exclude(identifiers__database=constants.DOI)
            doi_ref_initial = Reference.objects.filter(identifiers__database=constants.DOI).count()
            self.stdout.write(f"Attempting to create doi IDs for {refs.count()} references...")
            create_dois(refs, extensive=options["extensive"])
            doi_id_final = Identifiers.objects.filter(database=constants.DOI).count()
            doi_ref_final = Reference.objects.filter(identifiers__database=constants.DOI).count()
            ref_total = Reference.objects.count()
            self.stdout.write(
                f"Began with {doi_id_initial} doi IDs; finished with {doi_id_final} doi IDs"
            )
            self.stdout.write(
                f"Began with {doi_ref_initial} references with doi IDs; finished with {doi_ref_final} references with doi IDs, out of {ref_total} total references"
            )


def validate_dois(self, doi_identifiers):
    """Checks all existing doi IDs for valid doi ids, which are stored as a unique_id for doi identifiers
    Attempts to clean all the failing dois, merges duplicate doi IDs, and deletes invalid doi IDs that cannot be cleaned

    Args:
        doi_identifiers (QuerySet[Identifiers]): List of doi IDs to be checked
    """
    self.stdout.write(f"Validating {doi_identifiers.count()} doi IDs...")

    doi_id_saved = {}
    doi_idents_updated = []
    # duplicate_doi_ids: stores unclean DOIs that have a clean duplicate for updating later
    duplicate_doi_ids = DefaultDict(list)
    # invalid DOI IDs cannot be cleaned/validated (ex: '10')
    invalid_doi_idents = []

    # loop through once and add all valid dois to saved list to check for dupes as we go
    for ident in doi_identifiers:
        if constants.DOI_EXACT.fullmatch(ident.unique_id):
            doi_id_saved[ident.unique_id] = ident

    for ident in doi_identifiers:
        new_doi = get_doi_if_valid(ident.unique_id)
        if new_doi:
            if new_doi not in doi_id_saved:
                # doi validation resulted in a new doi--save to be bulk updated
                ident.unique_id = new_doi
                doi_idents_updated.append(ident)
                doi_id_saved[new_doi] = ident
            elif new_doi != ident.unique_id:
                # new doi exists already; save as a duplicate to be processed below
                duplicate_doi_ids[new_doi].append(ident)
        else:
            # extraction failed; doi is invalid, save to be deleted below
            invalid_doi_idents.append(ident)
    Identifiers.objects.bulk_update(doi_idents_updated, ["unique_id"])
    self.stdout.write(f"\tCleaned and updated {len(doi_idents_updated)} existing doi IDs")

    # pull references with incorrect DOI id and replace that ID with the correct duplicate doi ID
    self.stdout.write(f"Merging {len(duplicate_doi_ids)} duplicate doi ID(s)")
    for dupe, old_dois in duplicate_doi_ids.items():
        for old_doi in old_dois:
            self.stdout.write(f"\t Merging doi:'{old_doi.unique_id}' into doi:'{dupe}'")
            for reference in old_doi.references.all():
                reference.identifiers.remove(old_doi)
                reference.identifiers.add(doi_id_saved[dupe])
            old_doi.delete()

    # delete doi IDs that cannot be cleaned
    self.stdout.write(f"Deleting {len(invalid_doi_idents)} invalid doi ID(s)")
    ids = [id.unique_id for id in invalid_doi_idents]
    for doi in invalid_doi_idents:
        self.stdout.write(f"\t Removing doi: '{doi.unique_id}'")
    Identifiers.objects.filter(unique_id__in=ids).filter(database=constants.DOI).delete()


def create_dois(refs, extensive: bool = False):
    """goes through all references and attempts to locate a DOI from other ids
    default: json loads each id's content attribute and checks the doi attribute for a valid doi if false
        if True, searches entire content attribute as a string, no json loading
    extensive: searches entire content field for a valid doi

    Args:
        refs ([References]): a list of references without doi identifiers
        extensive (bool, optional): Determines whether to search extensively or by default (see above). Defaults to False.
    """
    for ref in refs.prefetch_related("identifiers"):
        for ids in ref.identifiers.all():
            doi = None
            if extensive:
                doi = get_doi_if_valid(ids.content)
            else:
                if ids.content != "":
                    if ids.database == constants.HERO:
                        doi = get_doi_from_hero(ids)
                    if ids.database == constants.RIS or ids.database == constants.PUBMED:
                        doi = get_doi_from_pubmed_or_ris(ids)
            if doi:
                doi_identifier, created = Identifiers.objects.get_or_create(
                    unique_id=doi, database=constants.DOI
                )
                ref.identifiers.add(doi_identifier)
                break
