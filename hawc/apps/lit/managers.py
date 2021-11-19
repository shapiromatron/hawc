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

from ...services.epa import hero
from ...services.nih import pubmed
from ..common.helper import HAWCDjangoJSONEncoder
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
            ident = self.filter(database=constants.RIS, unique_id=id_).first()
            if ident:
                ident.update(content=content)
            else:
                ident = self.create(database=constants.RIS, unique_id=id_, content=content)
            ids.append(ident)

            # create DOI identifier
            if constants.DOI_EXTRACT.search(str(ref["doi"])):
                ident, _ = self.get_or_create(
                    database=constants.DOI,
                    unique_id=constants.DOI_EXTRACT.search(str(ref["doi"])).group(0),
                    content="",
                )
                ids.append(ident)

            # create PMID identifier
            # (some may include both an accession number and PMID)
            if ref["PMID"] is not None or db == "nlm":
                id_ = ref["PMID"] or ref["accession_number"]
                if id_ is not None:
                    ident = self.filter(database=constants.PUBMED, unique_id=str(id_)).first()
                    if not ident:
                        ident = self.create(
                            database=constants.PUBMED, unique_id=str(id_), content=""
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
                    ident, _ = self.get_or_create(database=db_id, unique_id=id_, content="")
                    ids.append(ident)

            refs.append(ids)

        Identifiers.update_pubmed_content(pimdsFetch)
        return refs

    def validate_valid_hero_ids(self, ids: List[int]) -> Tuple[List[int], List[int], Dict]:
        qs = self.hero(ids, allow_missing=True).values_list("unique_id", flat=True)
        existing_ids = [int(id_) for id_ in qs]
        remaining_ids = list(set(ids) - set(existing_ids))
        fetcher = hero.HEROFetch(remaining_ids)
        fetched_content = fetcher.get_content()
        if len(fetched_content["failure"]) > 0:
            failed_ids = ",".join(str(el) for el in fetched_content["failure"])
            raise ValidationError(
                f"Import failed; the following HERO IDs could not be imported: {failed_ids}"
            )
        return existing_ids, remaining_ids, fetched_content

    def bulk_create_hero_ids(self, content):
        # sometimes HERO can import two records from a single ID
        deduplicated_content = {item["HEROID"]: item for item in content["success"]}.values()
        self.bulk_create(
            [
                apps.get_model("lit", "Identifiers")(
                    database=constants.HERO,
                    unique_id=str(content["HEROID"]),
                    content=json.dumps(content),
                )
                for content in deduplicated_content
            ]
        )

    def hero(self, hero_ids: List[int], allow_missing=False):
        qs = self.filter(database=constants.HERO, unique_id__in=hero_ids)

        if allow_missing is False and qs.count() != len(hero_ids):
            raise ValueError(
                f"Identifier count ({qs.count()}) does not match ID count ({len(hero_ids)})"
            )

        return qs

    def get_pubmed_identifiers(self, pmids: List[int]):
        """Return a queryset of identifiers, one for each PubMed ID. Either get
        or create an identifier, whatever is required

        Args:
            pmids (List[int]): A list of pubmed identifiers
        """
        #
        Identifiers = apps.get_model("lit", "Identifiers")

        # Filter IDs which need to be imported; we cast to str and back to mirror db fields
        pmids_str = [str(id) for id in pmids]
        existing = list(
            self.filter(database=constants.PUBMED, unique_id__in=pmids_str).values_list(
                "unique_id", flat=True
            )
        )
        need_import = [int(id) for id in set(pmids_str) - set(existing)]

        # Grab Pubmed objects
        fetch = pubmed.PubMedFetch(need_import)

        # Save new Identifier objects
        Identifiers.objects.bulk_create(
            [
                Identifiers(
                    unique_id=str(item["PMID"]),
                    database=constants.PUBMED,
                    content=json.dumps(item),
                )
                for item in fetch.get_content()
            ]
        )

        return self.filter(database=constants.PUBMED, unique_id__in=pmids_str)


class ReferenceManager(BaseManager):

    assessment_relation = "assessment"

    def build_ref_ident_m2m(self, objs):
        # Bulk-create reference-search relationships
        logger.debug("Starting bulk creation of reference-identifer values")
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
            content = json.loads(identifier.content)
            pmid = content.get("PMID", None)
            try:
                doi = content["json"]["doi"]
            except (KeyError):
                doi = None

            if pmid:
                ref = self.get_qs(search.assessment).filter(
                    identifiers__unique_id=str(pmid), identifiers__database=constants.PUBMED
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
            if constants.DOI_EXTRACT.search(str(doi)):
                doi = constants.DOI_EXTRACT.search(doi).group(0)
                doi_id = Identifiers.objects.get_or_create(unique_id=doi)
                ref.identifiers.add(doi_id[0])
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

        Identifiers = apps.get_model("lit", "Identifiers")
        # don't bulkcreate because we need the pks
        for identifier in identifiers:
            try:
                doi = json.loads(identifier.content)["doi"]
            except (KeyError):
                doi = None
            ref = identifier.create_reference(search.assessment)
            ref.save()
            ref.searches.add(search)
            ref.identifiers.add(identifier)
            if constants.DOI_EXTRACT.search(str(doi)):
                doi = constants.DOI_EXTRACT.search(doi).group(0)
                doiIdentifier = Identifiers.objects.get_or_create(unique_id=doi)
                ref.identifiers.add(doiIdentifier[0])
                ref.save()
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

        captured = {None, constants.HERO, constants.PUBMED}
        diff = set(qs.values_list("identifiers__database", flat=True).distinct()) - captured
        if diff:
            logger.warning(f"Missing some identifier IDs from id export: {diff}")

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
                references=models.OuterRef("id"), database=constants.PUBMED
            ).values("unique_id")[:1]
        )
        hero_qs = models.Subquery(
            Identifiers.objects.filter(
                references=models.OuterRef("id"), database=constants.HERO
            ).values("unique_id")[:1]
        )
        doi_qs = models.Subquery(
            Identifiers.objects.filter(
                references=models.OuterRef("id"), database=constants.DOI
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

        tree = ReferenceFilterTag.get_all_tags(assessment_id, json_encode=False)
        tag_qs = ReferenceTags.objects.assessment_qs(assessment_id)
        node_dict = refmltags.build_tree_node_dict(tree)
        df2 = (
            refmltags.create_df(tag_qs, node_dict)
            .rename(columns={"ref_id": "reference id"})
            .set_index("reference id")
        )

        return df1.merge(df2, how="left", left_index=True, right_index=True).reset_index()

    def hero_references(self, assessment_id: int) -> QuerySet:
        return self.assessment_qs(assessment_id).filter(identifiers__database=constants.HERO)


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
