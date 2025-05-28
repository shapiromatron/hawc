import pandas as pd
from django.apps import apps
from django.db import models
from django.db.models import Case, Exists, F, OuterRef, Q, QuerySet, Value, When
from django.db.models.functions import Concat

from ..common.models import BaseManager, sql_display, str_m2m
from ..lit.constants import ReferenceDatabase
from . import constants


def study_df_annotations(prefix: str = "") -> dict:
    return {
        "pmid": str_m2m(
            f"{prefix}identifiers__unique_id",
            filter=Q(**{f"{prefix}identifiers__database": ReferenceDatabase.PUBMED}),
        ),
        "hero": str_m2m(
            f"{prefix}identifiers__unique_id",
            filter=Q(**{f"{prefix}identifiers__database": ReferenceDatabase.HERO}),
        ),
        "doi": str_m2m(
            f"{prefix}identifiers__unique_id",
            filter=Q(**{f"{prefix}identifiers__database": ReferenceDatabase.DOI}),
        ),
    }


def study_df_mapping(key_prefix: str = "", query_prefix: str = "") -> dict:
    return {
        f"{key_prefix}id": f"{query_prefix}id",
        f"{key_prefix}PMID": "pmid",
        f"{key_prefix}HERO ID": "hero",
        f"{key_prefix}DOI": "doi",
        f"{key_prefix}short_citation": f"{query_prefix}short_citation",
        f"{key_prefix}full_citation": f"{query_prefix}full_citation",
        f"{key_prefix}coi_reported": sql_display(
            f"{query_prefix}coi_reported", constants.CoiReported
        ),
        f"{key_prefix}coi_details": f"{query_prefix}coi_details",
        f"{key_prefix}funding_source": f"{query_prefix}funding_source",
        f"{key_prefix}study_identifier": f"{query_prefix}study_identifier",
        f"{key_prefix}contact_author": f"{query_prefix}contact_author",
        f"{key_prefix}ask_author": f"{query_prefix}ask_author",
        f"{key_prefix}published": f"{query_prefix}published",
        f"{key_prefix}summary": f"{query_prefix}summary",
    }


class StudyQuerySet(QuerySet):
    def flat_df(self) -> pd.DataFrame:
        return pd.DataFrame(
            data=self.annotate(**study_df_annotations()).values_list(*study_df_mapping().values()),
            columns=list(study_df_mapping().keys()),
        )

    def published_only(self, published_only: bool):
        """If True, return only published studies. If False, all studies"""
        return self.filter(published=True) if published_only else self

    def clone_annotations(self):
        return self.annotate(
            has_rob=Exists(
                apps.get_model("riskofbias", "RiskOfBias").objects.filter(study=OuterRef("pk"))
            ),
            has_bioassay=Exists(
                apps.get_model("animal", "Experiment").objects.filter(study=OuterRef("pk"))
            ),
            has_epi=Exists(apps.get_model("epiv2", "Design").objects.filter(study=OuterRef("pk"))),
        )


class StudyManager(BaseManager):
    assessment_relation = "assessment"

    def get_queryset(self):
        return StudyQuerySet(self.model, using=self._db)

    def published(self, assessment_id=None):
        return self.get_qs(assessment_id).filter(published=True)

    def get_choices(self, assessment_id: int, data_type: str = ""):
        qs = (
            self.get_qs(assessment_id)
            .annotate(
                label=Concat(
                    F("short_citation"),
                    Case(When(published=False, then=Value(" (unpublished)")), default=Value("")),
                )
            )
            .values_list("id", "label")
        )
        if data_type:
            qs = qs.filter(**{data_type: True})
        return qs

    def rob_scores(self, assessment_id=None):
        return (
            self.get_qs(assessment_id)
            .annotate(
                final_score=models.Sum(
                    models.Case(
                        models.When(
                            riskofbiases__active=True,
                            riskofbiases__final=True,
                            then="riskofbiases__scores__score",
                        ),
                        default=0,
                    )
                )
            )
            .values("id", "short_citation", "final_score")
        )


class AttachmentManager(BaseManager):
    assessment_relation = "study__assessment"
