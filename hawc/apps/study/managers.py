import pandas as pd
from django.contrib.postgres.aggregates import StringAgg
from django.db import models
from django.db.models import Q, QuerySet

from ..common.models import BaseManager
from ..lit.constants import ReferenceDatabase


class StudyQuerySet(QuerySet):
    def flat_df(self) -> pd.DataFrame:
        names = [
            "id",
            "pmid",
            "hero",
            "doi",
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
        ]
        return pd.DataFrame(
            data=self.annotate(
                pmid=StringAgg(
                    "identifiers__unique_id",
                    filter=Q(identifiers__database=ReferenceDatabase.PUBMED),
                    delimiter="|",
                    distinct=True,
                ),
                hero=StringAgg(
                    "identifiers__unique_id",
                    filter=Q(identifiers__database=ReferenceDatabase.HERO),
                    delimiter="|",
                    distinct=True,
                ),
                doi=StringAgg(
                    "identifiers__unique_id",
                    filter=Q(identifiers__database=ReferenceDatabase.DOI),
                    delimiter="|",
                    distinct=True,
                ),
            ).values_list(*names),
            columns=names,
        )


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
