import pandas as pd
from django.contrib.postgres.aggregates import StringAgg
from django.db import models
from django.db.models import Q, QuerySet

from ..common.models import BaseManager, sql_display
from ..lit.constants import ReferenceDatabase
from . import constants


class StudyQuerySet(QuerySet):
    def flat_df(self) -> pd.DataFrame:
        return pd.DataFrame(
            data=self.annotate(
                pmid=StringAgg(
                    "identifiers__unique_id",
                    filter=Q(identifiers__database=ReferenceDatabase.PUBMED),
                    delimiter="|",
                    distinct=True,
                    default="",
                ),
                hero=StringAgg(
                    "identifiers__unique_id",
                    filter=Q(identifiers__database=ReferenceDatabase.HERO),
                    delimiter="|",
                    distinct=True,
                    default="",
                ),
                doi=StringAgg(
                    "identifiers__unique_id",
                    filter=Q(identifiers__database=ReferenceDatabase.DOI),
                    delimiter="|",
                    distinct=True,
                    default="",
                ),
                coi_reported_display=sql_display("coi_reported", constants.CoiReported),
            ).values_list(
                "id",
                "pmid",
                "hero",
                "doi",
                "short_citation",
                "full_citation",
                "coi_reported_display",
                "coi_details",
                "funding_source",
                "study_identifier",
                "contact_author",
                "ask_author",
                "published",
                "summary",
            ),
            columns=[
                "id",
                "PMID",
                "HERO ID",
                "DOI",
                "short_citation",
                "full_citation",
                "coi_reported",
                "coi_details",
                "funding_source",
                "study_identifier",
                "contact_author",
                "ask_author",
                "published",
                "summary",
            ],
        )

    def published_only(self, published_only: bool):
        """If True, return only published studies. If False, all studies"""
        return self.filter(published=True) if published_only else self


class StudyManager(BaseManager):
    assessment_relation = "assessment"

    def get_queryset(self):
        return StudyQuerySet(self.model, using=self._db)

    def published(self, assessment_id=None):
        return self.get_qs(assessment_id).filter(published=True)

    def get_choices(self, assessment_id=None):
        return self.get_qs(assessment_id).values_list("id", "short_citation")

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
