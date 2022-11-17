import html
import json
import logging
import pickle
import re
from io import BytesIO
from math import ceil
from urllib import parse

import pandas as pd
from celery import chain
from celery.result import ResultBase
from django.apps import apps
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from reversion import revisions as reversion
from taggit.models import ItemBase
from treebeard.mp_tree import MP_Node

from ...constants import ColorblindColors
from ...refml import topics
from ...services.nih import pubmed
from ...services.utils import ris
from ...services.utils.doi import get_doi_from_identifier, try_get_doi
from ..common.helper import SerializerHelper
from ..common.models import (
    AssessmentRootMixin,
    CustomURLField,
    NonUniqueTagBase,
    get_private_data_storage,
)
from ..myuser.models import HAWCUser
from . import constants, managers, tasks

logger = logging.getLogger(__name__)


class TooManyPubMedResults(Exception):
    """
    Raised when returned Query is too large
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class LiteratureAssessment(models.Model):

    DEFAULT_EXTRACTION_TAG = "Inclusion"
    TOPIC_MODEL_MIN_REFERENCES = 50

    assessment = models.OneToOneField(
        "assessment.Assessment",
        editable=False,
        on_delete=models.CASCADE,
        related_name="literature_settings",
    )
    conflict_resolution = models.BooleanField(
        default=settings.HAWC_FEATURES.DEFAULT_LITERATURE_CONFLICT_RESOLUTION,
        verbose_name="Conflict resolution required",
        help_text="Enable conflict resolution for reference screening. If enabled, at least two reviewers must independently review and tag literature, and tag conflicts must be resolved before tags are applied to a reference. If disabled, tags are immediately applied to references.  We do not recommend changing this setting after screening has begun.",
    )
    extraction_tag = models.ForeignKey(
        "lit.ReferenceFilterTag",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text="References tagged with this tag or its descendants will be available for data extraction and study quality/risk of bias evaluation.",
    )
    screening_instructions = models.TextField(
        blank=True,
        help_text="""Add instructions for screeners. This information will be shown on the
        literature screening page and will publicly available, if the assessment is made public.""",
    )
    name_list_1 = models.CharField(
        max_length=64,
        verbose_name="Name List 1",
        default="Positive",
        help_text="Name for this list of keywords",
    )
    color_list_1 = models.CharField(
        max_length=7,
        verbose_name="Highlight Color 1",
        default=ColorblindColors.BRIGHT[2],
        help_text="Keywords in list 1 will be highlighted this color",
    )
    keyword_list_1 = models.TextField(
        blank=True,
        help_text="""Keywords to highlight in titles and abstracts on the reference tagging page.
         Keywords are pipe-separated ("|") to allow for highlighting chemicals which may include
         commas.""",
    )
    name_list_2 = models.CharField(
        max_length=64,
        verbose_name="Name List 2",
        default="Negative",
        help_text="Name for this list of keywords",
    )
    color_list_2 = models.CharField(
        max_length=7,
        verbose_name="Highlight Color 2",
        default=ColorblindColors.BRIGHT[1],
        help_text="Keywords in list 2 will be highlighted this color",
    )
    keyword_list_2 = models.TextField(
        blank=True,
        help_text="""Keywords to highlight in titles and abstracts on the reference tagging page.
         Keywords are pipe-separated ("|") to allow for highlighting chemicals which may include
         commas.""",
    )
    name_list_3 = models.CharField(
        max_length=64,
        verbose_name="Name List 3",
        default="Additional",
        help_text="Name for this list of keywords",
    )
    color_list_3 = models.CharField(
        max_length=7,
        verbose_name="Highlight Color 3",
        default=ColorblindColors.BRIGHT[0],
        help_text="Keywords in list 3 will be highlighted this color",
    )
    keyword_list_3 = models.TextField(
        blank=True,
        help_text="""Keywords to highlight in titles and abstracts on the reference tagging page.
         Keywords are pipe-separated ("|") to allow for highlighting chemicals which may include
         commas.""",
    )
    topic_tsne_data = models.FileField(
        blank=True,
        null=True,
        editable=False,
        upload_to="lit/topic_model",
        storage=get_private_data_storage(),
    )
    topic_tsne_refresh_requested = models.DateTimeField(null=True)
    topic_tsne_last_refresh = models.DateTimeField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    BREADCRUMB_PARENT = "assessment"

    def __str__(self):
        return "Literature assessment settings"

    @classmethod
    def build_default(cls, assessment: "assessment.Assessment") -> "LiteratureAssessment":
        extraction_tag = (
            ReferenceFilterTag.get_assessment_root(assessment.id)
            .get_children()
            .filter(name=cls.DEFAULT_EXTRACTION_TAG)
            .first()
        )

        return cls.objects.create(
            assessment=assessment, extraction_tag_id=extraction_tag.id if extraction_tag else None
        )

    def get_assessment(self):
        return self.assessment

    def get_absolute_url(self):
        return reverse("lit:tags_update", args=(self.assessment_id,))

    def get_update_url(self) -> str:
        return reverse("lit:literature_assessment_update", args=(self.id,))

    def get_topic_model_url(self) -> str:
        return reverse("lit:api:assessment-topic-model", args=(self.assessment_id,))

    def get_topic_model_refresh_url(self) -> str:
        return reverse("lit:api:assessment-topic-model-request-refresh", args=(self.assessment_id,))

    @property
    def topic_tsne_fig_dict_cache_key(self) -> str:
        return f"{self.assessment_id}_topic_tsne_data"

    @property
    def topic_tsne_data_filename(self) -> str:
        return f"assessment-{self.assessment_id}.pkl"

    def create_topic_tsne_data(self) -> None:
        columns = ("id", "title", "abstract")
        refs = Reference.objects.filter(assessment=self.assessment_id).values_list(*columns)
        df = pd.DataFrame(data=refs, columns=columns)
        df.loc[:, "text"] = df.title + " " + df.abstract
        df.loc[:, "title"] = df.title.apply(topics.textwrapper)
        df.drop(columns=["abstract"], inplace=True)

        df, topics_df = topics.topic_model_tsne(df)

        f1 = BytesIO()
        df.to_parquet(f1, engine="pyarrow", index=False)

        f2 = BytesIO()
        topics_df.to_parquet(f2, engine="pyarrow", index=False)

        data = dict(df=f1.getvalue(), topics=f2.getvalue())

        if self.has_topic_model:
            self.topic_tsne_data.delete(save=False)
        self.topic_tsne_refresh_requested = None
        self.topic_tsne_last_refresh = timezone.now()
        self.topic_tsne_data.save(self.topic_tsne_data_filename, ContentFile(pickle.dumps(data)))
        cache.delete(self.topic_tsne_fig_dict_cache_key)

    def get_topic_tsne_data(self) -> dict:
        if not self.has_topic_model:
            raise ValueError("No data available.")
        data = pickle.load(self.topic_tsne_data.file.file)
        data["df"] = pd.read_parquet(BytesIO(data["df"]), engine="pyarrow")
        data["topics"] = pd.read_parquet(BytesIO(data["topics"]), engine="pyarrow")
        return data

    def get_topic_tsne_fig_dict(self) -> dict:
        fig_dict = cache.get(self.topic_tsne_fig_dict_cache_key)
        if fig_dict is None:
            data = self.get_topic_tsne_data()
            fig = topics.tsne_to_scatterplot(data)
            fig_dict = fig.to_dict()
            cache.set(self.topic_tsne_fig_dict_cache_key, fig_dict, 60 * 60)  # cache for 1 hour
        return fig_dict

    @property
    def has_topic_model(self) -> bool:
        name = self.topic_tsne_data.name
        return name is not None and name != ""

    def can_topic_model(self) -> bool:
        return self.assessment.references.count() >= self.TOPIC_MODEL_MIN_REFERENCES

    def can_request_refresh(self) -> bool:
        return self.can_topic_model and self.topic_tsne_refresh_requested is None

    def get_keyword_data(self) -> dict:
        return {
            "set1": {
                "name": self.name_list_1,
                "color": self.color_list_1,
                "keywords": [word.strip() for word in self.keyword_list_1.split("|") if word],
            },
            "set2": {
                "name": self.name_list_2,
                "color": self.color_list_2,
                "keywords": [word.strip() for word in self.keyword_list_2.split("|") if word],
            },
            "set3": {
                "name": self.name_list_3,
                "color": self.color_list_3,
                "keywords": [word.strip() for word in self.keyword_list_3.split("|") if word],
            },
        }


class Search(models.Model):
    objects = managers.SearchManager()

    MANUAL_IMPORT_SLUG = "manual-import"

    assessment = models.ForeignKey(
        "assessment.Assessment", on_delete=models.CASCADE, related_name="literature_searches"
    )
    search_type = models.CharField(max_length=1, choices=constants.SearchType.choices)
    source = models.PositiveSmallIntegerField(
        choices=constants.ReferenceDatabase.choices,
        help_text="Database used to identify literature.",
    )
    title = models.CharField(
        max_length=128,
        help_text="A brief-description to describe the identified literature.",
    )
    slug = models.SlugField(
        verbose_name="URL Name",
        help_text="The URL (web address) used to describe this object "
        "(no spaces or special-characters).",
    )
    description = models.TextField(
        blank=True,
        help_text="A more detailed description of the literature search or import strategy.",
    )
    search_string = models.TextField(
        blank=True,
        help_text="The search-text used to query an online database. "
        "Use colors to separate search-terms (optional).",
    )
    import_file = models.FileField(upload_to="lit-search-import", blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    BREADCRUMB_PARENT = "assessment"

    class Meta:
        verbose_name_plural = "searches"
        unique_together = (("assessment", "slug"), ("assessment", "title"))
        ordering = ["-last_updated"]
        get_latest_by = "last_updated"

    def __str__(self):
        return self.title

    @property
    def is_manual_import(self):
        # special case- created when assessment is created
        return (
            self.search_type == constants.SearchType.IMPORT and self.slug == self.MANUAL_IMPORT_SLUG
        )

    def get_absolute_url(self):
        return reverse("lit:search_detail", args=(self.assessment_id, self.slug))

    def get_assessment(self):
        return self.assessment

    def delete(self, **kwargs):
        # cascade delete references which no longer relate to any searches
        orphans = self.sole_references()
        if orphans.count() > 0:
            logger.info(
                f"Removed {orphans.count()} orphan references from assessment {self.assessment_id}"
            )
            orphans.delete()
        super().delete(**kwargs)

    @property
    def search_string_text(self):
        return html.unescape(strip_tags(self.search_string))

    @transaction.atomic
    def run_new_query(self):
        if self.source == constants.ReferenceDatabase.PUBMED:
            prior_query = None
            try:
                prior_query = PubMedQuery.objects.filter(search=self.pk).latest("query_date")
            except ObjectDoesNotExist:
                pass
            pubmed = PubMedQuery(search=self)
            results_dictionary = pubmed.run_new_query(prior_query)
            self.create_new_references(results_dictionary)
            self.delete_old_references(results_dictionary)
        else:
            raise Exception("Search functionality disabled")

    @property
    def import_ids(self):
        # convert from string->set->list to remove repeat ids
        return list(set(v.strip() for v in self.search_string_text.split(",")))

    @transaction.atomic
    def run_new_import(self, content=None):
        """Execute an import, creating references and identifiers.

        In some cases, content may be provided, where we may validate and process the data. In
        other cases, we may need to process the data in this method.

        Args:
            content (optional): existing identifier metadata, if available

        Raises:
            ValueError: If any error occurs
        """
        if self.source == constants.ReferenceDatabase.PUBMED:
            ids = [int(id) for id in self.import_ids]
            if content is None:
                # fetch content if not provided
                content = Identifiers.objects.validate_pubmed_ids(ids)
            Identifiers.objects.bulk_create_pubmed_ids(content)
            identifiers = Identifiers.objects.pubmed(ids)
            Reference.objects.get_pubmed_references(self, identifiers)
        elif self.source == constants.ReferenceDatabase.HERO:
            ids = [int(id) for id in self.import_ids]
            if content is None:
                # fetch content if not provided
                content = Identifiers.objects.validate_hero_ids(ids)
            Identifiers.objects.bulk_create_hero_ids(content)
            identifiers = Identifiers.objects.hero(ids)
            Reference.objects.get_hero_references(self, identifiers)
        elif self.source == constants.ReferenceDatabase.RIS:
            # check if importer references are cached on object
            refs = getattr(self, "_references", None)
            if refs is None:
                importer = ris.RisImporter(self.import_file.path)
                refs = importer.references
            identifiers = Identifiers.objects.get_from_ris(self.id, refs)
            Reference.objects.update_from_ris_identifiers(self, identifiers)
        else:
            raise ValueError(f"Source type cannot be imported: {self.source}")

    def create_new_references(self, results):
        # Create assessment-specific references for each value which return
        # result which was added, based on the new results query values, where
        # results is a dictionary with a field "added", which is a list of the
        # primary keys of identifiers which need a new reference creation.

        RefSearchM2M = Reference.searches.through
        RefIdM2M = Reference.identifiers.through

        # For the cases where the current search found a new identifier which
        # already has an assessment-specific Reference object associated with
        # it, just associate the current reference with this search.
        added_str = [str(id) for id in results["added"]]
        ref_ids = (
            Reference.objects.filter(
                assessment=self.assessment, identifiers__unique_id__in=added_str
            )
            .exclude(searches=self)
            .values_list("pk", flat=True)
        )
        ids_count = ref_ids.count()

        if ids_count > 0:
            logger.debug("Starting bulk creation of existing search-through values")
            ref_searches = [RefSearchM2M(reference_id=ref, search_id=self.pk) for ref in ref_ids]
            RefSearchM2M.objects.bulk_create(ref_searches)
            logger.debug(f"Completed bulk creation of {len(ref_searches)} search-through values")

        # For the cases where the search resulted in new ids which may or may
        # not already be imported as a reference for this assessment, find the
        # proper subset.
        ids = (
            Identifiers.objects.filter(database=self.source, unique_id__in=added_str)
            .exclude(references__in=Reference.objects.get_qs(self.assessment))
            .order_by("pk")
        )
        ids_count = ids.count()

        if ids_count > 0:
            block_id = timezone.now()

            # create list of references for each identifier
            refs = [i.create_reference(self.assessment, block_id) for i in ids]
            id_pks = [i.pk for i in ids]

            logger.debug(f"Starting  bulk creation of {len(refs)} references")
            Reference.objects.bulk_create(refs)
            logger.debug(f"Completed bulk creation of {len(refs)} references")

            # re-query to get the objects back with PKs
            refs = Reference.objects.filter(assessment=self.assessment, block_id=block_id).order_by(
                "pk"
            )

            # associate identifiers with each
            ref_searches = []
            ref_ids = []
            logger.debug(f"Starting  bulk creation of {refs.count()} reference-through values")
            for i, ref in enumerate(refs):
                ref_searches.append(RefSearchM2M(reference_id=ref.pk, search_id=self.pk))
                ref_ids.append(RefIdM2M(reference_id=ref.pk, identifiers_id=id_pks[i]))
            RefSearchM2M.objects.bulk_create(ref_searches)
            RefIdM2M.objects.bulk_create(ref_ids)
            logger.debug(f"Completed bulk creation of {refs.count()} reference-through values")

            # finally, remove temporary identifier used for re-query after bulk_create
            logger.debug("Removing block-id from created references")
            refs.update(block_id=None)

    def delete_old_references(self, results):
        """Conservatively delete results which were removed in the most recent search.

        Only delete references that meet the following criteria:

        1. were "removed" in the latest result set
        2. are not associated in any other searches
        3. do not have any tags applied
        4. do not have any studies
        """
        if results["removed"]:
            ids = [str(id) for id in results["removed"]]
            # filter removed references with no tags
            no_tags = list(
                self.references.filter(identifiers__unique_id__in=ids)
                .annotate(ntags=models.Count("tags"))
                .filter(ntags=0)
                .values_list("id", flat=True)
            )
            # filter untagged references with only one search (this one)
            no_searches = (
                Reference.objects.filter(id__in=no_tags)
                .annotate(nsearches=models.Count("searches"))
                .filter(nsearches=1)
            )
            # filter references where studies exist
            _ids = no_searches.values_list("id", flat=True)
            Study = apps.get_model("study", "Study")
            no_studies = no_searches.exclude(id__in=Study.objects.filter(id__in=_ids))

            # remove candidate deletions
            n = no_studies.count()
            if n > 0:
                logger.info(f"Removing {n} references from search {self.id}")
                no_studies.delete()

    def studies(self) -> models.QuerySet:
        Study = apps.get_model("study", "study")
        ids = self.references.values_list("id", flat=True)
        return Study.objects.filter(id__in=ids)

    def sole_studies(self) -> models.QuerySet:
        """Studies associated with this and only this search."""
        Study = apps.get_model("study", "study")
        ids = self.sole_references().values_list("id", flat=True)
        return Study.objects.filter(id__in=ids)

    def sole_references(self) -> models.QuerySet:
        """References associated with this and only this search."""
        return (
            Reference.objects.filter(id__in=self.references.all())
            .annotate(n_searches=models.Count("searches"))
            .filter(n_searches=1)
        )

    @property
    def date_last_run(self):
        if (
            self.source == constants.ReferenceDatabase.PUBMED
            and self.search_type == constants.SearchType.SEARCH
        ):
            try:
                return PubMedQuery.objects.filter(search=self).latest().query_date
            except Exception:
                return "Never (not yet run)"
        else:
            return self.last_updated

    @classmethod
    def build_default(cls, assessment):
        """
        Constructor to define default search when a new assessment is created.
        """
        cls.objects.create(
            assessment=assessment,
            source=constants.EXTERNAL_LINK,
            search_type="i",
            title="Manual import",
            slug=cls.MANUAL_IMPORT_SLUG,
            description="Default search instance used for manually "
            "importing literature into HAWC instead of "
            "using a search.",
            search_string="None. This is used to manually enter literature.",
        )

    def get_pubmed_queries(self):
        """
        Get all PubMed queries for the selected search, unpacking the JSON
        description object which details imported details.
        """
        dicts = []
        pubmed_queries = PubMedQuery.objects.filter(search=self)
        for pubmed_query in pubmed_queries:
            dicts.append(pubmed_query.to_dict())
        return dicts

    @property
    def references_count(self):
        return self.references.all().count()

    @property
    def references_tagged_count(self):
        return (
            self.references.all()
            .annotate(tag_count=models.Count("tags"))
            .filter(tag_count__gt=0)
            .count()
        )

    @property
    def fraction_tagged(self):
        refs = self.references_count
        if refs > 0:
            return 1.0 - (len(self.references_untagged)) / float(refs)
        return None

    @property
    def references_untagged(self):
        return self.references.all().annotate(tag_count=models.Count("tags")).filter(tag_count=0)

    def to_dict(self):
        return dict(
            pk=self.pk,
            title=self.title,
            url=self.get_absolute_url(),
            search_type=self.get_search_type_display(),
        )


class PubMedQuery(models.Model):
    objects = managers.PubMedQueryManager()

    search = models.ForeignKey(Search, on_delete=models.CASCADE)
    results = models.TextField(blank=True)
    query_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "PubMed Queries"
        ordering = ["-query_date"]
        get_latest_by = "query_date"

    def run_new_query(self, prior_query):
        # Create a new search
        search = pubmed.PubMedSearch(term=self.search.search_string_text)
        search.get_ids_count()

        if search.id_count > settings.PUBMED_MAX_QUERY_SIZE:
            raise TooManyPubMedResults(
                "Too many PubMed references found: {0}; reduce query scope to "
                "fewer than {1}".format(search.id_count, settings.PUBMED_MAX_QUERY_SIZE)
            )

        search.get_ids()
        results = {"ids": search.ids, "added": search.ids, "removed": []}

        if prior_query:
            old_ids_list = json.loads(prior_query.results)["ids"]
            changes = search.get_changes_from_previous_search(old_ids_list=old_ids_list)
            results["added"] = list(changes["added"])
            results["removed"] = list(changes["removed"])

        self.results = json.dumps(results)
        self.save()
        self.create_identifiers()
        return results

    def create_identifiers(self):
        # Create new PubMed identifiers for any PMIDs which are not already in
        # our database.
        new_ids = json.loads(self.results)["added"]
        existing_pmids = [
            int(id_)
            for id_ in Identifiers.objects.filter(
                database=constants.ReferenceDatabase.PUBMED, unique_id__in=new_ids
            ).values_list("unique_id", flat=True)
        ]
        ids_to_add = list(set(new_ids) - set(existing_pmids))
        ids_to_add_len = len(ids_to_add)

        block_size = 1000.0
        logger.debug(f"{ids_to_add_len} IDs to be added")
        for i in range(int(ceil(ids_to_add_len / block_size))):
            start_index = int(i * block_size)
            end_index = min(int(i * block_size + block_size), ids_to_add_len)
            logger.debug(f"Building from {start_index} to {end_index}")
            fetch = pubmed.PubMedFetch(
                id_list=ids_to_add[start_index:end_index], retmax=int(block_size)
            )
            identifiers = []
            for item in fetch.get_content():
                identifiers.append(
                    Identifiers(
                        unique_id=item["PMID"],
                        database=constants.ReferenceDatabase.PUBMED,
                        content=json.dumps(item),
                    )
                )
            Identifiers.objects.bulk_create(identifiers)

    def to_dict(self):
        def get_len(obj):
            if obj is not None:
                return len(obj)
            else:
                return 0

        details = json.loads(self.results)
        d = {
            "query_date": self.query_date,
            "total_count": get_len(details["ids"]),
            "total_added": get_len(details["added"]),
            "total_removed": get_len(details["removed"]),
        }
        return d


class Identifiers(models.Model):
    objects = managers.IdentifiersManager()

    unique_id = models.CharField(
        max_length=256, db_index=True
    )  # DOI has no limit; we make this relatively large
    database = models.IntegerField(choices=constants.ReferenceDatabase.choices)
    content = models.TextField()
    url = models.URLField(blank=True)

    class Meta:
        unique_together = (("database", "unique_id"),)
        index_together = (("database", "unique_id"),)
        verbose_name_plural = "identifiers"

    def __str__(self):
        return f"{self.database}: {self.unique_id}"

    URL_TEMPLATES = {
        constants.ReferenceDatabase.PUBMED: r"https://www.ncbi.nlm.nih.gov/pubmed/{0}",
        constants.ReferenceDatabase.HERO: r"http://hero.epa.gov/index.cfm?action=reference.details&reference_id={0}",
        constants.ReferenceDatabase.DOI: r"https://doi.org/{0}",
        constants.ReferenceDatabase.WOS: r"http://apps.webofknowledge.com/InboundService.do?product=WOS&UT={0}&action=retrieve&mode=FullRecord",
        constants.ReferenceDatabase.SCOPUS: r"http://www.scopus.com/record/display.uri?eid={0}&origin=resultslist",
    }

    def get_url(self):
        url = self.url
        template = self.URL_TEMPLATES.get(self.database, None)
        if template:
            url = template.format(parse.quote(self.unique_id))
        return url

    def create_reference(self, assessment, block_id=None):
        # create, but don't save reference object
        try:
            content = self.get_content()
        except ValueError:
            if self.database == constants.ReferenceDatabase.PUBMED:
                self.update_pubmed_content([self])
            raise AttributeError(f"Content invalid JSON: {self.unique_id}")

        if self.database == constants.ReferenceDatabase.PUBMED:
            ref = Reference(
                assessment=assessment,
                title=content.get("title", "[no title]"),
                authors_short=content.get("authors_short", "[no authors]"),
                authors=", ".join(content.get("authors", [])),
                journal=content.get("citation", "[no journal citation]"),
                abstract=content.get("abstract", "[no abstract]"),
                year=content.get("year", None),
                block_id=block_id,
            )
        elif self.database == constants.ReferenceDatabase.HERO:
            ref = Reference(assessment=assessment)
            ref.update_from_hero_content(content)
        else:
            raise ValueError("Unknown database for reference creation.")

        return ref

    def to_dict(self):
        return {
            "id": self.unique_id,
            "database": self.get_database_display(),
            "database_id": self.database,
            "url": self.get_url(),
        }

    def get_content(self) -> dict:
        return json.loads(self.content) if self.content else {}

    @staticmethod
    def update_pubmed_content(idents):
        tasks.update_pubmed_content.delay([d.unique_id for d in idents])

    @classmethod
    def existing_doi_map(cls, dois: list[str]) -> dict[str, int]:
        """
        Return a mapping of DOI and Identifier ID given a list of candidate DOIs
        """
        return {
            k: v
            for (k, v) in Identifiers.objects.filter(
                database=constants.ReferenceDatabase.DOI, unique_id__in=dois
            ).values_list("unique_id", "id")
        }

    def save(self, *args, **kwargs):
        if self.database == constants.ReferenceDatabase.DOI:
            self.unique_id = self.unique_id.lower()
        return super(Identifiers, self).save(*args, **kwargs)


class ReferenceFilterTag(NonUniqueTagBase, AssessmentRootMixin, MP_Node):
    cache_template_taglist = "reference-taglist-assessment-{0}"
    cache_template_tagtree = "reference-tagtree-assessment-{0}"

    def get_nested_name(self) -> str:
        if self.is_root():
            return "<root-node>"
        else:
            return f"{'━ ' * (self.depth - 1)}{self.name}"

    @classmethod
    def get_tags_in_assessment(cls, assessment_pk: int, tag_ids: list[int]):
        """Returns a queryset of matching tags which are in the assessment

        Args:
            assessment_pk (int): assessment id
            tag_ids (list[int]): list of tag ids expected to be in assessment

        Raises:
            ValueError: if any tags are missing or are not in the assessment
        """
        tags = cls.objects.filter(id__in=tag_ids)
        assessment_root = ReferenceFilterTag.get_assessment_root(assessment_pk)
        if len(set(tag_ids)) != tags.count():
            raise ValueError("Tags not found")
        if any(not tag.is_descendant_of(assessment_root) for tag in tags):
            raise ValueError("Tags are not descendants of root")
        return tags

    @classmethod
    def build_default(cls, assessment):
        """
        Constructor to define default literature-tags.
        """
        root = cls.add_root(name=cls.get_assessment_root_name(assessment.pk))

        inc = root.add_child(name=LiteratureAssessment.DEFAULT_EXTRACTION_TAG)
        inc.add_child(name="Human Study")
        inc.add_child(name="Animal Study")
        inc.add_child(name="Mechanistic Study")

        exc = root.add_child(name="Exclusion")
        exc.add_child(name="Tier I")
        exc.add_child(name="Tier II")
        exc.add_child(name="Tier III")

    @classmethod
    def get_flattened_taglist(cls, tagslist, include_parent=True):
        # expects tags dictionary dump_bulk format
        lst = []

        def appendChildren(obj, parents):
            parents = parents + "|" if parents != "" else parents
            txt = parents + obj["data"]["name"]
            lst.append(txt)
            for child in obj.get("children", []):
                appendChildren(child, txt)

        if include_parent:
            appendChildren(tagslist[0], "")
        else:
            for child in tagslist[0].get("children", []):
                appendChildren(child, "")

        return lst


class ReferenceTags(ItemBase):
    objects = managers.ReferenceTagsManager()

    tag = models.ForeignKey(
        ReferenceFilterTag, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_items"
    )
    content_object = models.ForeignKey("Reference", on_delete=models.CASCADE)


class Reference(models.Model):
    TEXT_CLEANUP_FIELDS = ("full_text_url",)

    objects = managers.ReferenceManager()

    assessment = models.ForeignKey(
        "assessment.Assessment", on_delete=models.CASCADE, related_name="references"
    )
    searches = models.ManyToManyField(Search, blank=False, related_name="references")
    identifiers = models.ManyToManyField(Identifiers, blank=True, related_name="references")
    title = models.TextField(blank=True)
    authors_short = models.TextField(
        blank=True, help_text='Short-text for to display (eg., "Smith et al.")'
    )
    authors = models.TextField(
        blank=True,
        help_text='The complete, comma separated authors list, (eg., "Smith JD, Tom JF, McFarlen PD")',
    )
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    journal = models.TextField(blank=True)
    abstract = models.TextField(blank=True)
    tags = managers.ReferenceFilterTagManager(through=ReferenceTags, blank=True)
    full_text_url = CustomURLField(
        blank=True,
        help_text="Link to full-text URL from journal site (may require increased "
        "access privileges to view)",
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    block_id = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Used internally for determining when reference was " "originally added",
    )

    BREADCRUMB_PARENT = "assessment"

    def update_tags(self, user, tag_pks: list[int]):
        """Update tags for user who requested this tags, and also potentially this reference.

        This method was reviewed to try to reduce the number of db hits required, assuming that
        the reference model has the required select and prefetch related, the tag comparisons
        should not require any additional queries (but it may cause up to 5 db writes).

        Args:
            user: The user requesting the tag changes
            tag_pks (list[int]): A list of tag IDs
        """
        # save user-level tags
        user_tag, _ = self.user_tags.get_or_create(reference=self, user=user)
        user_tag.is_resolved = False
        user_tag.tags.set(tag_pks)
        user_tag.save()

        # determine if we should save the reference-level tags
        update_reference_tags = False
        if self.assessment.literature_settings.conflict_resolution:
            if self.user_tags.count() >= 2:
                tags = set(tag_pks)
                if all(
                    tags == {tag.id for tag in user_tag.tags.all()}
                    for user_tag in self.user_tags.all()
                ):
                    update_reference_tags = True
        else:
            update_reference_tags = True

        # if we should save reference-level tags, do so
        if update_reference_tags:
            self.user_tags.update(is_resolved=True)
            self.tags.set(tag_pks)
            self.last_updated = timezone.now()
            self.save()

    def has_user_tag_conflicts(self):
        return self.user_tags.filter(is_resolved=False).exists()

    def get_absolute_url(self):
        return reverse("lit:ref_detail", args=(self.pk,))

    def __str__(self):
        return self.ref_short_citation

    def to_dict(self):
        d = {}
        fields = (
            "pk",
            "assessment_id",
            "title",
            "authors_short",
            "authors",
            "year",
            "journal",
            "abstract",
            "full_text_url",
            "has_study",
        )
        for field in fields:
            d[field] = getattr(self, field)

        d["url"] = self.get_absolute_url()
        d["editTagUrl"] = reverse("lit:tag", kwargs={"pk": self.assessment_id}) + f"?id={self.pk}"
        d["editReferenceUrl"] = reverse("lit:ref_edit", kwargs={"pk": self.pk})
        d["deleteReferenceUrl"] = reverse("lit:ref_delete", kwargs={"pk": self.pk})
        d["tagHistoryUrl"] = reverse("lit:tag-history", kwargs={"pk": self.pk})
        d["identifiers"] = [ident.to_dict() for ident in self.identifiers.all()]
        d["searches"] = [search.to_dict() for search in self.searches.all()]
        d["study_short_citation"] = self.study.short_citation if d["has_study"] else None

        d["tags"] = [tag.id for tag in self.tags.all()]
        return d

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def delete_caches(cls, ids):
        SerializerHelper.delete_caches(cls, ids)

    @classmethod
    def delete_cache(cls, assessment_id: int, delete_study_cache: bool = True):
        ids = list(cls.objects.filter(assessment_id=assessment_id).values_list("id", flat=True))
        SerializerHelper.delete_caches(cls, ids)
        if delete_study_cache:
            apps.get_model("study", "Study").delete_cache(
                assessment_id, delete_reference_cache=False
            )

    @classmethod
    def update_hero_metadata(cls, assessment_id: int) -> ResultBase:
        """Update reference metadata for all references in an assessment.

        Async worker task; updates data from HERO and then applies new data to references.
        """
        reference_ids = cls.objects.hero_references(assessment_id).values_list("id", flat=True)
        reference_ids = list(reference_ids)  # queryset to list for JSON serializability
        identifiers = Identifiers.objects.filter(
            references__in=reference_ids, database=constants.ReferenceDatabase.HERO
        )
        hero_ids = identifiers.values_list("unique_id", flat=True)
        hero_ids = list(hero_ids)  # queryset to list for JSON serializability

        # update content of hero identifiers
        t1 = tasks.update_hero_content.si(hero_ids)

        # update fields from content
        t2 = tasks.update_hero_fields.si(reference_ids)

        # run chained tasks
        return chain(t1, t2)()

    @property
    def ref_full_citation(self):
        # must be prefixed w/ ref b/c study.Study has the same property
        txt = ""
        for itm in [self.authors, self.title, self.journal]:
            txt += itm
            if (len(itm) > 0) and (itm[-1] != "."):
                txt += ". "
            else:
                txt += " "
        return txt

    @property
    def ref_short_citation(self):
        # must be prefixed w/ ref b/c study.Study has the same property
        # get short citation
        citation = self.authors_short if self.authors_short else "[No authors listed]"

        # get year guess
        year = ""
        if self.year is not None:
            year = str(self.year)
        else:
            m = re.findall(r" (\d+);", self.journal)
            if len(m) > 0:
                year = m[0]

        if year:
            citation += " " + year

        return citation

    @property
    def has_study(self) -> bool:
        return hasattr(self, "study")

    def get_pubmed_id(self):
        for ident in self.identifiers.all():
            if ident.database == constants.ReferenceDatabase.PUBMED:
                return int(ident.unique_id)
        return None

    def get_hero_id(self):
        for ident in self.identifiers.all():
            if ident.database == constants.ReferenceDatabase.HERO:
                return int(ident.unique_id)
        return None

    def get_doi_id(self):
        for ident in self.identifiers.all():
            if ident.database == constants.ReferenceDatabase.DOI:
                return ident.unique_id
        return None

    def update_from_hero_content(self, content: dict, save: bool = False):
        """
        Update reference in place given HERO content; optionally save reference
        """
        # retrieve all of the fields from HERO
        title = content.get("title", "")
        journal = content.get("source", content.get("journaltitle", ""))
        abstract = content.get("abstract", "")
        authors_short = content.get("authors_short", "")
        authors = ", ".join(content.get("authors", []))
        year = content.get("year")

        # set all of the fields on this reference
        setattr(self, "title", title)
        setattr(self, "journal", journal)
        setattr(self, "abstract", abstract)
        setattr(self, "authors_short", authors_short)
        setattr(self, "authors", authors)
        setattr(self, "year", year)

        if save:
            self.save()

    def get_assessment(self):
        return self.assessment

    @classmethod
    def extract_dois(cls, qs, logger=None, full_text: bool = False):
        """Attempt to extract a DOI for each reference given other identifier metadata

        Args:
            qs (Reference QuerySet): a QuerySet of References
            logger (logger): An optional logger instance
            full_text (bool, optional): Determines whether to search full text (True) of field (False; default)
        """
        n = qs.count()
        if n == 0:
            return

        qs_dois = qs.filter(identifiers__database=constants.ReferenceDatabase.DOI)
        n_doi_initial = qs_dois.count()

        qs_no_doi = (
            qs.only("id")
            .exclude(identifiers__database=constants.ReferenceDatabase.DOI)
            .prefetch_related("identifiers")
        )

        new_doi_relations = []
        for ref in qs_no_doi:
            doi = None
            for ident in ref.identifiers.all():
                if full_text:
                    doi = try_get_doi(ident.content, full_text=True)
                else:
                    doi = get_doi_from_identifier(ident)
                if doi:
                    new_doi_relations.append((doi, ref.id))
                    break

        existing_dois = Identifiers.existing_doi_map([el[0] for el in new_doi_relations])
        RefIdentM2M = Reference.identifiers.through

        # create new DOIs as needed
        doi_creates = []
        for doi, _ in new_doi_relations:
            if doi not in existing_dois:
                doi_creates.append(
                    Identifiers(database=constants.ReferenceDatabase.DOI, unique_id=doi)
                )
                existing_dois[doi] = -1  # set temporary value until after bulk_create

        created = Identifiers.objects.bulk_create(doi_creates)
        for ident in created:
            existing_dois[ident.unique_id] = ident.id

        # create new Reference-DOI assignments
        m2m_creates = []
        for doi, ref_id in new_doi_relations:
            ident_id = existing_dois[doi]
            m2m_creates.append(RefIdentM2M(identifiers_id=ident_id, reference_id=ref_id))
        RefIdentM2M.objects.bulk_create(m2m_creates)

        if logger:
            n_doi = qs_dois.count()
            logger.write(f"{n:8} references reviewed ({n_doi_initial/n:.0%} have DOI)")
            logger.write(
                f"{n_doi_initial:8} -> {n_doi:8} references with a DOI (+{n_doi-n_doi_initial}; {n_doi/n:.0%} have DOI)"
            )
            logger.write(
                f"{n-n_doi:8} references remaining without a DOI ({(n-n_doi)/n:.0%} missing DOI)"
            )


class UserReferenceTags(ItemBase):
    objects = managers.UserReferenceTagsManager()

    tag = models.ForeignKey(
        ReferenceFilterTag, on_delete=models.CASCADE, related_name="user_references"
    )
    content_object = models.ForeignKey("UserReferenceTag", on_delete=models.CASCADE)


class UserReferenceTag(models.Model):
    user = models.ForeignKey(HAWCUser, on_delete=models.CASCADE, related_name="reference_tags")
    reference = models.ForeignKey(Reference, on_delete=models.CASCADE, related_name="user_tags")
    tags = managers.ReferenceFilterTagManager(through=UserReferenceTags, blank=True)
    is_resolved = models.BooleanField(
        default=False, help_text="User specific tag differences are resolved for this reference"
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    @property
    def assessment_id(self) -> int:
        return self.reference.assessment_id


reversion.register(LiteratureAssessment)
reversion.register(Search)
reversion.register(Reference)
reversion.register(UserReferenceTag)
