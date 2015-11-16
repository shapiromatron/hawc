from datetime import datetime
from math import ceil
import urllib
import json
import logging
import re
import HTMLParser

from django.db import connection, models, transaction
from django.db.models.loading import get_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import URLValidator
from django.utils.html import strip_tags

from taggit.models import ItemBase
from treebeard.mp_tree import MP_Node

from utils.helper import HAWCDjangoJSONEncoder
from utils.models import NonUniqueTagBase, get_crumbs, CustomURLField

from fetchers.pubmed import PubMedSearch, PubMedFetch
from fetchers.hero import HEROFetch
from fetchers import ris
from . import managers, tasks


EXTERNAL_LINK = 0
PUBMED = 1
HERO = 2
RIS = 3
DOI = 4
WOS = 5
SCOPUS = 6
EMBASE = 7
REFERENCE_DATABASES = (
    (EXTERNAL_LINK, 'External link'),
    (PUBMED, 'PubMed'),
    (HERO, 'HERO'),
    (RIS, 'RIS (Endnote/Refman)'),
    (DOI, 'DOI'),
    (WOS, 'Web of Science'),
    (SCOPUS, 'Scopus'),
    (EMBASE, 'Embase')
)


class TooManyPubMedResults(Exception):
    """
    Raised when returned Query is too large
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Search(models.Model):

    SEARCH_TYPES = (
        ('s', 'Search'),
        ('i', 'Import'),)

    assessment = models.ForeignKey(
        'assessment.Assessment',
        related_name='literature_searches')
    search_type = models.CharField(
        max_length=1,
        choices=SEARCH_TYPES)
    source = models.PositiveSmallIntegerField(
        choices=REFERENCE_DATABASES,
        help_text="Database used to identify literature.")
    title = models.CharField(
        max_length=128,
        help_text="A brief-description to describe the identified literature.")
    slug = models.SlugField(
        verbose_name="URL Name",
        help_text="The URL (web address) used to describe this object "
                  "(no spaces or special-characters).")
    description = models.TextField(
        blank=True,
        help_text="A more detailed description of the literature search or import strategy.")
    search_string = models.TextField(
        blank=True,
        help_text="The search-text used to query an online database. "
                  "Use colors to separate search-terms (optional).")
    import_file = models.FileField(
        upload_to="lit-search-import",
        blank=True)
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        verbose_name_plural = "searches"
        unique_together = (("assessment", "slug"),
                           ("assessment", "title"))
        ordering = ['-last_updated']
        get_latest_by = 'last_updated'

    def __unicode__(self):
        return self.title

    def clean(self):
        # unique_together constraint checked above;
        # not done in form because assessment is excluded
        pk_exclusion = {}
        if self.pk:
            pk_exclusion['pk'] = self.pk
        if Search.objects\
                .filter(assessment=self.assessment, title=self.title)\
                .exclude(**pk_exclusion)\
                .count() > 0:
            raise ValidationError('Error- title must be unique for assessment.')
        if Search.objects\
                .filter(assessment=self.assessment, slug=self.slug)\
                .exclude(**pk_exclusion)\
                .count() > 0:
            raise ValidationError('Error- slug name must be unique for assessment.')

    def get_absolute_url(self):
        return reverse('lit:search_detail', kwargs={'pk': self.assessment.pk,
                                                    'slug': self.slug})

    def get_assessment(self):
        return self.assessment

    def delete(self, **kwargs):
        assessment_pk = self.assessment.pk
        super(Search, self).delete(**kwargs)
        Reference.delete_orphans(assessment_pk)

    @property
    def search_string_text(self):
        # strip all HTML tags from search-string text
        html_parser = HTMLParser.HTMLParser()
        return html_parser.unescape(strip_tags(self.search_string))

    @transaction.atomic
    def run_new_query(self):
        if self.source == PUBMED:
            prior_query = None
            try:
                prior_query = PubMedQuery.objects.filter(search=self.pk).latest('query_date')
            except:
                pass
            pubmed = PubMedQuery(search=self)
            results_dictionary = pubmed.run_new_query(prior_query)
            self.create_new_references(results_dictionary)
        else:
            raise Exception("Search functionality disabled")

    @property
    def import_ids(self):
        return [v.strip() for v in self.search_string_text.split(',')]

    @transaction.atomic
    def run_new_import(self):
        if self.source == EXTERNAL_LINK:
            raise Exception("Import functionality disabled for manual import")
        elif self.source == PUBMED:
            identifiers = Identifiers.get_pubmed_identifiers(self.import_ids)
            Reference.get_pubmed_references(self, identifiers)
        elif self.source == HERO:
            identifiers = Identifiers.get_hero_identifiers(self.import_ids)
            Reference.get_hero_references(self, identifiers)
        elif self.source == RIS:
            # check if importer references are cached on object
            refs = getattr(self, '_references', None)
            if refs is None:
                importer = ris.RisImporter(self.import_file.path)
                refs = importer.references
            identifiers = Identifiers.get_from_ris(self.id, refs)
            Reference.update_from_ris_identifiers(self, identifiers)
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
        ref_ids = Reference.objects \
            .filter(assessment=self.assessment, identifiers__unique_id__in=results['added'])\
            .exclude(searches=self)\
            .values_list('pk', flat=True)
        ids_count = ref_ids.count()

        if ids_count > 0:
            logging.debug("Starting bulk creation of existing search-thorough values")
            ref_searches = []
            for ref in ref_ids:
                ref_searches.append(
                    RefSearchM2M(reference_id=ref, search_id=self.pk))
            RefSearchM2M.objects.bulk_create(ref_searches)
            logging.debug("Completed bulk creation of {c} search-thorough values".format(c=len(ref_searches)))

        # For the cases where the search resulted in new ids which may or may
        # not already be imported as a reference for this assessment, find the
        # proper subset.
        ids = Identifiers.objects\
            .filter(database=self.source, unique_id__in=results['added'])\
            .exclude(references__in=Reference.objects.filter(assessment=self.assessment))\
            .order_by('pk')
        ids_count = ids.count()

        if ids_count > 0:
            block_id = datetime.now()

            # create list of references for each identifier
            refs = [i.create_reference(self.assessment, block_id) for i in ids]
            id_pks = [i.pk for i in ids]

            logging.debug("Starting  bulk creation of {c} references".format(c=len(refs)))
            Reference.objects.bulk_create(refs)
            logging.debug("Completed bulk creation of {c} references".format(c=len(refs)))

            # re-query to get the objects back with PKs
            refs = Reference.objects\
                .filter(assessment=self.assessment, block_id=block_id)\
                .order_by('pk')

            # associate identifiers with each
            ref_searches = []
            ref_ids = []
            logging.debug("Starting  bulk creation of {c} reference-thorough values".format(c=refs.count()))
            for i, ref in enumerate(refs):
                ref_searches.append(
                    RefSearchM2M(reference_id=ref.pk, search_id=self.pk))
                ref_ids.append(
                    RefIdM2M(reference_id=ref.pk, identifiers_id=id_pks[i]))
            RefSearchM2M.objects.bulk_create(ref_searches)
            RefIdM2M.objects.bulk_create(ref_ids)
            logging.debug("Completed bulk creation of {c} reference-thorough values".format(c=refs.count()))

            # finally, remove temporary identifier used for re-query after bulk_create
            logging.debug("Removing block-id from created references")
            refs.update(block_id=None)

    @property
    def date_last_run(self):
        if self.source == PUBMED and self.search_type == "s":
            try:
                return PubMedQuery.objects\
                    .filter(search=self)\
                    .latest().query_date
            except:
                return "Never (not yet run)"
        else:
            return self.last_updated

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

    @classmethod
    def build_default(cls, assessment):
        """
        Constructor to define default search when a new assessment is created.
        """
        Search.objects.create(
            assessment=assessment,
            source=EXTERNAL_LINK,
            search_type='i',
            title="Manual import",
            slug="manual-import",
            description="Default search instance used for manually "
                        "importing literature into HAWC instead of "
                        "using a search.",
            search_string="None. This is used to manually enter literature."
        )

    @classmethod
    def get_manually_added(cls, assessment):
        try:
            return Search.objects.get(assessment=assessment,
                                      source=EXTERNAL_LINK,
                                      title="Manual import",
                                      slug="manual-import")
        except Exception:
            return None

    def get_all_reference_tags(self, json_encode=True):
        refs = self.references.all().values_list('pk', flat=True)
        ref_objs = list(
            ReferenceTags.objects
                .filter(content_object__in=refs).values())
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
                tag_ids.extend(list(tag.get_descendants().values_list('pk', flat=True)))
            return self.references.filter(tags__in=tag_ids).distinct('pk')

    @property
    def references_count(self):
        return self.references.all().count()

    @property
    def references_tagged_count(self):
        return self.references.all()\
                    .annotate(tag_count=models.Count('tags'))\
                    .filter(tag_count__gt=0).count()

    @property
    def references_untagged(self):
        return self.references.all()\
                   .annotate(tag_count=models.Count('tags'))\
                   .filter(tag_count=0)

    def get_json(self):
        d = {}
        fields = ('pk', 'title')
        for field in fields:
            d[field] = getattr(self, field)
        d['url'] = self.get_absolute_url()
        d['search_type'] = self.get_search_type_display()
        return d


class PubMedQuery(models.Model):

    MAX_QUERY_SIZE = 5000

    search = models.ForeignKey(
        Search)
    results = models.TextField(
        blank=True)
    query_date = models.DateTimeField(
        auto_now_add=True)

    class Meta:
        verbose_name_plural = "PubMed Queries"
        ordering = ['-query_date']
        get_latest_by = 'query_date'

    def run_new_query(self, prior_query):
        # Create a new search
        search = PubMedSearch(term=self.search.search_string_text)
        search.get_ids_count()

        if search.id_count > self.MAX_QUERY_SIZE:
            raise TooManyPubMedResults(
                "Too many PubMed references found: {0}; reduce query scope to "
                "fewer than {1}".format(search.id_count, self.MAX_QUERY_SIZE))

        search.get_ids()
        results = {"ids": search.ids,
                   "added": search.ids,
                   "removed": []}

        if prior_query:
            old_ids_list = json.loads(prior_query.results)['ids']
            changes = search.get_changes_from_previous_search(old_ids_list=old_ids_list)
            results['added'] = list(changes['added'])
            results['removed'] = list(changes['removed'])

        self.results = json.dumps(results)
        self.save()
        self.create_identifiers()
        return results

    def create_identifiers(self):
        # Create new PubMed identifiers for any PMIDs which are not already in
        # our database.
        new_ids = json.loads(self.results)['added']
        existing_pmids = list(Identifiers.objects
            .filter(database=PUBMED, unique_id__in=new_ids)
            .values_list('unique_id', flat=True))
        ids_to_add = list(set(new_ids) - set(existing_pmids))
        ids_to_add_len = len(ids_to_add)

        block_size = 1000.
        logging.debug("{0} IDs to be added".format(ids_to_add_len))
        for i in xrange(int(ceil(ids_to_add_len/block_size))):
            start_index = int(i*block_size)
            end_index = min(int(i*block_size+block_size), ids_to_add_len)
            logging.debug("Building from {0} to {1}".format(start_index, end_index))
            fetch = PubMedFetch(id_list=ids_to_add[start_index:end_index],
                                retmax=int(block_size))
            identifiers = []
            for item in fetch.get_content():
                identifiers.append(Identifiers(unique_id=item['PMID'],
                                               database=PUBMED,
                                               content=json.dumps(item)))
            Identifiers.objects.bulk_create(identifiers)

    def get_json(self, json_encode=True):

        def get_len(obj):
            if obj is not None:
                return len(obj)
            else:
                return 0

        details = json.loads(self.results)
        d = {"query_date": self.query_date,
             "total_count": get_len(details["ids"]),
             "total_added": get_len(details["added"]),
             "total_removed": get_len(details["removed"])}
        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d


class Identifiers(models.Model):
    unique_id = models.CharField(
        max_length=256,  # DOI has no limit; we make this relatively large
        db_index=True)
    database = models.IntegerField(
        choices=REFERENCE_DATABASES)
    content = models.TextField()
    url = models.URLField(
        blank=True)

    class Meta:
        unique_together = (("database", "unique_id"),)
        index_together = (("database", "unique_id"),)

    def __unicode__(self):
        return '{db}: {id}'.format(db=self.database, id=self.unique_id)

    URL_TEMPLATES = {
        PUBMED: ur'http://www.ncbi.nlm.nih.gov/pubmed/{0}',
        HERO: ur'http://hero.epa.gov/index.cfm?action=reference.details&reference_id={0}',
        DOI: ur'https://doi.org/{0}',
        WOS: ur'http://apps.webofknowledge.com/InboundService.do?product=WOS&UT={0}&action=retrieve&mode=FullRecord',
        SCOPUS: ur'http://www.scopus.com/record/display.uri?eid={0}&origin=resultslist',
    }

    def get_url(self):
        url = self.url
        template = self.URL_TEMPLATES.get(self.database, None)
        if template:
            url = template.format(urllib.quote(self.unique_id))
        return url

    def create_reference(self, assessment, block_id=None):
        # create, but don't save reference object
        content = json.loads(self.content, encoding='utf-8')
        if self.database == PUBMED:
            ref = Reference(
                assessment=assessment,
                title=content.get('title', ""),
                authors=content.get('authors_short', ""),
                journal=content.get('citation', ""),
                abstract=content.get('abstract', ""),
                year=content.get('year', None),
                block_id=block_id)
        elif self.database == HERO:
            # in some cases; my return None, we want "" instead of null
            title = content.get('title')
            journal = content.get('source') or content.get('journaltitle')
            abstract = content.get('abstract', "")
            ref = Reference(
                assessment=assessment,
                title=title or "",
                authors=content.get('authors_short', ""),
                year=content.get('year', None),
                journal=journal or "",
                abstract=abstract or "")
        else:
            raise ValueError("Unknown database for reference creation.")

        return ref

    def get_json(self, json_encode=True):
        return {
            "id": self.unique_id,
            "database": self.get_database_display(),
            "database_id": self.database,
            "url": self.get_url()
        }

    @classmethod
    def get_hero_identifiers(cls, hero_ids):
        # Return a queryset of identifiers, one for each hero ID. Either get or
        # create an identifier, whatever is required

        # Filter HERO IDs to those which need to be imported
        idents = list(Identifiers.objects
            .filter(database=HERO, unique_id__in=hero_ids)
            .values_list('unique_id', flat=True))
        need_import = tuple(set(hero_ids) - set(idents))

        # Grab HERO objects
        fetcher = HEROFetch(need_import)
        fetcher.get_content()

        # Save new Identifier objects
        for content in fetcher.content:
            ident = Identifiers(database=HERO,
                                unique_id=content["HEROID"],
                                content=json.dumps(content, encoding='utf-8'))
            ident.save()
            idents.append(ident.unique_id)

        return Identifiers.objects.filter(database=HERO, unique_id__in=idents)

    @classmethod
    def get_pubmed_identifiers(cls, ids):
        # Return a queryset of identifiers, one for each PubMed ID. Either get
        # or create an identifier, whatever is required

        # Filter IDs which need to be imported
        idents = list(Identifiers.objects
            .filter(database=PUBMED, unique_id__in=ids)
            .values_list('unique_id', flat=True))
        need_import = tuple(set(ids) - set(idents))

        # Grab Pubmed objects
        fetch = PubMedFetch(need_import)

        # Save new Identifier objects
        for item in fetch.get_content():
            ident = Identifiers(unique_id=item['PMID'],
                                database=PUBMED,
                                content=json.dumps(item, encoding='utf-8'))
            ident.save()
            idents.append(ident.unique_id)

        return Identifiers.objects\
            .filter(database=PUBMED, unique_id__in=idents)

    @classmethod
    def get_from_ris(cls, search_id, references):
        # Return a queryset of identifiers for each object in RIS file.
        # Expensive; requires a maximum of ~5N queries
        pimdsFetch = []
        refs = []
        for ref in references:
            ids = []
            db = ref['accession_db'].lower()
            id_ = ref['accession_number']

            # Create Endnote identifier
            # create id based on search_id and id from RIS file.
            id_ = "s{}-id{}".format(search_id, ref['id'])
            content = json.dumps(ref, encoding='utf8')
            ident = Identifiers.objects\
                .filter(database=RIS, unique_id=id_)\
                .first()
            if ident:
                ident.update(content=content)
            else:
                ident = Identifiers.objects\
                    .create(database=RIS, unique_id=id_, content=content)
            ids.append(ident)

            # create DOI identifier
            if ref["doi"] is not None:
                ident, _ = Identifiers.objects\
                    .get_or_create(database=DOI, unique_id=ref['doi'], content="None")
                ids.append(ident)

            # create PMID identifier
            # (some may include both an accession number and PMID)
            if ref["PMID"] is not None or db == "nlm":
                id_ = ref['PMID'] or ref['accession_number']
                ident = Identifiers.objects\
                    .filter(database=PUBMED, unique_id=id_)\
                    .first()
                if not ident:
                    ident = Identifiers.objects.create(
                        database=PUBMED, unique_id=id_, content="None")
                    pimdsFetch.append(ident)
                ids.append(ident)

            # create other accession identifiers
            if ref['accession_db'] is not None and ref['accession_number'] is not None:
                db_id = None
                if db == "wos":
                    db_id = WOS
                elif db == "scopus":
                    db_id = SCOPUS
                elif db == "emb":
                    db_id = EMBASE

                if db_id:
                    id_ = ref['accession_number']
                    ident, _ = Identifiers.objects\
                                .get_or_create(database=db_id, unique_id=id_, content="None")
                    ids.append(ident)

            refs.append(ids)

        Identifiers.update_pubmed_content(pimdsFetch)

        return refs

    @classmethod
    def update_pubmed_content(cls, idents):
        tasks.update_pubmed_content.delay([d.unique_id for d in idents])

    @classmethod
    def get_max_external_id(cls):
        return cls.objects.filter(database=EXTERNAL_LINK)\
            .aggregate(models.Max('unique_id'))["unique_id__max"]


class ReferenceFilterTag(NonUniqueTagBase, MP_Node):
    cache_template_taglist = 'reference-taglist-assessment-{0}'
    cache_template_tagtree = 'reference-tagtree-assessment-{0}'

    @classmethod
    def get_assessment_root_name(cls, assessment_pk):
        return 'assessment-{pk}'.format(pk=assessment_pk)

    @classmethod
    def get_assessment_root(cls, assessment_pk):
        return cls.objects.get(name=cls.get_assessment_root_name(assessment_pk))

    def get_assessment(self):
        name = self.get_root().name
        Assessment = get_model('assessment', 'Assessment')
        return Assessment.objects.get(pk=int(name[name.find('-')+1:]))

    @classmethod
    def get_tag_in_assessment(cls, assessment_pk, tag_id):
        tag = cls.objects.get(id=tag_id)
        assert tag.get_root().name == cls.get_assessment_root_name(assessment_pk)
        return tag

    @classmethod
    def get_all_tags(cls, assessment, json_encode=True):
        """
        Get all tags for the selected assessment.
        """
        key = cls.cache_template_tagtree.format(assessment.pk)
        tags = cache.get(key)
        if tags:
            logging.info('cache used: {0}'.format(key))
        else:

            root = cls.get_assessment_root(assessment.pk)
            try:
                tags = cls.dump_bulk(root)
            except KeyError as e:
                logging.exception(e)
                cls.clean_orphans()
                tags = cls.dump_bulk(root)
                logging.info("ReferenceFilterTag cleanup successful.")
            cache.set(key, tags)
            logging.info('cache set: {0}'.format(key))

        if json_encode:
            return json.dumps(tags, cls=HAWCDjangoJSONEncoder)
        else:
            return tags

    @classmethod
    def get_descendants_pks(cls, assessment_pk):
        # get a list of keys for assessment descendants
        key = cls.cache_template_taglist.format(assessment_pk)
        descendants = cache.get(key)
        if descendants:
            logging.info('cache used: {0}'.format(key))
        else:
            root = cls.get_assessment_root(assessment_pk)
            descendants = root.get_descendants().values_list('pk', flat=True)
            cache.set(key, descendants)
            logging.info('cache set: {0}'.format(key))
        return descendants

    @classmethod
    def clear_cache(cls, assessment_pk):
        keys = (cls.cache_template_taglist.format(assessment_pk),
                cls.cache_template_tagtree.format(assessment_pk))
        logging.info('removing cache: {0}'.format(', '.join(keys)))
        cache.delete_many(keys)

    @classmethod
    def add_tag(cls, assessment_pk, name, parent_pk=None):
        cls.clear_cache(assessment_pk)
        if parent_pk:
            parent = cls.objects.get(pk=parent_pk)
        else:
            parent = cls.get_assessment_root(assessment_pk)
        new_tag = parent.add_child(name=name)
        return cls.dump_bulk(new_tag)

    @classmethod
    def remove_tag(cls, assessment_pk, pk):
        cls.clear_cache(assessment_pk)
        cls.objects.filter(pk=pk).delete()

    @classmethod
    def build_default(cls, assessment):
        """
        Constructor to define default literature-tags.
        """
        root = cls.add_root(name=cls.get_assessment_root_name(assessment.pk))

        inc = root.add_child(name="Inclusion")
        inc.add_child(name='Human Study')
        inc.add_child(name='Animal Study')
        inc.add_child(name='Mechanistic Study')

        exc = root.add_child(name="Exclusion")
        exc.add_child(name='Tier I')
        exc.add_child(name='Tier II')
        exc.add_child(name='Tier III')

    @classmethod
    def copy_tags(cls, copy_to_assessment, copy_from_assessment):
        # delete existing tags for this assessment
        old_root = cls.get_assessment_root(copy_to_assessment.pk)
        old_root.delete()

        # copy tags from alternative assessment, renaming root-tag
        root = cls.get_assessment_root(copy_from_assessment.pk)
        tags = cls.dump_bulk(root)
        tags[0]['data']['name'] = cls.get_assessment_root_name(copy_to_assessment.pk)
        tags[0]['data']['slug'] = cls.get_assessment_root_name(copy_to_assessment.pk)

        # insert as new taglist
        cls.load_bulk(tags, parent=None, keep_ids=False)
        cls.clear_cache(copy_to_assessment.pk)

    def move_within_parent(self, assessment_pk, offset):
        # move the node within the current parent
        self.clear_cache(assessment_pk)
        siblings = list(self.get_siblings())
        index = siblings.index(self)
        related = siblings[index+offset]
        pos = 'right' if (offset > 0) else 'left'
        self.move(related, pos)

    @classmethod
    def get_flattened_taglist(cls, tagslist, include_parent=True):
        # expects tags dictionary dump_bulk format
        lst = []

        def appendChildren(obj, parents):
            parents = parents + '|' if parents != "" else parents
            txt = parents + obj['data']['name']
            lst.append(txt)
            for child in obj.get('children', []):
                appendChildren(child, txt)

        if include_parent:
            appendChildren(tagslist[0], "")
        else:
            for child in tagslist[0]["children"]:
                appendChildren(child, "")

        return lst

    @classmethod
    def clean_orphans(cls):
        """
        Treebeard can sometimes delete parents but retain orphans; this will
        remove all orphans from the tree.
        """
        logging.warning("ReferenceFilterTag: attempting to recover...")
        problems = ReferenceFilterTag.find_problems()
        ReferenceFilterTag.fix_tree()
        problems = ReferenceFilterTag.find_problems()
        logging.warning("ReferenceFilterTag: problems identified: {}".format(problems))
        orphan_ids = problems[2]
        if len(orphan_ids) > 0:
            cursor = connection.cursor()
            for orphan_id in orphan_ids:
                orphan = cls.objects.get(id=orphan_id)
                logging.warning('ReferenceFilterTag "{}" {} is orphaned [path={}]. Deleting.'.format(
                    orphan.name, orphan.id, orphan.path))
                cursor.execute("DELETE FROM {0} WHERE id = %s".format(cls._meta.db_table), [orphan.id])
            cursor.close()


class ReferenceTags(ItemBase):
    # required to be copied when overridden tag object. See GitHub bug report:
    # https://github.com/alex/django-taggit/issues/101
    # copied directly and unchanged from "TaggedItemBase"
    tag = models.ForeignKey(ReferenceFilterTag, related_name="%(app_label)s_%(class)s_items")
    content_object = models.ForeignKey('Reference')

    @classmethod
    def tags_for(cls, model, instance=None):
        if instance is not None:
            return cls.tag_model().objects.filter(**{
                '%s__content_object' % cls.tag_relname(): instance
            })
        return cls.tag_model().objects.filter(**{
            '%s__content_object__isnull' % cls.tag_relname(): False
        }).distinct()


class Reference(models.Model):
    assessment = models.ForeignKey(
        'assessment.Assessment',
        related_name='references')
    searches = models.ManyToManyField(
        Search,
        blank=False,
        related_name='references')
    identifiers = models.ManyToManyField(
        Identifiers,
        blank=True,
        related_name='references')
    title = models.TextField(
        blank=True)
    authors = models.TextField(
        blank=True)
    year = models.PositiveSmallIntegerField(
        blank=True,
        null=True)
    journal = models.TextField(
        blank=True)
    abstract = models.TextField(
        blank=True)
    tags = managers.ReferenceFilterTagManager(
        through=ReferenceTags,
        blank=True)
    full_text_url = CustomURLField(
        blank=True,
        help_text="Link to full-text publication (may require increased "
                  "access privileges, only reviewers and team-members)")
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)
    block_id = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Used internally for determining when reference was "
                  "originally added")

    def get_absolute_url(self):
        return reverse('lit:ref_detail', kwargs={'pk': self.pk})

    def __unicode__(self):
        return self.get_short_citation_estimate()

    def get_json(self, json_encode=True, searches=False):
        d = {}
        fields = ('pk', 'title', 'authors', 'year',
                  'journal', 'abstract', 'full_text_url')
        for field in fields:
            d[field] = getattr(self, field)

        d['identifiers'] = [
            ident.get_json(json_encode=False)
            for ident in self.identifiers.all()
        ]
        if searches:
            d['searches'] = [ref.get_json() for ref in self.searches.all()]

        d['tags'] = list(self.tags.all().values_list('pk', flat=True))
        d['tags_text'] = list(self.tags.all().values_list('name', flat=True))
        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d

    def get_crumbs(self):
        return get_crumbs(self, parent=self.assessment)

    @property
    def reference_citation(self):
        txt = u""
        for itm in [self.authors, self.title, self.journal]:
            txt += itm
            if ((len(itm) > 0) and (itm[-1] != ".")):
                txt += ". "
            else:
                txt += " "
        return txt

    def get_short_citation_estimate(self):
        citation = u""

        # get authors guess
        if ((self.authors.find('and') > -1) or (self.authors.find('et al.') > -1)):
            citation = re.sub(r' ([A-Z]{2})', '', self.authors)  # remove initials
        else:
            authors = re.findall(r"[\w']+", self.authors)
            if len(authors) > 0:
                citation = authors[0]
            else:
                citation = "[No authors listed]"

        # get year guess
        year = u""
        if self.year is not None:
            year = unicode(self.year)
        else:
            m = re.findall(r' (\d+);', self.journal)
            if len(m) > 0:
                year = m[0]

        if len(year) > 0:
            citation += u" " + year

        return citation

    def getPubMedID(ref):
        for ident in ref.identifiers.all():
            if ident.database == 1:
                return ident.unique_id
        return None

    def set_custom_url(self, url):
        """
        Special-case. Add an Identifier with the selected URL for this reference.
        Only-one custom URL is allowed for each reference; overwrites existing.
        """
        i = self.identifiers.filter(database=EXTERNAL_LINK).first()
        if i:
            i.url = url
            i.save()
        else:
            unique_id = Identifiers.get_max_external_id() + 1
            self.identifiers.add(
                Identifiers.objects.create(
                    database=EXTERNAL_LINK, unique_id=unique_id, url=url))

    @classmethod
    def get_untagged_references(cls, assessment):
        return cls.objects\
                .filter(assessment_id=assessment.id)\
                .annotate(tag_count=models.Count('tags'))\
                .filter(tag_count=0)

    @classmethod
    def get_overview_details(cls, assessment):
        # Get an overview of tagging progress for an assessment
        refs = Reference.objects.filter(assessment=assessment)
        total = refs.count()
        total_tagged = refs.annotate(tag_count=models.Count('tags'))\
            .filter(tag_count__gt=0).count()
        total_untagged = total-total_tagged
        total_searched = refs.filter(searches__search_type='s').distinct().count()
        total_imported = total - total_searched
        overview = {
            'total_references': total,
            'total_tagged': total_tagged,
            'total_untagged': total_untagged,
            'total_searched': total_searched,
            'total_imported': total_imported
        }
        return overview

    @classmethod
    def delete_orphans(cls, assessment_pk):
        # Remove orphan references (references with no associated searches)
        orphans = cls.objects\
                     .filter(assessment=assessment_pk)\
                     .only("id")\
                     .annotate(searches_count=models.Count('searches'))\
                     .filter(searches_count=0)
        logging.info("Removing {} orphan references from assessment {}".format(
                        orphans.count(), assessment_pk))
        orphans.delete()

    @classmethod
    def get_full_assessment_json(cls, assessment, json_encode=True):
        refs = Reference.objects.filter(assessment=assessment).values_list('pk', flat=True)
        ref_objs = list(ReferenceTags.objects.filter(content_object__in=refs).values())
        if json_encode:
            return json.dumps(ref_objs, cls=HAWCDjangoJSONEncoder)
        else:
            return ref_objs

    @classmethod
    def get_references_ready_for_import(cls, assessment):
        try:
            root_inclusion = ReferenceFilterTag.objects \
                .get(name='assessment-{a}'.format(a=assessment.pk)) \
                .get_descendants().get(name='Inclusion')
            inclusion_tags = list(
                root_inclusion.get_descendants().values_list('pk', flat=True))
            inclusion_tags.append(root_inclusion.pk)
        except:
            inclusion_tags = []
        Study = get_model('study', 'Study')

        return Reference.objects\
            .filter(assessment=assessment, referencetags__tag_id__in=inclusion_tags)\
            .exclude(pk__in=
                Study.objects
                    .filter(assessment=assessment)
                    .values_list('pk', flat=True)
            ).distinct()

    @classmethod
    def update_from_ris_identifiers(cls, search, identifiers):
        """
        Create or update Reference from list of lists of identifiers.
        Expensive; each reference requires 4N queries.
        """
        assessment_id = search.assessment_id
        for idents in identifiers:

            # check if existing reference is found
            ref = cls.objects\
                .filter(assessment_id=assessment_id, identifiers__in=idents)\
                .first()

            # find ref if exists and update content
            # first identifier is from RIS file; use this content
            content = json.loads(idents[0].content)
            if ref:
                ref.__dict__.update(
                    title=content['title'],
                    authors=content['authors_short'],
                    year=content['year'],
                    journal=content['citation'],
                    abstract=content['abstract'],
                )
                ref.save()
            else:
                ref = cls.objects.create(
                    assessment_id=assessment_id,
                    title=content['title'],
                    authors=content['authors_short'],
                    year=content['year'],
                    journal=content['citation'],
                    abstract=content['abstract'],
                )

            # add all identifiers and searches
            ref.identifiers.add(*idents)
            ref.searches.add(search)

    @classmethod
    def build_ref_search_m2m(cls, refs, search):
        # Bulk-create reference-search relationships
        logging.debug("Starting bulk creation of reference-search values")
        m2m = Reference.searches.through
        objects = [
            m2m(reference_id=ref.id, search_id=search.id)
            for ref in refs
        ]
        m2m.objects.bulk_create(objects)

    @classmethod
    def build_ref_ident_m2m(cls, objs):
        # Bulk-create reference-search relationships
        logging.debug("Starting bulk creation of reference-identifer values")
        m2m = Reference.identifiers.through
        objects = [
            m2m(reference_id=ref_id, identifiers_id=ident_id)
            for ref_id, ident_id in objs
        ]
        m2m.objects.bulk_create(objects)

    @classmethod
    def get_hero_references(cls, search, identifiers):
        """
        Given a list of Identifiers, return a list of references associated
        with each of these identifiers.
        """
        # Get references which already existing and are tied to this identifier
        # but are not associated with the current search and save this search
        # as well to this Reference.
        refs = Reference.objects\
            .filter(assessment=search.assessment, identifiers__in=identifiers)\
            .exclude(searches=search)
        cls.build_ref_search_m2m(refs, search)

        # get references associated with these identifiers, and get a subset of
        # identifiers which have no reference associated with them
        refs = list(
            Reference.objects
            .filter(assessment=search.assessment, identifiers__in=identifiers)
        )
        if refs:
            identifiers = identifiers.exclude(references__in=refs)

        for identifier in identifiers:
            # check if any identifiers have a pubmed ID that already exists
            # in database. If not, save a new reference.
            content = json.loads(identifier.content, encoding='utf-8')
            pmid = content.get('PMID', None)

            if pmid:
                ref = Reference.objects.filter(
                    assessment=search.assessment,
                    identifiers__unique_id=pmid,
                    identifiers__database=PUBMED)
            else:
                ref = Reference.objects.none()

            if ref.count() == 1:
                ref = ref[0]
            elif ref.count() > 1:
                raise Exception("Duplicate HERO reference found")
            else:
                ref = identifier.create_reference(search.assessment)
                ref.save()

            ref.searches.add(search)
            ref.identifiers.add(identifier)
            refs.append(ref)

        return refs

    @classmethod
    def get_pubmed_references(cls, search, identifiers):
        """
        Given a list of Identifiers, return a list of references associated
        with each of these identifiers.
        """
        # Get references which already existing and are tied to this identifier
        # but are not associated with the current search and save this search
        # as well to this Reference.
        refs = Reference.objects\
            .filter(assessment=search.assessment, identifiers__in=identifiers)\
            .exclude(searches=search)
        cls.build_ref_search_m2m(refs, search)

        # Get any references already are associated with these identifiers
        refs = list(
            Reference.objects
            .filter(assessment=search.assessment, identifiers__in=identifiers)
        )

        # Only process identifiers which have no reference
        if refs:
            identifiers = identifiers.exclude(references__in=refs)

        # don't bulk-create because we need the pks
        for identifier in identifiers:
            ref = identifier.create_reference(search.assessment)
            ref.save()
            ref.searches.add(search)
            ref.identifiers.add(identifier)
            refs.append(ref)

        return refs

    @classmethod
    def get_references_with_tag(cls, tag, descendants=False):
        tag_ids = [tag.id]
        if descendants:
            tag_ids.extend(list(tag.get_descendants().values_list('pk', flat=True)))
        return cls.objects.filter(tags__in=tag_ids).distinct('pk')

    def get_assessment(self):
        return self.assessment

    @classmethod
    def process_excel(cls, df, assessment_id):
        """
        Expects a data-frame with two columns - HAWC ID and Full text URL
        """
        errors = []

        def fn(d):
            if d["HAWC ID"] in cw and d["Full text URL"] != cw[d["HAWC ID"]]:
                try:
                    validator(d["Full text URL"])
                    cls.objects\
                        .filter(id=d["HAWC ID"])\
                        .update(full_text_url=d["Full text URL"])
                except ValidationError:
                    errors.append("HAWC ID {0}, invalid URL: {1}".format(
                        d["HAWC ID"], d["Full text URL"]))

        cw = {}
        validator = URLValidator()
        existing = cls.objects\
            .filter(id__in=df["HAWC ID"].unique(), assessment_id=assessment_id)\
            .values_list('id', 'full_text_url')
        for obj in existing:
            cw[obj[0]] = obj[1]
        df.apply(fn, axis=1)

        return errors
