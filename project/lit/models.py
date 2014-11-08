from datetime import datetime
from copy import copy, deepcopy
from math import ceil
import json
import logging
import re
import HTMLParser

from django.db import models
from django.db.models.loading import get_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.html import strip_tags

from taggit.models import ItemBase
from treebeard.mp_tree import MP_Node

from utils.helper import HAWCDjangoJSONEncoder, build_excel_file
from utils.models import NonUniqueTagBase

from fetchers.pubmed import PubMedSearch, PubMedFetch
from fetchers.hero import HEROFetch
from . import managers


SEARCH_SOURCES = ((0, 'Manually imported'),
                  (1, 'PubMed'),
                  (2, 'HERO'))

SEARCH_TYPES = (('s', 'Search'),
                ('i', 'Import'),)

class TooManyPubMedResults(Exception):
    """
    Raised when returned Query is too large
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class Search(models.Model):
    assessment = models.ForeignKey(
        'assessment.Assessment',
        related_name='literature_searches')
    search_type =  models.CharField(
        max_length=1,
        choices=SEARCH_TYPES)
    source = models.PositiveSmallIntegerField(
        choices=SEARCH_SOURCES)
    title = models.CharField(
        max_length=128)
    slug = models.SlugField(
        verbose_name="URL Name",
        help_text="The URL (web address) used to describe this object "
                  "(no spaces or special-characters).")
    description = models.TextField()
    search_string = models.TextField(
        help_text="The exact text used to search using an online database. "
                  "Use colors to separate search-terms (optional).")
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        verbose_name_plural = "searches"
        unique_together = (("assessment", "slug"),
                           ("assessment", "title"))
        ordering = ['-last_updated']
        get_latest_by = ('last_updated', )

    def __unicode__(self):
        return self.title

    def clean(self):
        # unique_together constraint checked above; not done in form because assessment is excluded
        pk_exclusion = {}
        if self.pk:
            pk_exclusion['pk'] = self.pk
        if Search.objects.filter(assessment=self.assessment,
                                 title=self.title).exclude(**pk_exclusion).count() > 0:
            raise ValidationError('Error- title must be unique for assessment.')
        if Search.objects.filter(assessment=self.assessment,
                                 slug=self.slug).exclude(**pk_exclusion).count() > 0:
            raise ValidationError('Error- slug name must be unique for assessment.')

    def get_absolute_url(self):
        return reverse('lit:search_detail', kwargs={'pk': self.assessment.pk,
                                                    'slug': self.slug})

    def get_assessment(self):
        return self.assessment

    @property
    def search_string_text(self):
        # strip all HTML tags from search-string text
        html_parser = HTMLParser.HTMLParser()
        return html_parser.unescape(strip_tags(self.search_string))

    def run_new_query(self):
        if self.source == 1:  # PubMed
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

    def run_new_import(self):
        ids = [int(v) for v in self.search_string_text.split(',')]
        if self.source == 0:  # Manually imported
            raise Exception("Import functionality disabled for manual import")
        elif self.source == 1:  # PubMed
            identifiers = Identifiers.get_pubmed_identifiers(ids)
            Reference.get_pubmed_references(self, identifiers)
        elif self.source == 2:  # HERO
            identifiers = Identifiers.get_hero_identifiers(ids)
            Reference.get_hero_references(self, identifiers)

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
            .filter(assessment=self.assessment,
                    identifiers__unique_id__in=results['added']) \
            .values_list('pk', flat=True)
        ids_count = ref_ids.count()

        if ids_count>0:
            logging.debug("Starting bulk creation of existing search-thorough values")
            ref_searches = []
            for ref in ref_ids:
                ref_searches.append(RefSearchM2M(reference_id=ref,
                                                 search_id=self.pk))
            RefSearchM2M.objects.bulk_create(ref_searches)
            logging.debug("Completed bulk creation of {c} search-thorough values".format(c=len(ref_searches)))


        # For the cases where the search resulted in new ids which may or may
        # not already be imported as a reference for this assessment, find the
        # proper subset.
        ids = Identifiers.objects \
                         .filter(database=self.source, unique_id__in=results['added']) \
                         .exclude(references__in=
                            Reference.objects.filter(assessment=self.assessment)) \
                         .order_by('pk')
        ids_count = ids.count()

        if ids_count>0:
            block_id = datetime.now()

            # create list of references for each identifier
            refs = [ i.create_reference(self.assessment, block_id) for i in ids ]
            id_pks = [ i.pk for i in ids ]

            logging.debug("Starting  bulk creation of {c} references".format(c=len(refs)))
            Reference.objects.bulk_create(refs)
            logging.debug("Completed bulk creation of {c} references".format(c=len(refs)))

            # re-query to get the objects back with PKs
            refs = Reference.objects.filter(assessment=self.assessment,
                                            block_id=block_id).order_by('pk')

            #associate identifiers with each
            ref_searches = []
            ref_ids = []
            logging.debug("Starting  bulk creation of {c} reference-thorough values".format(c=refs.count()))
            for i, ref in enumerate(refs):
                ref_searches.append(RefSearchM2M(reference_id=ref.pk,
                                                 search_id=self.pk))
                ref_ids.append(RefIdM2M(reference_id=ref.pk,
                                        identifiers_id=id_pks[i]))
            RefSearchM2M.objects.bulk_create(ref_searches)
            RefIdM2M.objects.bulk_create(ref_ids)
            logging.debug("Completed bulk creation of {c} reference-thorough values".format(c=refs.count()))

            # finally, remove temporary identifier used for re-query after bulk_create
            logging.debug("Removing block-id from created references")
            refs.update(block_id=None)

    @property
    def date_last_run(self):
        if self.source == 1 and self.search_type == "s":
            try:
                return PubMedQuery.objects.filter(search=self).latest().query_date
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
        s = Search(assessment=assessment,
                   source=0, #manual import
                   search_type='i',
                   title="Manual import",
                   slug="manual-import",
                   description="Default search instance used for manually importing literature into HAWC instead of using a search.",
                   search_string="None. This is used to manually enter literature.")
        s.save()

    @classmethod
    def get_manually_added(cls, assessment):
        try:
            return Search.objects.get(assessment=assessment,
                                      source=0, #manual import
                                      title="Manual import",
                                      slug="manual-import")
        except Exception:
            return None

    def get_all_reference_tags(self, json_encode=True):
        refs = self.references.all().values_list('pk', flat=True)
        ref_objs = list(ReferenceTags.objects.filter(content_object__in=refs).values())
        if json_encode:
            return json.dumps(ref_objs, cls=HAWCDjangoJSONEncoder)
        else:
            return ref_objs

    @property
    def references_count(self):
        return self.references.all().count()

    @property
    def references_tagged_count(self):
        return self.references.all().annotate(tag_count=models.Count('tags')) \
                                .filter(tag_count__gt=0).count()

    @property
    def references_untagged_count(self):
        return self.references.all().annotate(tag_count=models.Count('tags')) \
                                .filter(tag_count=0).count()

    def excel_export(self):
        """
        Full XLS data export for search.
        """
        queryset = self.references.all()
        tags = ReferenceFilterTag.get_all_tags(assessment=self.assessment, json_encode=False)
        sheet_name = self.slug
        return Reference.excel_export(queryset, tags, sheet_name=sheet_name, include_parent_tag=False)


class PubMedQuery(models.Model):
    search = models.ForeignKey(Search)
    results = models.TextField(blank=True)
    query_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "PubMed Queries"
        ordering = ['-query_date']
        get_latest_by = 'query_date'

    def run_new_query(self, prior_query):
        # Create a new search
        search = PubMedSearch(term=self.search.search_string_text)
        search.get_ids_count()

        query_size_limit = 5000
        if search.id_count > query_size_limit:
            raise TooManyPubMedResults("Too many PubMed references found: {0}; reduce query scope to fewer than {1}".format(search.id_count, query_size_limit))

        search.get_ids()
        results = {"ids": search.ids,
                   "added": search.ids,
                   "removed": None}

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
        existing_pmids = list(Identifiers.objects.filter(database=1,
                                                         unique_id__in=new_ids)
                                            .values_list('unique_id', flat=True))
        ids_to_add = list(set(new_ids) - set(existing_pmids))
        ids_to_add_len = len(ids_to_add)

        block_size=1000.
        logging.debug("{c} IDs to be added".format(c=ids_to_add_len))
        for i in xrange(int(ceil(ids_to_add_len/block_size))):
            start_index = int(i*block_size)
            end_index = min(int(i*block_size+block_size), ids_to_add_len)
            logging.debug("Building from {s} to {e}".format(s=start_index, e=end_index))
            fetch = PubMedFetch(id_list=ids_to_add[start_index:end_index],
                                retmax=int(block_size))
            identifiers = []
            for item in fetch.get_content():
                identifiers.append(Identifiers(unique_id=item['PMID'],
                                               database=1,
                                               content=json.dumps(item)))
            Identifiers.objects.bulk_create(identifiers)

    def get_json(self, json_encode=True):

        def get_len(obj):
            if obj is not None:
                return len(obj)
            else: return 0

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
    unique_id = models.IntegerField()
    database = models.IntegerField(choices=SEARCH_SOURCES)
    content = models.TextField()

    class Meta:
        unique_together = (("database", "unique_id"),)

    def __unicode__(self):
        return '{db}: {id}'.format(db=self.database, id=self.unique_id)

    def get_url(self):
        if self.database == 0: # Manually imported
            return 'None'
        elif self.database == 1: # PubMed
            return r'http://www.ncbi.nlm.nih.gov/pubmed/{unique_id}'.format(
                        unique_id=self.unique_id)
        elif self.database == 2: # HERO
            return r'http://hero.epa.gov/index.cfm?action=reference.details&reference_id={unique_id}'.format(
                        unique_id=self.unique_id)

    def create_reference(self, assessment, block_id=None):
        # create, but don't save reference object
        content = json.loads(self.content, encoding='utf-8')
        if self.database == 1:  # PubMed
            ref = Reference(assessment=assessment,
                            title=content.get('title', ""),
                            authors=content.get('authors_short', ""),
                            journal=content.get('citation', ""),
                            abstract=content.get('abstract', ""),
                            year=content.get('year', None),
                            block_id=block_id)
        elif self.database == 2:  # HERO
            ref = Reference(assessment=assessment,
                            title=content.get('title', ""),
                            authors=content.get('authors_short', ""),
                            year=content.get('year', None),
                            journal=content.get('source', ""),
                            abstract=content.get('abstract', ""))
        else:
            raise ValueError("Unknown database for reference creation.")

        return ref

    def get_json(self, json_encode=True):
        return {"id": self.unique_id,
                "database": self.get_database_display(),
                "url": self.get_url()}

    @classmethod
    def get_hero_identifiers(cls, hero_ids):
        # Return a queryset of identifiers, one for each hero ID. Either get or
        # create an identifier, whatever is required

        # Filter HERO IDs to those which need to be imported
        idents = list(Identifiers.objects
                        .filter(database=2, unique_id__in=hero_ids)
                        .values_list('unique_id', flat=True))
        need_import = tuple(set(hero_ids) - set(idents))

        # Grab HERO objects
        fetcher = HEROFetch(need_import)
        fetcher.get_content()

        # Save new Identifier objects
        for content in fetcher.content:
            ident = Identifiers(database=2,
                                unique_id=content["HEROID"],
                                content=json.dumps(content, encoding='utf-8'))
            ident.save()
            idents.append(ident.unique_id)

        return Identifiers.objects.filter(database=2, unique_id__in=idents)

    @classmethod
    def get_pubmed_identifiers(cls, ids):
        # Return a queryset of identifiers, one for each PubMed ID. Either get
        # or create an identifier, whatever is required

        # Filter IDs which need to be imported
        idents = list(Identifiers.objects
                        .filter(database=1, unique_id__in=ids)
                        .values_list('unique_id', flat=True))
        need_import = tuple(set(ids) - set(idents))

        # Grab Pubmed objects
        fetch = PubMedFetch(need_import)

        # Save new Identifier objects
        for item in fetch.get_content():
            ident = Identifiers(unique_id=item['PMID'],
                                database=1,
                                content=json.dumps(item, encoding='utf-8'))
            ident.save()
            idents.append(ident.unique_id)

        return Identifiers.objects.filter(database=1, unique_id__in=idents)


class ReferenceFilterTag(NonUniqueTagBase, MP_Node):
    cache_template_taglist = 'reference-taglist-assessment-{0}'
    cache_template_tagtree = 'reference-tagtree-assessment-{0}'

    @classmethod
    def get_assessment_root_name(cls, assessment_pk):
        return 'assessment-{pk}'.format(pk=assessment_pk)

    @classmethod
    def get_assessment_root(cls, assessment_pk):
        return cls.objects.get(name=cls.get_assessment_root_name(assessment_pk))

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
            tags = cls.dump_bulk(root)
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
        Constructor to define default study-quality metrics.
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
        pos = 'right' if (offset>0) else 'left'
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


class ReferenceTags(ItemBase):
    tag = models.ForeignKey(ReferenceFilterTag, related_name="%(app_label)s_%(class)s_items")
    content_object = models.ForeignKey('Reference')

    #required to be copied when overridden tag object. See GitHub bug report:
    # https://github.com/alex/django-taggit/issues/101
    # copied directly and unchanged from "TaggedItemBase"
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
    assessment = models.ForeignKey('assessment.Assessment', related_name='references')
    searches = models.ManyToManyField(Search, blank=False, related_name='references')
    identifiers = models.ManyToManyField(Identifiers, blank=True, related_name='references')
    title = models.TextField(blank=True)
    authors = models.TextField(blank=True)
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    journal = models.TextField(blank=True)
    abstract = models.TextField(blank=True)
    tags = managers.ReferenceFilterTagManager(through=ReferenceTags, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    block_id = models.DateTimeField(blank=True, null=True, help_text="Used internally for determining when reference was originally added")

    def get_json(self, json_encode=True):
        d = {"identifiers": [], "tags": []}
        fields = ('pk', 'title', 'authors', 'year', 'journal', 'abstract')
        for field in fields:
            d[field] = getattr(self, field)
        for ref in self.identifiers.all():
            d['identifiers'].append(ref.get_json(json_encode=False))

        # ajs todo: refactor JSON to use list of dictionaries instead of two lists
        d['tags'] = list(self.tags.all().values_list('pk', flat=True))
        d['tags_text'] = list(self.tags.all().values_list('name', flat=True))
        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d

    @property
    def reference_citation(self):
        txt = u""
        for itm in [self.authors, self.title, self.journal]:
            txt += itm
            if ((len(itm)>0) and (itm[-1] != ".")):
                txt += ". "
            else:
                txt += " "
        return txt

    def get_short_citation_estimate(self):
        citation = ""

        # get authors guess
        if ((self.authors.find('and')>-1) or (self.authors.find('et al.')>-1)):
            citation = re.sub(r' ([A-Z]{2})','',self.authors) # get rid of initials
        else:
            authors = re.findall(r"[\w']+", self.authors)
            if len(authors)>0:
                citation = authors[0]

        # get year guess
        year = re.findall(r' (\d+);', self.journal)
        if len(year)>0:
            citation += " " + year[0]

        return citation

    def getPubMedID(ref):
        for ident in ref.identifiers.all():
            if ident.database == 1:
                return ident.unique_id
        return None

    @classmethod
    def get_untagged_references(cls, assessment):
        # get all untagged references for the specified assessment.
        refs = Reference.objects.filter(assessment=assessment)
        tagged = list(ReferenceTags.objects.filter(content_object__in=refs)
                                   .values_list('content_object', flat=True))
        return refs.exclude(pk__in=tagged)

    @classmethod
    def get_overview_details(cls, assessment):
        # Get an overview of tagging progress for an assessment
        refs = Reference.objects.filter(assessment=assessment)
        total = refs.count()
        tagged = refs.annotate(tag_count=models.Count('tags')) \
                     .filter(tag_count__gt=0).count()
        overview = {'total_references': total,
                    'total_tagged': tagged,
                    'total_untagged': total-tagged}
        return overview

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
            inclusion_tags = list(root_inclusion.get_descendants() \
                                    .values_list('pk', flat=True))
            inclusion_tags.append(root_inclusion.pk)
        except:
            inclusion_tags=[]
        study_model = get_model('study', 'Study')
        return Reference.objects.filter(assessment=assessment,
                                 referencetags__tag_id__in=inclusion_tags) \
                    .exclude(pk__in=study_model.objects.filter(assessment=assessment)
                              .values_list('pk', flat=True)).distinct()

    @classmethod
    def get_hero_references(cls, search, identifiers):
        """
        Given a list of Identifiers, return a list of references associated
        with each of these identifiers.
        """
        # Get references which already existing and are tied to this identifier
        # but are not associated with the current search and save this search
        # as well to this Reference.
        refs = Reference.objects.filter(assessment=search.assessment,
                                        identifiers__in=identifiers).exclude(searches=search)
        logging.debug("Starting bulk creation of search-thorough values")
        RefSearchM2M = Reference.searches.through
        ref_searches = []
        for ref in refs:
            ref_searches.append(RefSearchM2M(reference_id=ref.pk,
                                             search_id=search.pk))
        RefSearchM2M.objects.bulk_create(ref_searches)

        # get references associated with these identifiers, and get a subset of
        # identifiers which have no reference associated with them
        refs = list(Reference.objects.filter(assessment=search.assessment,
                                             identifiers__in=identifiers))
        if refs:
            identifiers = identifiers.exclude(references__in=refs)

        for identifier in identifiers:
            # check if any identifiers have a pubmed ID that already exists
            # in database. If not, save a new reference.
            content = json.loads(identifier.content, encoding='utf-8')
            ref = Reference.objects.filter(assessment=search.assessment,
                                           identifiers__unique_id=content.get('PMID', None),
                                           identifiers__database=1)  # PubMed

            if ref.count()==1:
                ref = ref[0]
            elif ref.count()>1:
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

        refs = Reference.objects.filter(assessment=search.assessment,
                                        identifiers__in=identifiers).exclude(searches=search)
        logging.debug("Starting bulk creation of search-thorough values")
        RefSearchM2M = Reference.searches.through
        ref_searches = []
        for ref in refs:
            ref_searches.append(RefSearchM2M(reference_id=ref.pk,
                                             search_id=search.pk))
        RefSearchM2M.objects.bulk_create(ref_searches)

        # Get any references which already are associated with these identifiers
        refs = list(Reference.objects.filter(assessment=search.assessment,
                                             identifiers__in=identifiers))

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

    def get_assessment(self):
        return self.assessment

    @classmethod
    def assessment_excel_export(cls, assessment, tag=None):
        # return an excel-export of references for a given assessment, including
        # all-references or only those which have the specified tag.
        queryset = cls.objects.filter(assessment=assessment)
        sheet_name = u'{0}'.format(unicode(assessment))

        # filter references by tag and don't show additional columns
        if tag is not None:
            tags_pks = [tag.pk]
            tags_pks.extend(list(tag.get_descendants().values_list('pk', flat=True)))
            queryset = queryset.filter(tags__in=tags_pks).distinct('pk')
            sheet_name += u'-{0}'.format(tag.name)
            tags = ReferenceFilterTag.dump_bulk(tag)
            include_parent_tag=True
        else:
            # show all tags and all references
            tags = ReferenceFilterTag.get_all_tags(assessment=assessment, json_encode=False)
            include_parent_tag=False

        return cls.excel_export(queryset, tags, sheet_name=sheet_name, include_parent_tag=include_parent_tag)

    @classmethod
    def get_excel_export_header(cls, tags, include_parent_tag):
        headers = ['HAWC ID', 'PubMed ID', 'Citation','Full Citation',
                   'Title', 'Authors', 'Year', 'Journal',  'Abstract']
        if tags:
            headers.extend(ReferenceFilterTag.get_flattened_taglist(tags, include_parent_tag))
        return headers

    @classmethod
    def excel_export(cls, queryset, tags, sheet_name="hawc-reference-export", include_parent_tag=False):
        headers = cls.get_excel_export_header(tags, include_parent_tag)
        data_rows_func = cls.build_excel_rows
        excel = build_excel_file(sheet_name, headers, queryset, data_rows_func, tags=tags, include_parent_tag=include_parent_tag)
        return excel

    @staticmethod
    def build_excel_rows(ws, queryset, *args, **kwargs):
        # build Excel row for each item in queryset

        def resetTags(tags):
            def setFalse(obj):
                obj['isTagged']=False
                for child in obj.get('children', []):
                    setFalse(child)

            tagsCopy = deepcopy(tags)
            setFalse(tagsCopy)
            return tagsCopy

        tags_base = resetTags(kwargs.get('tags')[0])
        include_parent_tag = kwargs.get('include_parent_tag', False)

        def printTags(ws, row, idx, tags):
            col = {'value': idx}
            def printStatus(obj, col):
                ws.write(row, col['value'], obj['isTagged'])
                col['value'] = col['value'] + 1
                for child in obj.get('children', []):
                    printStatus(child, col)

            if include_parent_tag:
                printStatus(tags, col)
            else:
                for child in tags['children']:
                    printStatus(child, col)

        def applyTags(tagslist, ref):

            def applyTag(tagged, tagslist):

                def checkMatch(tagged, tag, parents):
                    parents = copy(parents)
                    if tagged.id == tag['id']:
                        tag['isTagged'] = True
                        for parent in parents:
                            parent['isTagged'] = True

                    parents.append(tag)
                    for child in tag.get('children', []):
                        checkMatch(tagged, child, parents)

                if include_parent_tag:
                    checkMatch(tagged, tagslist, [])
                else:
                    for child in tagslist['children']:
                        checkMatch(tagged, child, [])

            for tag in ref.tags.all():
                applyTag(tag, tagslist)

        row = 0
        for ref in queryset:
            row+=1
            ws.write(row, 0, ref.pk)
            ws.write(row, 1, ref.getPubMedID())
            ws.write(row, 2, ref.get_short_citation_estimate())
            ws.write(row, 3, ref.reference_citation)
            ws.write(row, 4, ref.title)
            ws.write(row, 5, ref.authors)
            ws.write(row, 6, ref.year)
            ws.write(row, 7, ref.journal)
            ws.write(row, 8, strip_tags(ref.abstract))
            tagsCopy = deepcopy(tags_base)
            applyTags(tagsCopy, ref)
            printTags(ws, row, 9, tagsCopy)
