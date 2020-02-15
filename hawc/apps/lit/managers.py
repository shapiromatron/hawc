import json
import logging
from collections import defaultdict
from typing import List

import pandas as pd
from django.apps import apps
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.db.models import QuerySet
from litter_getter import hero, pubmed
from taggit.managers import TaggableManager, _TaggableManager
from taggit.utils import require_instance_manager

from ..common.helper import HAWCDjangoJSONEncoder
from ..common.models import BaseManager
from . import constants


class ReferenceFilterTagManager(TaggableManager):
    def __get__(self, instance, model):
        if instance is not None and instance.pk is None:
            raise ValueError(
                f"{model.__name__} objects need to have a primary key value before you can access their tags."
            )
        manager = _ReferenceFilterTagManager(
            through=self.through, model=model, instance=instance, prefetch_cache_name=self.name,
        )
        return manager


class _ReferenceFilterTagManager(_TaggableManager):
    @require_instance_manager
    def set(self, tag_pks):
        # optimized to reduce queries
        self.clear()

        # make sure we're only using pks for tags with this assessment
        tag_pks = [int(tag) for tag in tag_pks]
        full_taglist = self.through.tag_model().get_descendants_pks(self.instance.assessment_id)
        selected_tags = set(tag_pks).intersection(full_taglist)

        tagrefs = []
        for tag_id in selected_tags:
            tagrefs.append(self.through(tag_id=tag_id, content_object=self.instance))
        self.through.objects.bulk_create(tagrefs)


class SearchManager(BaseManager):
    assessment_relation = "assessment"

    def get_manually_added(self, assessment):
        try:
            return self.get(
                assessment=assessment,
                source=constants.EXTERNAL_LINK,
                title="Manual import",
                slug=self.model.MANUAL_IMPORT_SLUG,
            )
        except Exception:
            return None


class PubMedQueryManager(BaseManager):
    assessment_relation = "search__assessment"


