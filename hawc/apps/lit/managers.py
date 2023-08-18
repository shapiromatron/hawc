import json
import logging

import pandas as pd
from django.apps import apps
from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.postgres.search import SearchQuery
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Count, Q, QuerySet
from django.db.models.functions import Cast
from taggit.managers import TaggableManager, _TaggableManager
from taggit.utils import require_instance_manager

from hawc.refml import tags as refmltags
from hawc.services.utils.doi import get_doi_from_identifier

from ...services.epa import hero
from ...services.nih import pubmed
from ..assessment.managers import published
from ..common.models import BaseManager, replace_null, str_m2m
from ..study.managers import study_df_annotations
from . import constants

logger = logging.getLogger(__name__)


class ReferenceFilterTagManager(TaggableManager):
    def __get__(self, instance, model):
        if instance is not None and instance.pk is None:
            raise ValueError(
                f"{model.__name__} objects need to have a primary key value before you can access their tags."
            )
        manager = _ReferenceFilterTagManager(
            through=self.through,
            model=model,
            instance=instance,
            prefetch_cache_name=self.name,
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

        if len(selected_tags) < len(tag_pks):
            raise ValueError("At least one of the given tags belongs to a different assessment.")

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


class IdentifiersQuerySet(models.QuerySet):
    def _associate_identifiers(
        self, identifier_to_associated_id: dict, associated_id_to_identifier: dict
    ) -> tuple[dict, list]:
        """
        Creates a dict of identifier to associated identifier given some intermediary dicts.

        Args:
            identifier_to_associated_id (dict): dict of identifier to associated id (ie PubMed/DOI string)
            associated_id_to_identifier (dict): dict of associated ids from first argument to matching identifiers

        Returns:
            tuple[dict, list]: dict of identifier to associated identifier,
                list of identifiers where associated identifier wasn't resolved
        """
        identifier_to_associated_identifier = {}
        missing_identifiers = []

        for identifier, associated_id in identifier_to_associated_id.items():
            found = associated_id in associated_id_to_identifier
            if found:
                identifier_to_associated_identifier[identifier] = associated_id_to_identifier[
                    associated_id
                ]
            else:
                missing_identifiers.append(identifier)
        return identifier_to_associated_identifier, missing_identifiers

    def associated_doi(self, create: bool) -> dict:
        """
        Maps associated DOI identifier with each identifier in this queryset if it exists.

        Args:
            create (bool): Whether to create any missing DOI identifiers

        Returns:
            dict: Mapping of each identifier in this queryset to its associated DOI identifier.
                If the association cannot be resolved, the key is left out.
        """
        # find associated doi ids
        identifier_to_associated_doi = {
            identifier: str(doi)
            for identifier in self
            if (doi := get_doi_from_identifier(identifier))
        }

        # find associated doi identifiers
        doi_identifiers = self.model.objects.filter(
            database=constants.ReferenceDatabase.DOI,
            unique_id__in=identifier_to_associated_doi.values(),
        )
        doi_to_matching_identifier = {
            identifier.unique_id: identifier for identifier in doi_identifiers
        }

        # map identifiers to associated doi identifiers
        identifier_to_associated_identifier, missing_identifiers = self._associate_identifiers(
            identifier_to_associated_doi, doi_to_matching_identifier
        )

        if create and missing_identifiers:
            # create any missing doi identifiers
            missing_doi_identifiers = [
                self.model(
                    database=constants.ReferenceDatabase.DOI,
                    unique_id=identifier_to_associated_doi[identifier],
                )
                for identifier in missing_identifiers
            ]
            created_doi_identifiers = self.model.objects.bulk_create(missing_doi_identifiers)

            # add these new doi identifiers to the association map
            _identifier_to_associated_doi = {
                identifier: identifier_to_associated_doi[identifier]
                for identifier in missing_identifiers
            }
            _doi_to_matching_identifier = {
                identifier.unique_id: identifier for identifier in created_doi_identifiers
            }
            _identifier_to_associated_identifier, _ = self._associate_identifiers(
                _identifier_to_associated_doi, _doi_to_matching_identifier
            )
            identifier_to_associated_identifier.update(_identifier_to_associated_identifier)

        return identifier_to_associated_identifier

    def associated_pubmed(self, create: bool) -> dict:
        """
        Maps associated PubMed identifier with each identifier in this queryset if it exists.

        Args:
            create (bool): Whether to create any missing PubMed identifiers

        Returns:
            dict: Mapping of each identifier in this queryset to its associated PubMed identifier.
                If the association cannot be resolved, the key is left out.
        """
        # find associated pubmed ids
        identifier_to_associated_pubmed = {
            identifier: str(pmid)
            for identifier in self
            if (pmid := identifier.get_content().get("PMID"))
        }

        # find associated pubmed identifiers
        pubmed_identifiers = self.model.objects.filter(
            database=constants.ReferenceDatabase.PUBMED,
            unique_id__in=identifier_to_associated_pubmed.values(),
        )
        pubmed_to_matching_identifier = {
            identifier.unique_id: identifier for identifier in pubmed_identifiers
        }

        # map identifiers to associated pubmed identifiers
        identifier_to_associated_identifier, missing_identifiers = self._associate_identifiers(
            identifier_to_associated_pubmed, pubmed_to_matching_identifier
        )

        if create and missing_identifiers:
            # create any missing pubmed identifiers
            fetcher = pubmed.PubMedFetch(
                [identifier_to_associated_pubmed[identifier] for identifier in missing_identifiers]
            )
            fetched_content = fetcher.get_content()
            created_pubmed_identifiers = self.model.objects.bulk_create_pubmed_ids(fetched_content)

            # add these new pubmed identifiers to the association map
            _identifier_to_associated_pubmed = {
                identifier: identifier_to_associated_pubmed[identifier]
                for identifier in missing_identifiers
            }
            _pubmed_to_matching_identifier = {
                identifier.unique_id: identifier for identifier in created_pubmed_identifiers
            }
            _identifier_to_associated_identifier, _ = self._associate_identifiers(
                _identifier_to_associated_pubmed, _pubmed_to_matching_identifier
            )
            identifier_to_associated_identifier.update(_identifier_to_associated_identifier)

        return identifier_to_associated_identifier


class IdentifiersManager(BaseManager):
    assessment_relation = "references__assessment"

    def get_queryset(self):
        return IdentifiersQuerySet(self.model, using=self._db)

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

    def validate_hero_ids(self, ids: list[int]) -> dict:
        """Queries HERO to return a valid list HERO content which doesn't already exist in HAWC.

        Only queries HERO with identifiers which are not already saved in HAWC.

        Args:
            ids (list[int]): A list of HERO IDs

        Raises:
            ValidationError: Error if input ids are an invalid format, or HERO cannot find a match

        Returns:
            dict: {"success": list[dict], "failures": list[int]}
        """
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

    def hero(self, hero_ids: list[int], allow_missing=False):
        qs = self.filter(database=constants.ReferenceDatabase.HERO, unique_id__in=hero_ids)

        if allow_missing is False and qs.count() != len(hero_ids):
            raise ValueError(
                f"Identifier count ({qs.count()}) does not match ID count ({len(hero_ids)})"
            )

        return qs

    def validate_pubmed_ids(self, ids: list[int]) -> list[dict]:
        """Queries Pubmed to return a valid list Pubmed content which doesn't already exist in HAWC.

        Only queries Pubmed with identifiers which are not already saved in HAWC.

        Args:
            ids (list[int]): A list of PMIDs

        Raises:
            ValidationError: If any PMIDs are non-numeric or if PubMed is unable to find a PMID.

        Returns:
            list[dict]: A list of imported pubmed content
        """
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

    def pubmed(self, pubmed_ids: list[int], allow_missing=False):
        qs = self.filter(database=constants.ReferenceDatabase.PUBMED, unique_id__in=pubmed_ids)

        if allow_missing is False and qs.count() != len(pubmed_ids):
            raise ValueError(
                f"Identifier count ({qs.count()}) does not match ID count ({len(pubmed_ids)})"
            )

        return qs


class ReferenceQuerySet(models.QuerySet):
    def tagged(self):
        return self.annotate(tag_count=models.Count("tags")).exclude(tag_count=0)

    def untagged(self):
        return self.annotate(tag_count=models.Count("tags")).filter(tag_count=0)

    def with_tag(self, tag, descendants: bool = False):
        tag_ids = [tag.id]
        if descendants:
            tag_ids.extend(list(tag.get_descendants().values_list("pk", flat=True)))
        return self.filter(tags__in=tag_ids).distinct("pk")

    def require_tags(self, required_tags, intersection: bool = False, descendants: bool = False):
        """
        Filter references by the given tags.

        Args:
            required_tags (list[ReferenceFilterTag]): Tags to require.
            intersection (bool, optional): Whether all of the tags should be required, or any. Defaults to False.
            descendants (bool, optional): Whether to include descendants under required tags. Defaults to False.
        """
        if not required_tags:
            return self

        if descendants:
            # keep tags and their descendants together; needed if intersection is True
            required_tags = [[tag, *tag.get_descendants()] for tag in required_tags]
        else:
            required_tags = [[tag] for tag in required_tags]

        if intersection:
            query = Q(tags__in=required_tags[0])
            for tags in required_tags[1:]:
                query &= Q(tags__in=tags)
        else:
            query = Q(tags__in=[tag for tags in required_tags for tag in tags])

        return self.filter(query).distinct("pk")

    def prune_tags(self, root_tag, pruned_tags, descendants: bool = False):
        """
        Only prune references if they are tagged by given tags and are not tagged elsewhere
        under a given root tag.

        Args:
            root_tag (ReferenceFilterTag): Place to begin pruning; used to determine references that should remain
            even if tagged by a pruned tag.
            pruned_tags (list[ReferenceFilterTag]): Tags to prune.
            descendants (bool, optional): Whether to include descendants under pruned tags. Defaults to False.
        """
        if not pruned_tags:
            return self

        if descendants:
            pruned_tags = [
                tag
                for tags in [[tag, *tag.get_descendants()] for tag in pruned_tags]
                for tag in tags
            ]

        all_tags = [root_tag, *root_tag.get_descendants()]
        safe_tags = [
            tag for tag in all_tags if all([tag.pk != pruned_tag.pk for pruned_tag in pruned_tags])
        ]
        query = Q(tags__in=[tag.pk for tag in pruned_tags]) & ~Q(
            tags__in=[tag.pk for tag in safe_tags]
        )
        return self.exclude(query).distinct("pk")

    def unresolved_user_tags(self, user_id: int) -> dict[int, list[int]]:
        # Return a dictionary of reference_id: list[tag_ids] items for all references in a queryset
        # TODO - update to annotate queryset with Django 4.1?
        # https://docs.djangoproject.com/en/4.1/ref/contrib/postgres/expressions/#arraysubquery-expressions
        UserReferenceTag = apps.get_model("lit", "UserReferenceTag")
        user_qs = (
            UserReferenceTag.objects.filter(reference__in=self, user=user_id, is_resolved=False)
            .annotate(tag_ids=ArrayAgg("tags__id"))
            .values_list("reference_id", "tag_ids")
        )
        # ArrayAgg can return [None] if some cases; filter to remove
        return {
            reference_id: [tag for tag in tag_ids if tag is not None]
            for reference_id, tag_ids in user_qs
        }

    def global_df(self) -> pd.DataFrame:
        mapping = {
            "ID": "id",
            "PubMed ID": "pmid",
            "HERO ID": "hero",
            "DOI": "doi",
            "Title": "title",
            "Author": "authors_short",
            "Year": "year",
            "Created": "created",
            "Last updated": "last_updated",
            "Tags count": "num_tags",
            "Assessment ID": "assessment",
            "Assessment name": "assessment__name",
            "Assessment year": "assessment__year",
            "Assessment DTXSIDs": "assessment__dtxsids_str",
            "Assessment CAS": "assessment__cas",
            "Assessment published": "published",
            "Assessment creator": replace_null("assessment__creator__email"),
            "Assessment created": "assessment__created",
            "Assessment last updated": "assessment__last_updated",
            "Study citation": replace_null("study__short_citation", "N/A"),
            "Study published": "study__published",
            "Study riskofbias count": "num_robs",
            "Study bioassay": "study__bioassay",
            "Study epi": "study__epi",
            "Study epi meta": "study__epi_meta",
            "Study in vitro": "study__in_vitro",
            "Study ecology": "study__eco",
            "Study created": "study__created",
            "Study last updated": "study__last_updated",
        }

        qs = self.annotate(
            **study_df_annotations(),
            num_tags=Count("tags"),
            num_robs=Count("study__riskofbiases", Q(study__riskofbiases__final=True)),
            assessment__dtxsids_str=str_m2m("assessment__dtxsids"),
            published=published("assessment__"),
        ).values_list(*mapping.values())
        return pd.DataFrame(list(qs), columns=list(mapping.keys()))

    def full_text_search(self, search_text, filters: Q | None = None):
        """Filter queryset using a full text search.

        Args:
            search_text: Text to use in the full text search filter.
            filters: Additional filters to combine with the FTS with an OR. Can be used to add
                identifiers to the search, which are not a part of the Reference model. Defaults to
                None.

        Returns:
            Queryset: The filtered ReferenceQueryset
        """
        query = Q(search=SearchQuery(search_text, search_type="websearch"))
        if filters is None:
            filters = query
        else:
            filters |= query

        return self.annotate(search=constants.REFERENCE_SEARCH_VECTOR).filter(filters)


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

        pubmed_map = identifiers.associated_pubmed(create=True)
        doi_map = identifiers.associated_doi(create=True)

        for identifier in identifiers:
            # check if any identifiers have a pubmed ID that already exists
            # in database. If not, save a new reference.

            if pubmed_identifier := pubmed_map.get(identifier):
                ref = self.get_qs(search.assessment).filter(identifiers=pubmed_identifier)
            else:
                ref = self.none()

            if ref.count() == 1:
                ref = ref[0]
            elif ref.count() > 1:
                raise Exception("Duplicate HERO reference found")
            else:
                ref = identifier.create_reference(search.assessment)
                ref.save()
                if pubmed_identifier:
                    ref.identifiers.add(pubmed_identifier)

            if doi_identifier := doi_map.get(identifier):
                ref.identifiers.add(doi_identifier)
            ref.searches.add(search)
            ref.identifiers.add(identifier)
            refs.append(ref)

        return refs

    def get_overview_details(self, assessment) -> dict[str, int]:
        # Get an overview of tagging progress for an assessment
        refs = self.get_qs(assessment)
        total = refs.count()
        total_tagged = refs.annotate(tag_count=models.Count("tags")).filter(tag_count__gt=0).count()
        total_untagged = total - total_tagged
        total_searched = refs.all().filter(searches__search_type="s").distinct().count()
        total_imported = total - total_searched
        overview = {
            "total_references": total,
            "total_tagged": total_tagged,
            "total_untagged": total_untagged,
            "total_searched": total_searched,
            "total_imported": total_imported,
        }
        if assessment.literature_settings.conflict_resolution:
            UserReferenceTag = apps.get_model("lit", "UserReferenceTag")
            user_refs = UserReferenceTag.objects.filter(reference__in=refs)
            overview.update(
                needs_tagging=(
                    refs.annotate(
                        user_tag_count=Count("user_tags", filter=Q(user_tags__is_resolved=False))
                    )
                    .filter(user_tag_count__lt=2)
                    .count()
                ),
                conflicts=(
                    refs.annotate(
                        n_unapplied_reviews=Count(
                            "user_tags", filter=Q(user_tags__is_resolved=False)
                        )
                    )
                    .filter(n_unapplied_reviews__gt=1)
                    .count()
                ),
                total_reviews=user_refs.count(),
                total_users=user_refs.distinct("user_id").count(),
            )
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

        doi_map = identifiers.associated_doi(create=True)

        # don't bulkcreate because we need the pks
        for identifier in identifiers:
            ref = identifier.create_reference(search.assessment)
            ref.save()
            ref.searches.add(search)
            ref.identifiers.add(identifier)
            if doi_identifier := doi_map.get(identifier):
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

        ids = qs.order_by("id").values_list("id", flat=True)
        pubmed_ids = {
            id: val
            for id, val in qs.filter(identifiers__database=constants.ReferenceDatabase.PUBMED)
            .annotate(int_id=Cast("identifiers__unique_id", models.IntegerField()))
            .values_list("id", "int_id")
        }
        hero_ids = {
            id: val
            for id, val in qs.filter(identifiers__database=constants.ReferenceDatabase.HERO)
            .annotate(int_id=Cast("identifiers__unique_id", models.IntegerField()))
            .values_list("id", "int_id")
        }
        doi_ids = {
            id: val
            for id, val in qs.filter(
                identifiers__database=constants.ReferenceDatabase.DOI
            ).values_list("id", "identifiers__unique_id")
        }

        data = [(id, pubmed_ids.get(id), hero_ids.get(id), doi_ids.get(id)) for id in ids]
        df = pd.DataFrame(data, columns="reference_id pubmed_id hero_id doi".split())

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

    def delete_orphan_tags(self, assessment_id) -> tuple[int, int]:
        """
        Deletes all unreachable tags in an assessment's tag tree.
        An assessment log is created detailing these deleted tags.

        Args:
            assessment_id (int): Assessment id

        Returns:
            tuple[int, int]: Number of tags deleted, followed by log ID.
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


class UserReferenceTagsManager(BaseManager):
    assessment_relation = "content_object__reference__assessment"
