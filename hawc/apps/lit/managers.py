import json
import logging
from collections import defaultdict
from typing import Dict, List, Tuple

import pandas as pd
from django.apps import apps
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.db.models import QuerySet
from django.db.models.functions import Cast
from taggit.managers import TaggableManager, _TaggableManager
from taggit.utils import require_instance_manager

from hawc.refml import tags as refmltags
from hawc.services.utils.doi import get_doi_from_identifier

from ...services.epa import hero
from ...services.nih import pubmed
from ..common.models import BaseManager
from . import constants

logger = logging.getLogger(__name__)


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
            ident = self.filter(database=constants.ReferenceDatabase.RIS, unique_id=id_).first()
            if ident:
                ident.update(content=content)
            else:
                ident = self.create(
                    database=constants.ReferenceDatabase.RIS, unique_id=id_, content=content
                )
            ids.append(ident)

            # create DOI identifier
            if doi := get_doi_from_identifier(ident):
                ident, _ = self.get_or_create(
                    database=constants.ReferenceDatabase.DOI, unique_id=doi
                )
                ids.append(ident)

            # create PMID identifier
            # (some may include both an accession number and PMID)
            if ref["PMID"] is not None or db == "nlm":
                id_ = ref["PMID"] or ref["accession_number"]
                if id_ is not None:
                    ident = self.filter(
                        database=constants.ReferenceDatabase.PUBMED, unique_id=str(id_)
                    ).first()
                    if not ident:
                        ident = self.create(
                            database=constants.ReferenceDatabase.PUBMED,
                            unique_id=str(id_),
                            content="",
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
                    db_id = constants.ReferenceDatabase.WOS
                elif db == "scopus":
                    db_id = constants.ReferenceDatabase.SCOPUS
                elif db == "emb":
                    db_id = constants.ReferenceDatabase.EMBASE

                if db_id:
                    id_ = ref["accession_number"]
                    ident, _ = self.get_or_create(database=db_id, unique_id=id_, content="")
                    ids.append(ident)

            refs.append(ids)

        Identifiers.update_pubmed_content(pimdsFetch)
        return refs

    def validate_hero_ids(self, ids: List[int]) -> Dict:
        # cast all ids to int
        invalid_ids = []
        _ids = []
        for id in ids:
            try:
                _ids.append(int(id))
            except ValueError:
                invalid_ids.append(id)
        if invalid_ids:
            invalid_join = ", ".join(str(id) for id in invalid_ids)
            raise ValidationError(f"The following HERO ID(s) are not integers: {invalid_join}")

        # determine which ids do not already exist
        qs = self.hero(_ids, allow_missing=True).values_list("unique_id", flat=True)
        existing_ids = [int(id) for id in qs]
        remaining_ids = list(set(_ids) - set(existing_ids))

        # fetch missing ids
        fetcher = hero.HEROFetch(remaining_ids)
        fetched_content = fetcher.get_content()
        if len(fetched_content["failure"]) > 0:
            failed_join = ", ".join(str(el) for el in fetched_content["failure"])
            raise ValidationError(f"The following HERO ID(s) could not be imported: {failed_join}")
        return fetched_content

    def bulk_create_hero_ids(self, content):
        # sometimes HERO can import two records from a single ID
        deduplicated_content = {item["HEROID"]: item for item in content["success"]}.values()
        return self.bulk_create(
            [
                apps.get_model("lit", "Identifiers")(
                    database=constants.ReferenceDatabase.HERO,
                    unique_id=str(content["HEROID"]),
                    content=json.dumps(content),
                )
                for content in deduplicated_content
            ]
        )

    def hero(self, hero_ids: List[int], allow_missing=False):
        qs = self.filter(database=constants.ReferenceDatabase.HERO, unique_id__in=hero_ids)

        if allow_missing is False and qs.count() != len(hero_ids):
            raise ValueError(
                f"Identifier count ({qs.count()}) does not match ID count ({len(hero_ids)})"
            )

        return qs

    def validate_pubmed_ids(self, ids: List[int]):
        # cast all ids to int
        invalid_ids = []
        _ids = []
        for id in ids:
            try:
                _ids.append(int(id))
            except ValueError:
                invalid_ids.append(id)
        if invalid_ids:
            invalid_join = ", ".join(str(id) for id in invalid_ids)
            raise ValidationError(f"The following PubMed ID(s) are not integers: {invalid_join}")

        # determine which ids do not already exist
        qs = self.pubmed(_ids, allow_missing=True).values_list("unique_id", flat=True)
        existing_ids = [int(id) for id in qs]
        remaining_ids = list(set(_ids) - set(existing_ids))

        # fetch missing ids
        fetcher = pubmed.PubMedFetch(remaining_ids)
        fetched_content = fetcher.get_content()
        if failed_ids := set(remaining_ids) - {int(item["PMID"]) for item in fetched_content}:
            failed_join = ", ".join(str(id) for id in failed_ids)
            raise ValidationError(
                f"The following PubMed ID(s) could not be imported: {failed_join}"
            )

        return fetched_content

    def bulk_create_pubmed_ids(self, content):
        Identifiers = apps.get_model("lit", "Identifiers")

        # Save new Identifier objects
        return Identifiers.objects.bulk_create(
            [
                Identifiers(
                    unique_id=str(item["PMID"]),
                    database=constants.ReferenceDatabase.PUBMED,
                    content=json.dumps(item),
                )
                for item in content
            ]
        )

    def pubmed(self, pubmed_ids: List[int], allow_missing=False):
        qs = self.filter(database=constants.ReferenceDatabase.PUBMED, unique_id__in=pubmed_ids)

        if allow_missing is False and qs.count() != len(pubmed_ids):
            raise ValueError(
                f"Identifier count ({qs.count()}) does not match ID count ({len(pubmed_ids)})"
            )

        return qs


class ReferenceQuerySet(models.QuerySet):
    def untagged(self):
        return self.annotate(tag_count=models.Count("tags")).filter(tag_count=0)

    def with_tag(self, tag, descendants: bool = False):
        tag_ids = [tag.id]
        if descendants:
            tag_ids.extend(list(tag.get_descendants().values_list("pk", flat=True)))
        return self.filter(tags__in=tag_ids).distinct("pk")


class ReferenceManager(BaseManager):

    assessment_relation = "assessment"

    def get_queryset(self):
        return ReferenceQuerySet(self.model, using=self._db)

    def build_ref_ident_m2m(self, objs):
        # Bulk-create reference-search relationships
        logger.debug("Starting bulk creation of reference-identifier values")
        m2m = self.model.identifiers.through
        objects = [m2m(reference_id=ref_id, identifiers_id=ident_id) for ref_id, ident_id in objs]
        m2m.objects.bulk_create(objects)

    def build_ref_search_m2m(self, refs, search):
        # Bulk-create reference-search relationships
        logger.debug("Starting bulk creation of reference-search values")
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
        logger.info(f"Removed {orphans.count()} orphan references from assessment {assessment_id}")
        orphans.delete()

    def tag_pairs(self, qs):
        # get reference tag pairs
        ReferenceTags = apps.get_model("lit", "ReferenceTags")
        return list(
            ReferenceTags.objects.filter(content_object__in=qs)
            .annotate(reference_id=models.F("content_object_id"))
            .values("reference_id", "tag_id")
        )

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
            content = json.loads(identifier.content)
            pmid = content.get("PMID", None)

            if pmid:
                ref = self.get_qs(search.assessment).filter(
                    identifiers__unique_id=str(pmid),
                    identifiers__database=constants.ReferenceDatabase.PUBMED,
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

            Identifiers = apps.get_model("lit", "Identifiers")
            if doi := get_doi_from_identifier(identifier):
                doi_id, _ = Identifiers.objects.get_or_create(
                    unique_id=doi, database=constants.ReferenceDatabase.DOI
                )
                ref.identifiers.add(doi_id)
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

        Identifiers = apps.get_model("lit", "Identifiers")
        # don't bulkcreate because we need the pks
        for identifier in identifiers:
            ref = identifier.create_reference(search.assessment)
            ref.save()
            ref.searches.add(search)
            ref.identifiers.add(identifier)
            if doi := get_doi_from_identifier(identifier):
                doi_identifier, _ = Identifiers.objects.get_or_create(
                    unique_id=doi, database=constants.ReferenceDatabase.DOI
                )
                ref.identifiers.add(doi_identifier)
            refs.append(ref)

        return refs

    def get_references_ready_for_import(self, assessment):
        Study = apps.get_model("study", "Study")

        root_inclusion = assessment.literature_settings.extraction_tag
        inclusion_tags = []
        if root_inclusion:
            inclusion_tags = list(root_inclusion.get_descendants().values_list("pk", flat=True))
            inclusion_tags.append(root_inclusion.pk)
            return (
                self.get_qs(assessment)
                .filter(referencetags__tag_id__in=inclusion_tags)
                .exclude(pk__in=Study.objects.get_qs(assessment).values_list("pk", flat=True))
                .order_by("authors")
                .distinct()
            )
        else:
            return self.none()

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
            data = dict(
                title=content["title"],
                authors_short=content["authors_short"],
                authors=", ".join(content["authors"]),
                year=content["year"],
                journal=content["citation"],
                abstract=content["abstract"],
            )
            if ref:
                for key, value in data.items():
                    setattr(ref, key, value)
                ref.save()
            else:
                data["assessment_id"] = assessment_id
                ref = self.create(**data)

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

        captured = {
            None,
            constants.ReferenceDatabase.HERO,
            constants.ReferenceDatabase.PUBMED,
            constants.ReferenceDatabase.DOI,
        }
        diff = set(qs.values_list("identifiers__database", flat=True).distinct()) - captured
        if diff:
            logger.warning(f"Missing some identifier IDs from id export: {diff}")

        data = defaultdict(dict)

        # capture HERO ids
        heros = qs.filter(identifiers__database=constants.ReferenceDatabase.HERO).values_list(
            "id", "identifiers__unique_id"
        )
        for hawc_id, hero_id in heros:
            data[hawc_id]["hero_id"] = int(hero_id)

        # capture PUBMED ids
        pubmeds = qs.filter(identifiers__database=constants.ReferenceDatabase.PUBMED).values_list(
            "id", "identifiers__unique_id"
        )
        for hawc_id, pubmed_id in pubmeds:
            data[hawc_id]["pubmed_id"] = int(pubmed_id)

        # capture DOI ids
        dois = qs.filter(identifiers__database=constants.ReferenceDatabase.DOI).values_list(
            "id", "identifiers__unique_id"
        )
        for hawc_id, doi_id in dois:
            data[hawc_id]["doi_id"] = doi_id

        # create a dataframe
        df = (
            pd.DataFrame.from_dict(data, orient="index")
            .reset_index()
            .rename(columns={"index": "reference_id"})
        )

        # set missing columns
        for col in ["hero_id", "pubmed_id", "doi_id"]:
            if col not in df.columns:
                df[col] = None

        return df

    def heatmap_dataframe(self, assessment_id: int) -> pd.DataFrame:
        Identifiers = apps.get_model("lit", "Identifiers")
        ReferenceFilterTag = apps.get_model("lit", "ReferenceFilterTag")
        ReferenceTags = apps.get_model("lit", "ReferenceTags")

        values = dict(
            id="reference id",
            hero_id="hero id",
            pubmed_id="pubmed id",
            doi="doi",
            authors_short="authors short",
            authors="authors",
            title="title",
            year="year",
            journal="journal",
        )
        pubmed_qs = models.Subquery(
            Identifiers.objects.filter(
                references=models.OuterRef("id"), database=constants.ReferenceDatabase.PUBMED
            ).values("unique_id")[:1]
        )
        hero_qs = models.Subquery(
            Identifiers.objects.filter(
                references=models.OuterRef("id"), database=constants.ReferenceDatabase.HERO
            ).values("unique_id")[:1]
        )
        doi_qs = models.Subquery(
            Identifiers.objects.filter(
                references=models.OuterRef("id"), database=constants.ReferenceDatabase.DOI
            ).values("unique_id")[:1]
        )
        qs = (
            self.filter(assessment_id=assessment_id)
            .annotate(pubmed_id=Cast(pubmed_qs, models.IntegerField()))
            .annotate(hero_id=Cast(hero_qs, models.IntegerField()))
            .annotate(doi=doi_qs)
            .values_list(*values.keys())
            .order_by("id")
        )
        df1 = pd.DataFrame(data=qs, columns=values.values()).set_index("reference id")

        # build full citation column
        # TODO - replace `ref_full_citation`?
        df1["full citation"] = (
            (
                df1.authors
                + "|"
                + df1.year.fillna(-999).astype(int).astype(str)
                + "|"
                + df1.title
                + "|"
                + df1.journal
            )
            .str.replace(r"-999", "", regex=True)  # remove flag number
            .str.replace(r"^\|+|\|+$", "", regex=True)  # remove pipes at beginning/end
            .str.replace("|", ". ", regex=False)  # change pipes to periods
        )

        tree = ReferenceFilterTag.get_all_tags(assessment_id)
        tag_qs = ReferenceTags.objects.assessment_qs(assessment_id)
        node_dict = refmltags.build_tree_node_dict(tree)
        df2 = (
            refmltags.create_df(tag_qs, node_dict)
            .rename(columns={"ref_id": "reference id"})
            .set_index("reference id")
        )

        return df1.merge(df2, how="left", left_index=True, right_index=True).reset_index()

    def hero_references(self, assessment_id: int) -> QuerySet:
        return self.assessment_qs(assessment_id).filter(
            identifiers__database=constants.ReferenceDatabase.HERO
        )


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
        qs = self.assessment_qs(assessment_id).values("content_object_id", "tag_id")
        df = pd.DataFrame(columns=["reference_id", "tag_id"])
        if qs.count() > 0:
            df = pd.DataFrame(data=list(qs))
            df = df.rename(columns=dict(content_object_id="reference_id")).sort_values(
                by=["reference_id", "tag_id"]
            )
        return df

    def get_assessment_qs(self, assessment_id: int):
        return self.get_queryset().filter(content_object__assessment_id=assessment_id)

    def delete_orphan_tags(self, assessment_id) -> Tuple[int, int]:
        """
        Deletes all unreachable tags in an assessment's tag tree.
        An assessment log is created detailing these deleted tags.

        Args:
            assessment_id (int): Assessment id

        Returns:
            Tuple[int, int]: Number of tags deleted, followed by log ID.
        """
        from .models import ReferenceFilterTag

        # queryset of tag tree associated with assessment
        filter_tags = ReferenceFilterTag.get_assessment_qs(assessment_id)
        # queryset of tags associated with assessment
        tags = self.get_assessment_qs(assessment_id)
        # delete tags that are not in the assessment tag tree
        deleted_tags = tags.exclude(tag__in=filter_tags)
        deleted_data = list(deleted_tags.values("content_object_id", "tag_id"))
        number_deleted, _ = deleted_tags.delete()
        # log the deleted tags
        Log = apps.get_model("assessment", "Log")
        log = Log.objects.create(
            assessment_id=assessment_id,
            message=json.dumps({"count": number_deleted, "data": deleted_data}),
        )
        return number_deleted, log.id
