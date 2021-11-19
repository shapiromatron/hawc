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
        validate_dois(doi_identifiers)
        refs = Reference.objects.exclude(identifiers__database=4)
        if options["extensive"]:
            create_dois_extensive(refs)
        else:
            create_dois(refs)


def validate_dois(doi_identifiers):
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

    # pull references with incorrect DOI id and replace that ID with the correct duplicate doi ID
    for dupe, old_doi in duplicate_doi_ids.items():
        for reference in Reference.objects.filter(identifiers__id=old_doi.id):
            reference.identifiers.remove(old_doi)
            reference.identifiers.add(Identifiers.objects.filter(unique_id=dupe)[0])
        old_doi.delete()

    # delete doi IDs that cannot be cleaned
    for doi in tarnished_doi_ids:
        for reference in Reference.objects.filter(identifiers__id=doi.id):
            reference.identifiers.remove(doi)
        doi.delete()


def create_dois(refs):
    # warning: takes a while!
    # goes through all references without a DOI id and attempts to locate a DOI within the other ids
    # this method loads the content attribute for an id and checks the doi attribute for a valid doi
    for ref in refs:
        for ids in ref.identifiers.all():
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
                try:
                    existingID = Identifiers.objects.get(
                        unique_id=doi
                    )  # check if doi ID already exists
                    ref.identifiers.add(existingID)
                except (Identifiers.DoesNotExist):  # if not, create it and save to reference
                    newID = Identifiers(unique_id=doi, database=4)
                    newID.save()
                    ref.identifiers.add(newID)


def create_dois_extensive(refs):
    # warning: takes a while!
    # goes through all references without a DOI id and attempts to locate a DOI within the other ids
    # This method searches through the entire content field of an identifier instead of json loading and referencing just the doi attribute
    for ref in refs:
        for ids in ref.identifiers.all():
            doi = constants.DOI_EXTRACT.search(ids.content())
            if doi:
                doi = doi.group(0)
                if doi.endswith(","):
                    doi = doi[: len(doi) - 1]
                if doi.endswith('"'):
                    doi = doi[: len(doi) - 1]
                if doi.endswith("."):
                    doi = doi[: len(doi) - 1]
                doi_identifier = Identifiers.objects.get_or_create(unique_id=doi)
                ref.identifiers.add(doi_identifier)