class IdentifiersManager(BaseManager):
    assessment_relation = "references__assessment"

    def get_from_ris(self, search_id, references):
        # Return a queryset of identifiers for each object in RIS file.
        # Expensive; requires a maximum of ~5N queries
        pimdsFetch = []
        refs = []
        Identifiers = apps.get_model("lit", "Identifiers")
        for ref in references:
            ids = []

            db = ref.get("accession_db")
            if db:
                db = db.lower()

            # Create Endnote identifier
            # create id based on search_id and id from RIS file.
            id_ = f"s{search_id}-id{ref['id']}"
            content = json.dumps(ref)
            ident = self.filter(database=constants.RIS, unique_id=id_).first()
            if ident:
                ident.update(content=content)
            else:
                ident = self.create(database=constants.RIS, unique_id=id_, content=content)
            ids.append(ident)

            # create DOI identifier
            if ref["doi"] is not None:
                ident, _ = self.get_or_create(
                    database=constants.DOI, unique_id=ref["doi"], content="None"
                )
                ids.append(ident)

            # create PMID identifier
            # (some may include both an accession number and PMID)
            if ref["PMID"] is not None or db == "nlm":
                id_ = ref["PMID"] or ref["accession_number"]
                if id_ is not None:
                    ident = self.filter(database=constants.PUBMED, unique_id=id_).first()
                    if not ident:
                        ident = self.create(
                            database=constants.PUBMED, unique_id=id_, content="None"
                        )
                        pimdsFetch.append(ident)
                    ids.append(ident)

            # create other accession identifiers
            if (
                db is not None
                and ref["accession_number"] is not None
                and ref["accession_number"] != ""
            ):
                db_id = None
                if db == "wos":
                    db_id = constants.WOS
                elif db == "scopus":
                    db_id = constants.SCOPUS
                elif db == "emb":
                    db_id = constants.EMBASE

                if db_id:
                    id_ = ref["accession_number"]
                    ident, _ = self.get_or_create(database=db_id, unique_id=id_, content="None")
                    ids.append(ident)

            refs.append(ids)

        Identifiers.update_pubmed_content(pimdsFetch)
        return refs

    def get_hero_identifiers(self, hero_ids):
        # Return a queryset of identifiers, one for each hero ID. Either get or
        # create an identifier, whatever is required
        Identifiers = apps.get_model("lit", "Identifiers")
        # Filter HERO IDs to those which need to be imported
        idents = list(
            self.filter(database=constants.HERO, unique_id__in=hero_ids).values_list(
                "unique_id", flat=True
            )
        )
        need_import = tuple(set(hero_ids) - set(idents))

        # Grab HERO objects
        fetcher = hero.HEROFetch(need_import)
        fetcher.get_content()

        # Save new Identifier objects
        for content in fetcher.content:
            ident = Identifiers(
                database=constants.HERO, unique_id=content["HEROID"], content=json.dumps(content),
            )
            ident.save()
            idents.append(ident.unique_id)

        return self.filter(database=constants.HERO, unique_id__in=idents)

    def get_max_external_id(self):
        return self.filter(database=constants.EXTERNAL_LINK).aggregate(models.Max("unique_id"))[
            "unique_id__max"
        ]

    def get_pubmed_identifiers(self, ids):
        # Return a queryset of identifiers, one for each PubMed ID. Either get
        # or create an identifier, whatever is required
        Identifiers = apps.get_model("lit", "Identifiers")
        # Filter IDs which need to be imported
        idents = list(
            self.filter(database=constants.PUBMED, unique_id__in=ids).values_list(
                "unique_id", flat=True
            )
        )
        need_import = tuple(set(ids) - set(idents))

        # Grab Pubmed objects
        fetch = pubmed.PubMedFetch(need_import)

        # Save new Identifier objects
        for item in fetch.get_content():
            ident = Identifiers(
                unique_id=item["PMID"], database=constants.PUBMED, content=json.dumps(item),
            )
            ident.save()
            idents.append(ident.unique_id)

        return self.filter(database=constants.PUBMED, unique_id__in=idents)


