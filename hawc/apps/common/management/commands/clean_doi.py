import html
import json

from django.core.management.base import BaseCommand
from django.db import transaction

from hawc.apps.lit import constants
from hawc.apps.lit.models import Identifiers, Reference


class Command(BaseCommand):
    help = """Clean doi IDs and attempt to create doi ids for references without one"""

    def add_arguments(self, parser):
        parser.add_argument(
            "--extensive",
            action="store_true",
            help="Attempt to extract DOI ids from all content fields",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        doi_identifiers = Identifiers.objects.filter(database=4)
        doi_id_initial = doi_identifiers.count()
        validate_dois(doi_identifiers)
        refs = Reference.objects.exclude(identifiers__database=4)
        doi_ref_initial = Reference.objects.filter(identifiers__database=4).count()
        if options["extensive"]:
            create_dois_extensive(refs)
        else:
            create_dois(refs)
        doi_id_final = Identifiers.objects.filter(database=4).count()
        doi_ref_final = Reference.objects.filter(identifiers__database=4).count()
        ref_total = Reference.objects.count()
        print(f"Began with {doi_id_initial} doi IDs; finished with {doi_id_final} doi IDs")
        print(
            f"Began with {doi_ref_initial} references with doi IDs; finished with {doi_ref_final} references with doi IDs, out of {ref_total} total references"
        )


def validate_dois(doi_identifiers):
    print(f"Validating {doi_identifiers.count()} doi IDs...")
    clean_count = 0
    doi_id_saved = []
    for doi_id in doi_identifiers:
        if constants.DOI_EXACT.fullmatch(doi_id.unique_id):
            doi_id_saved.append(doi_id.unique_id)

    duplicate_doi_ids = {}  # stores unclean DOIs that have a clean duplicate for updating later
    tarnished_doi_ids = []  # tarnished DOI IDs cannot be cleaned/validated (ex: '10')
    for doi_id in doi_identifiers:
        new_doi = html.unescape(
            doi_id.unique_id
        )  # converts html character references to actual Unicode characters (ex: &gt; to >)
        if (
            constants.DOI_EXACT.fullmatch(new_doi) and new_doi not in doi_id_saved
        ):  # html conversion made a difference; update
            doi_id.unique_id = new_doi
            doi_id.save()
            doi_id_saved.append(new_doi)
            clean_count = clean_count + 1
        elif (
            constants.DOI_EXACT.fullmatch(new_doi) and new_doi != doi_id.unique_id
        ):  # html conversion made a difference but theres an existing duplicate
            duplicate_doi_ids[new_doi] = doi_id
        elif not constants.DOI_EXACT.fullmatch(
            new_doi
        ):  # doi needs to be further cleaned/validated
            new_doi = constants.DOI_EXTRACT.search(new_doi)
            if new_doi:
                new_doi = new_doi.group(0)
            if new_doi and new_doi.endswith("."):  # remove period at end of doi if it exists
                new_doi = new_doi[: len(new_doi) - 1]
            if new_doi is None or not constants.DOI_EXACT.fullmatch(
                new_doi
            ):  # extraction failed; doi is tarnished
                tarnished_doi_ids.append(doi_id)
            else:
                if new_doi in doi_id_saved:
                    duplicate_doi_ids[
                        new_doi
                    ] = doi_id  # new doi exists already; save to duplicates for updating
                else:
                    doi_id.unique_id = new_doi  # update doi ID with validated doi
                    doi_id.save()
                    doi_id_saved.append(doi_id.unique_id)
                    clean_count = clean_count + 1
    print(f"\tCleaned and updated {clean_count} existing doi IDs")

    # pull references with incorrect DOI id and replace that ID with the correct duplicate doi ID
    print(f"Merging {len(duplicate_doi_ids)} duplicate doi ID(s)")
    for dupe, old_doi in duplicate_doi_ids.items():
        print(f"\t Merging doi:'{old_doi.unique_id}' into doi:'{dupe}'")
        for reference in Reference.objects.filter(identifiers__id=old_doi.id):
            reference.identifiers.remove(old_doi)
            reference.identifiers.add(Identifiers.objects.filter(unique_id=dupe)[0])
        old_doi.delete()

    # delete doi IDs that cannot be cleaned
    print(f"Deleting {len(tarnished_doi_ids)} tarnished doi ID(s)")
    for doi in tarnished_doi_ids:
        print(f"\t Removing doi: '{doi.unique_id}'")
        for reference in Reference.objects.filter(identifiers__id=doi.id):
            reference.identifiers.remove(doi)
        doi.delete()


def create_dois(refs):
    # warning: takes a while!
    # goes through all references without a DOI id and attempts to locate a DOI within the other ids
    # this method loads the content attribute for an id and checks the doi attribute for a valid doi
    print(f"Attempting to create doi IDs for {refs.count()} references...")
    for ref in refs:
        for ids in ref.identifiers.all():
            doi = None
            if ids.content != "":
                if ids.database == constants.HERO:
                    try:
                        doi = json.loads(ids.content)["json"]["doi"]
                    except (KeyError):
                        try:
                            doi = json.loads(ids.content)["doi"]
                        except (KeyError):
                            doi = None
                if ids.database == constants.RIS or ids.database == constants.PUBMED:
                    doi = json.loads(ids.content)["doi"]
            if constants.DOI_EXTRACT.search(str(doi)):
                doi = constants.DOI_EXTRACT.search(str(doi)).group(0)
                doi_identifier = Identifiers.objects.get_or_create(
                    unique_id=doi, database=constants.DOI
                )
                ref.identifiers.add(doi_identifier[0])


def create_dois_extensive(refs):
    # warning: takes a while!
    # goes through all references without a DOI id and attempts to locate a DOI within the other ids
    # This method searches through the entire content field of an identifier instead of json loading and referencing just the doi attribute
    print(f"Attempting to extensively create doi IDs for {refs.count()} references...")
    for ref in refs:
        for ids in ref.identifiers.all():
            doi = constants.DOI_EXTRACT.search(ids.content)
            if doi:
                doi = doi.group(0)
                if doi.endswith(","):
                    doi = doi[: len(doi) - 1]
                if doi.endswith('"'):
                    doi = doi[: len(doi) - 1]
                if doi.endswith("."):
                    doi = doi[: len(doi) - 1]
                doi_identifier = Identifiers.objects.get_or_create(
                    unique_id=doi, database=constants.DOI
                )
                ref.identifiers.add(doi_identifier[0])
