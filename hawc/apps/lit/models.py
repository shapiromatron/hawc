import html
import json
import logging
import re
from datetime import datetime
from math import ceil
from urllib import parse

from django.apps import apps
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models, transaction
from django.utils.html import strip_tags
from litter_getter import pubmed, ris
from taggit.models import ItemBase
from treebeard.mp_tree import MP_Node

from ..common.helper import HAWCDjangoJSONEncoder, SerializerHelper
from ..common.models import AssessmentRootMixin, CustomURLField, NonUniqueTagBase, get_crumbs
from . import constants, managers, tasks


class TooManyPubMedResults(Exception):
    """
    Raised when returned Query is too large
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Search(models.Model):
    objects = managers.SearchManager()

    MANUAL_IMPORT_SLUG = "manual-import"

    SEARCH_TYPES = (
        ("s", "Search"),
        ("i", "Import"),
    )

    assessment = models.ForeignKey("assessment.Assessment", related_name="literature_searches")
    search_type = models.CharField(max_length=1, choices=SEARCH_TYPES)
    source = models.PositiveSmallIntegerField(
        choices=constants.REFERENCE_DATABASES, help_text="Database used to identify literature.",
    )
    title = models.CharField(
        max_length=128, help_text="A brief-description to describe the identified literature.",
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
        return self.search_type == "i" and self.slug == self.MANUAL_IMPORT_SLUG

    def clean(self):
        # unique_together constraint checked above;
        # not done in form because assessment is excluded
        pk_exclusion = {}
        if self.pk:
            pk_exclusion["pk"] = self.pk
        if (
            Search.objects.filter(assessment=self.assessment, title=self.title)
            .exclude(**pk_exclusion)
            .count()
            > 0
        ):
            raise ValidationError("Error- title must be unique for assessment.")
        if (
            Search.objects.filter(assessment=self.assessment, slug=self.slug)
            .exclude(**pk_exclusion)
            .count()
            > 0
        ):
            raise ValidationError("Error- slug name must be unique for assessment.")

    def get_absolute_url(self):
        return reverse("lit:search_detail", kwargs={"pk": self.assessment.pk, "slug": self.slug})

    def get_assessment(self):
        return self.assessment

    def delete(self, **kwargs):
        ref_ids = list(self.references.all().values_list("id", flat=True))
        super().delete(**kwargs)
        Reference.objects.delete_orphans(assessment_id=self.assessment_id, ref_ids=ref_ids)

    @property
    def search_string_text(self):
        return html.unescape(strip_tags(self.search_string))

    @transaction.atomic
    def run_new_query(self):
        if self.source == constants.PUBMED:
            prior_query = None
            try:
                prior_query = PubMedQuery.objects.filter(search=self.pk).latest("query_date")
            except Exception:
                pass
            pubmed = PubMedQuery(search=self)
            results_dictionary = pubmed.run_new_query(prior_query)
            self.create_new_references(results_dictionary)
        else:
            raise Exception("Search functionality disabled")

    @property
    def import_ids(self):
        return [v.strip() for v in self.search_string_text.split(",")]

    @transaction.atomic
    def run_new_import(self):
        if self.source == constants.EXTERNAL_LINK:
            raise Exception("Import functionality disabled for manual import")
        elif self.source == constants.PUBMED:
            identifiers = Identifiers.objects.get_pubmed_identifiers(self.import_ids)
            Reference.objects.get_pubmed_references(self, identifiers)
        elif self.source == constants.HERO:
            identifiers = Identifiers.objects.get_hero_identifiers(self.import_ids)
            Reference.objects.get_hero_references(self, identifiers)
        elif self.source == constants.RIS:
            # check if importer references are cached on object
            refs = getattr(self, "_references", None)
            if refs is None:
                importer = ris.RisImporter(self.import_file.path)
                refs = importer.references
            identifiers = Identifiers.objects.get_from_ris(self.id, refs)
            Reference.objects.update_from_ris_identifiers(self, identifiers)
        else:
            raise ValueError("Unknown import type")

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
        ref_ids = (
            Reference.objects.filter(
                assessment=self.assessment, identifiers__unique_id__in=results["added"]
            )
            .exclude(searches=self)
            .values_list("pk", flat=True)
        )
        ids_count = ref_ids.count()

        if ids_count > 0:
            logging.debug("Starting bulk creation of existing search-thorough values")
            ref_searches = []
            for ref in ref_ids:
                ref_searches.append(RefSearchM2M(reference_id=ref, search_id=self.pk))
            RefSearchM2M.objects.bulk_create(ref_searches)
            logging.debug(f"Completed bulk creation of {len(ref_searches)} search-thorough values")

        # For the cases where the search resulted in new ids which may or may
        # not already be imported as a reference for this assessment, find the
        # proper subset.
        ids = (
            Identifiers.objects.filter(database=self.source, unique_id__in=results["added"])
            .exclude(references__in=Reference.objects.get_qs(self.assessment))
            .order_by("pk")
        )
        ids_count = ids.count()

        if ids_count > 0:
            block_id = datetime.now()

            # create list of references for each identifier
            refs = [i.create_reference(self.assessment, block_id) for i in ids]
            id_pks = [i.pk for i in ids]

            logging.debug(f"Starting  bulk creation of {len(refs)} references")
            Reference.objects.bulk_create(refs)
            logging.debug(f"Completed bulk creation of {len(refs)} references")

            # re-query to get the objects back with PKs
            refs = Reference.objects.filter(assessment=self.assessment, block_id=block_id).order_by(
                "pk"
            )

            # associate identifiers with each
            ref_searches = []
            ref_ids = []
            logging.debug(f"Starting  bulk creation of {refs.count()} reference-thorough values")
            for i, ref in enumerate(refs):
                ref_searches.append(RefSearchM2M(reference_id=ref.pk, search_id=self.pk))
                ref_ids.append(RefIdM2M(reference_id=ref.pk, identifiers_id=id_pks[i]))
            RefSearchM2M.objects.bulk_create(ref_searches)
            RefIdM2M.objects.bulk_create(ref_ids)
            logging.debug(f"Completed bulk creation of {refs.count()} reference-thorough values")

            # finally, remove temporary identifier used for re-query after bulk_create
            logging.debug("Removing block-id from created references")
            refs.update(block_id=None)

    @property
    def date_last_run(self):
        if self.source == constants.PUBMED and self.search_type == "s":
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
            dicts.append(pubmed_query.get_json(json_encode=False))
        return dicts

    def get_all_reference_tags(self, json_encode=True):
        ref_objs = list(
            ReferenceTags.objects.filter(content_object__in=self.references.all())
            .annotate(reference_id=models.F("content_object_id"))
            .values("reference_id", "tag_id")
        )
        if json_encode:
            return json.dumps(ref_objs, cls=HAWCDjangoJSONEncoder)
        else:
            return ref_objs

    def get_references_with_tag(self, tag=None, descendants=False):
        if tag is None:
            return self.references_untagged
        else:
            tag_ids = [tag.id]
            if descendants:
                tag_ids.extend(list(tag.get_descendants().values_list("pk", flat=True)))
            return self.references.filter(tags__in=tag_ids).distinct("pk")

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

    def get_json(self):
        d = {}
        fields = ("pk", "title")
        for field in fields:
            d[field] = getattr(self, field)
        d["url"] = self.get_absolute_url()
        d["search_type"] = self.get_search_type_display()
        return d


class PubMedQuery(models.Model):
    objects = managers.PubMedQueryManager()

    MAX_QUERY_SIZE = 5000

    search = models.ForeignKey(Search)
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

        if search.id_count > self.MAX_QUERY_SIZE:
            raise TooManyPubMedResults(
                "Too many PubMed references found: {0}; reduce query scope to "
                "fewer than {1}".format(search.id_count, self.MAX_QUERY_SIZE)
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
        existing_pmids = list(
            Identifiers.objects.filter(
                database=constants.PUBMED, unique_id__in=new_ids
            ).values_list("unique_id", flat=True)
        )
        ids_to_add = list(set(new_ids) - set(existing_pmids))
        ids_to_add_len = len(ids_to_add)

        block_size = 1000.0
        logging.debug(f"{ids_to_add_len} IDs to be added")
        for i in range(int(ceil(ids_to_add_len / block_size))):
            start_index = int(i * block_size)
            end_index = min(int(i * block_size + block_size), ids_to_add_len)
            logging.debug(f"Building from {start_index} to {end_index}")
            fetch = pubmed.PubMedFetch(
                id_list=ids_to_add[start_index:end_index], retmax=int(block_size)
            )
            identifiers = []
            for item in fetch.get_content():
                identifiers.append(
                    Identifiers(
                        unique_id=item["PMID"], database=constants.PUBMED, content=json.dumps(item),
                    )
                )
            Identifiers.objects.bulk_create(identifiers)

    def get_json(self, json_encode=True):
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
        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d


class Identifiers(models.Model):
    objects = managers.IdentifiersManager()

    unique_id = models.CharField(
        max_length=256, db_index=True
    )  # DOI has no limit; we make this relatively large
    database = models.IntegerField(choices=constants.REFERENCE_DATABASES)
    content = models.TextField()
    url = models.URLField(blank=True)

    class Meta:
        unique_together = (("database", "unique_id"),)
        index_together = (("database", "unique_id"),)

    def __str__(self):
        return f"{self.database}: {self.unique_id}"

    URL_TEMPLATES = {
        constants.PUBMED: r"https://www.ncbi.nlm.nih.gov/pubmed/{0}",
        constants.HERO: r"http://hero.epa.gov/index.cfm?action=reference.details&reference_id={0}",
        constants.DOI: r"https://doi.org/{0}",
        constants.WOS: r"http://apps.webofknowledge.com/InboundService.do?product=WOS&UT={0}&action=retrieve&mode=FullRecord",
        constants.SCOPUS: r"http://www.scopus.com/record/display.uri?eid={0}&origin=resultslist",
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
            content = json.loads(self.content, encoding="utf-8")
        except ValueError:
            if self.database == constants.PUBMED:
                self.update_pubmed_content([self])
            raise AttributeError(f"Content invalid JSON: {self.unique_id}")

        if self.database == constants.PUBMED:
            ref = Reference(
                assessment=assessment,
                title=content.get("title", ""),
                authors=content.get("authors_short", ""),
                journal=content.get("citation", ""),
                abstract=content.get("abstract", ""),
                year=content.get("year", None),
                block_id=block_id,
            )
        elif self.database == constants.HERO:
            # in some cases; my return None, we want "" instead of null
            title = content.get("title")
            journal = content.get("source") or content.get("journaltitle")
            abstract = content.get("abstract", "")
            ref = Reference(
                assessment=assessment,
                title=title or "",
                authors=content.get("authors_short", ""),
                year=content.get("year", None),
                journal=journal or "",
                abstract=abstract or "",
            )
        else:
            raise ValueError("Unknown database for reference creation.")

        return ref

    def get_json(self, json_encode=True):
        return {
            "id": self.unique_id,
            "database": self.get_database_display(),
            "database_id": self.database,
            "url": self.get_url(),
        }

    @staticmethod
    def update_pubmed_content(idents):
        tasks.update_pubmed_content.delay([d.unique_id for d in idents])


class ReferenceFilterTag(NonUniqueTagBase, AssessmentRootMixin, MP_Node):
    cache_template_taglist = "reference-taglist-assessment-{0}"
    cache_template_tagtree = "reference-tagtree-assessment-{0}"

    def get_nested_name(self) -> str:
        if self.is_root():
            return "<root-node>"
        else:
            return f"{'━ ' * (self.depth - 1)}{self.name}"

    @classmethod
    def get_tag_in_assessment(cls, assessment_pk, tag_id):
        tag = cls.objects.get(id=tag_id)
        assert tag.get_root().name == cls.get_assessment_root_name(assessment_pk)
        return tag

    @classmethod
    def build_default(cls, assessment):
        """
        Constructor to define default literature-tags.
        """
        root = cls.add_root(name=cls.get_assessment_root_name(assessment.pk))

        inc = root.add_child(name="Inclusion")
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
            for child in tagslist[0]["children"]:
                appendChildren(child, "")

        return lst


class ReferenceTags(ItemBase):
    objects = managers.ReferenceTagsManager()
    # required to be copied when overridden tag object. See GitHub bug report:
    # https://github.com/alex/django-taggit/issues/101
    # copied directly and unchanged from "TaggedItemBase"
    tag = models.ForeignKey(ReferenceFilterTag, related_name="%(app_label)s_%(class)s_items")
    content_object = models.ForeignKey("Reference")

    @classmethod
    def tags_for(cls, model, instance=None):
        if instance is not None:
            return cls.tag_model().objects.filter(
                **{"%s__content_object" % cls.tag_relname(): instance}
            )
        return (
            cls.tag_model()
            .objects.filter(**{"%s__content_object__isnull" % cls.tag_relname(): False})
            .distinct()
        )


class Reference(models.Model):
    TEXT_CLEANUP_FIELDS = ("full_text_url",)

    objects = managers.ReferenceManager()

    assessment = models.ForeignKey("assessment.Assessment", related_name="references")
    searches = models.ManyToManyField(Search, blank=False, related_name="references")
    identifiers = models.ManyToManyField(Identifiers, blank=True, related_name="references")
    title = models.TextField(blank=True)
    authors = models.TextField(blank=True)
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

    def get_absolute_url(self):
        return reverse("lit:ref_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.get_short_citation_estimate()

    def get_json(self, json_encode=True, searches=False):
        d = {}
        fields = (
            "pk",
            "title",
            "authors",
            "year",
            "journal",
            "abstract",
            "full_text_url",
        )
        for field in fields:
            d[field] = getattr(self, field)

        d["identifiers"] = [ident.get_json(json_encode=False) for ident in self.identifiers.all()]
        if searches:
            d["searches"] = [ref.get_json() for ref in self.searches.all()]

        d["tags"] = list(self.tags.all().values_list("pk", flat=True))
        d["tags_text"] = list(self.tags.all().values_list("name", flat=True))
        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d

    def get_crumbs(self):
        return get_crumbs(self, parent=self.assessment)

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

    @property
    def reference_citation(self):
        txt = ""
        for itm in [self.authors, self.title, self.journal]:
            txt += itm
            if (len(itm) > 0) and (itm[-1] != "."):
                txt += ". "
            else:
                txt += " "
        return txt

    def get_short_citation_estimate(self):
        citation = ""

        # get authors guess
        if (self.authors.find("and") > -1) or (self.authors.find("et al.") > -1):
            citation = re.sub(r" ([A-Z]{2})", "", self.authors)  # remove initials
        else:
            authors = re.findall(r"[\w']+", self.authors)
            if len(authors) > 0:
                citation = authors[0]
            else:
                citation = "[No authors listed]"

        # get year guess
        year = ""
        if self.year is not None:
            year = str(self.year)
        else:
            m = re.findall(r" (\d+);", self.journal)
            if len(m) > 0:
                year = m[0]

        if len(year) > 0:
            citation += " " + year

        return citation

    def get_pubmed_id(ref):
        for ident in ref.identifiers.all():
            if ident.database == constants.PUBMED:
                return int(ident.unique_id)
        return None

    def get_hero_id(ref):
        for ident in ref.identifiers.all():
            if ident.database == constants.HERO:
                return int(ident.unique_id)
        return None

    def set_custom_url(self, url):
        """
        Special-case. Add an Identifier with the selected URL for this reference.
        Only-one custom URL is allowed for each reference; overwrites existing.
        """
        i = self.identifiers.filter(database=constants.EXTERNAL_LINK).first()
        if i:
            i.url = url
            i.save()
        else:
            unique_id = Identifiers.objects.get_max_external_id() + 1
            self.identifiers.add(
                Identifiers.objects.create(
                    database=constants.EXTERNAL_LINK, unique_id=unique_id, url=url
                )
            )

    def get_assessment(self):
        return self.assessment