class ReferenceManager(BaseManager):
    assessment_relation = "assessment"

    def build_ref_ident_m2m(self, objs):
        # Bulk-create reference-search relationships
        logging.debug("Starting bulk creation of reference-identifer values")
        m2m = self.model.identifiers.through
        objects = [m2m(reference_id=ref_id, identifiers_id=ident_id) for ref_id, ident_id in objs]
        m2m.objects.bulk_create(objects)

    def build_ref_search_m2m(self, refs, search):
        # Bulk-create reference-search relationships
        logging.debug("Starting bulk creation of reference-search values")
        m2m = self.model.searches.through
        objects = [m2m(reference_id=ref.id, search_id=search.id) for ref in refs]
        m2m.objects.bulk_create(objects)

    def delete_orphans(self, assessment_id: int, ref_ids: List[int]):
        """
        Remove orphan references (references with no associated searches). Note that this only
        searches in a given space of reference ids.

        Args:
            assessment_id (int): the assessment to search
            ref_ids (List[int]): list of references to check if orphaned
        """
        orphans = (
            self.get_qs(assessment_id)
            .filter(id__in=ref_ids)
            .only("id")
            .annotate(searches_count=models.Count("searches"))
            .filter(searches_count=0)
        )
        logging.info(f"Removed {orphans.count()} orphan references from assessment {assessment_id}")
        orphans.delete()

    def get_full_assessment_json(self, assessment, json_encode=True):
        ReferenceTags = apps.get_model("lit", "ReferenceTags")
        ref_objs = list(
            ReferenceTags.objects.filter(content_object__in=self.get_qs(assessment))
            .annotate(reference_id=models.F("content_object_id"))
            .values("reference_id", "tag_id")
        )
        if json_encode:
            return json.dumps(ref_objs, cls=HAWCDjangoJSONEncoder)
        else:
            return ref_objs

    def get_hero_references(self, search, identifiers):
        """
        Given a list of Identifiers, return a list of references associated
        with each of these identifiers.
        """
        # Get references which already existing and are tied to this identifier
        # but are not associated with the current search and save this search
        # as well to this Reference.
        refs = (
            self.get_qs(search.assessment)
            .filter(identifiers__in=identifiers)
            .exclude(searches=search)
        )
        self.build_ref_search_m2m(refs, search)

        # get references associated with these identifiers, and get a subset of
        # identifiers which have no reference associated with them
        refs = list(self.get_qs(search.assessment).filter(identifiers__in=identifiers))
        if refs:
            identifiers = identifiers.exclude(references__in=refs)

        for identifier in identifiers:
            # check if any identifiers have a pubmed ID that already exists
            # in database. If not, save a new reference.
            content = json.loads(identifier.content, encoding="utf-8")
            pmid = content.get("PMID", None)

            if pmid:
                ref = self.get_qs(search.assessment).filter(
                    identifiers__unique_id=pmid, identifiers__database=constants.PUBMED
                )
            else:
                ref = self.none()

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

    def get_overview_details(self, assessment):
        # Get an overview of tagging progress for an assessment
        refs = self.get_qs(assessment)
        total = refs.count()
        total_tagged = refs.annotate(tag_count=models.Count("tags")).filter(tag_count__gt=0).count()
        total_untagged = total - total_tagged
        total_searched = refs.filter(searches__search_type="s").distinct().count()
        total_imported = total - total_searched
        overview = {
            "total_references": total,
            "total_tagged": total_tagged,
            "total_untagged": total_untagged,
            "total_searched": total_searched,
            "total_imported": total_imported,
        }
        return overview

    def get_pubmed_references(self, search, identifiers):
        """
        Given a list of Identifiers, return a list of references associated
        with each of these identifiers.
        """
        # Get references which already existing and are tied to this identifier
        # but are not associated with the current search and save this search
        # as well to this Reference.
        refs = (
            self.get_qs(search.assessment)
            .filter(identifiers__in=identifiers)
            .exclude(searches=search)
        )
        self.build_ref_search_m2m(refs, search)

        # Get any references already are associated with these identifiers
        refs = list(self.get_qs(search.assessment).filter(identifiers__in=identifiers))

        # Only process identifiers which have no reference
        if refs:
            identifiers = identifiers.exclude(references__in=refs)

        # don't bulkcreate because we need the pks
        for identifier in identifiers:
            ref = identifier.create_reference(search.assessment)
            ref.save()
            ref.searches.add(search)
            ref.identifiers.add(identifier)
            refs.append(ref)

        return refs

    def get_references_ready_for_import(self, assessment):
        ReferenceFilterTag = apps.get_model("lit", "ReferenceFilterTag")
        Study = apps.get_model("study", "Study")
        try:
            root_inclusion = (
                ReferenceFilterTag.objects.get(name=f"assessment-{assessment.pk}")
                .get_descendants()
                .get(name="Inclusion")
            )
            inclusion_tags = list(root_inclusion.get_descendants().values_list("pk", flat=True))
            inclusion_tags.append(root_inclusion.pk)
        except Exception:
            inclusion_tags = []

        return (
            self.get_qs(assessment)
            .filter(referencetags__tag_id__in=inclusion_tags)
            .exclude(pk__in=Study.objects.get_qs(assessment).values_list("pk", flat=True))
            .distinct()
        )

    def get_references_with_tag(self, tag, descendants=False):
        tag_ids = [tag.id]
        if descendants:
            tag_ids.extend(list(tag.get_descendants().values_list("pk", flat=True)))
        return self.filter(tags__in=tag_ids).distinct("pk")

    def get_untagged_references(self, assessment):
        return self.get_qs(assessment).annotate(tag_count=models.Count("tags")).filter(tag_count=0)

    def process_excel(self, df, assessment_id):
        """
        Expects a data-frame with two columns - HAWC ID and Full text URL
        """
        errors = []

        def fn(d):
            if d["HAWC ID"] in cw and d["Full text URL"] != cw[d["HAWC ID"]]:
                try:
                    validator(d["Full text URL"])
                    self.filter(id=d["HAWC ID"]).update(full_text_url=d["Full text URL"])
                except ValidationError:
                    errors.append(f"HAWC ID {d['HAWC ID']}, invalid URL: {d['Full text URL']}")

        cw = {}
        validator = URLValidator()
        existing = (
            self.get_qs(assessment_id)
            .filter(id__in=df["HAWC ID"].unique())
            .values_list("id", "full_text_url")
        )
        for obj in existing:
            cw[obj[0]] = obj[1]
        df.apply(fn, axis=1)

        return errors

    def update_from_ris_identifiers(self, search, identifiers):
        """
        Create or update Reference from list of lists of identifiers.
        Expensive; each reference requires 4N queries.
        """
        assessment_id = search.assessment_id
        for idents in identifiers:

            # check if existing reference is found
            ref = self.get_qs(assessment_id).filter(identifiers__in=idents).first()

            # find ref if exists and update content
            # first identifier is from RIS file; use this content
            content = json.loads(idents[0].content)
            if ref:
                ref.__dict__.update(
                    title=content["title"],
                    authors=content["authors_short"],
                    year=content["year"],
                    journal=content["citation"],
                    abstract=content["abstract"],
                )
                ref.save()
            else:
                ref = self.create(
                    assessment_id=assessment_id,
                    title=content["title"],
                    authors=content["authors_short"],
                    year=content["year"],
                    journal=content["citation"],
                    abstract=content["abstract"],
                )

            # add all identifiers and searches
            ref.identifiers.add(*idents)
            ref.searches.add(search)

    def identifiers_dataframe(self, qs: QuerySet) -> pd.DataFrame:
        """
        Returns identifiers references for an assessment from external databases or tools.

        Args:
            qs (QuerySet): A queryset

        Returns:
            pd.DataFrame: A pandas dataframe
        """
        qs = qs.prefetch_related("identifiers")

        captured = {None, constants.HERO, constants.PUBMED}
        diff = set(qs.values_list("identifiers__database", flat=True).distinct()) - captured
        if diff:
            logging.warning(f"Missing some identifier IDs from id export: {diff}")

        data = defaultdict(dict)

        # capture HERO ids
        heros = qs.filter(identifiers__database=constants.HERO).values_list(
            "id", "identifiers__unique_id"
        )
        for hawc_id, hero_id in heros:
            data[hawc_id]["hero_id"] = int(hero_id)

        # capture PUBMED ids
        pubmeds = qs.filter(identifiers__database=constants.PUBMED).values_list(
            "id", "identifiers__unique_id"
        )
        for hawc_id, pubmed_id in pubmeds:
            data[hawc_id]["pubmed_id"] = int(pubmed_id)

        # create a dataframe
        df = (
            pd.DataFrame.from_dict(data, orient="index")
            .reset_index()
            .rename(columns={"index": "reference_id"})
        )

        # set missing columns
        for col in ["hero_id", "pubmed_id"]:
            if col not in df.columns:
                df[col] = None

        return df


class ReferenceTagsManager(BaseManager):
    assessment_relation = "content_object__assessment"

    def as_dataframe(self, assessment_id: int) -> pd.DataFrame:
        """
        Returns all reference tag relations for an assessment.

        Args:
            assessment_id (int): Assessment id

        Returns:
            pd.DataFrame: A pandas dataframe
        """
        df = pd.DataFrame(
            data=list(self.assessment_qs(assessment_id).values("tag_id", "content_object_id"))
        )
        df = df.rename(columns=dict(content_object_id="reference_id"))
        return df
