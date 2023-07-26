import pandas as pd
from django.contrib.postgres.aggregates import StringAgg
from django.db.models import QuerySet

from ..common.models import BaseManager


class DesignQuerySet(QuerySet):
    def published_only(self, published_only: bool):
        return self.filter(study__published=True) if published_only else self

    def flat_df(self) -> pd.DataFrame:
        names = [
            "id",
            "study_id",
            "name",
            "design__value",
            "study_setting__value",
            "countries_",
            "states_",
            "ecoregions_",
            "habitats_",
            "habitats_as_reported",
            "climates_",
            "climates_as_reported",
            "comments",
            "created",
            "last_updated",
        ]
        return pd.DataFrame(
            data=self.annotate(
                countries_=StringAgg("countries__name", delimiter="|", distinct=True, default=""),
                states_=StringAgg("states__name", delimiter="|", distinct=True, default=""),
                ecoregions_=StringAgg(
                    "ecoregions__value", delimiter="|", distinct=True, default=""
                ),
                habitats_=StringAgg("habitats__value", delimiter="|", distinct=True, default=""),
                climates_=StringAgg("climates__value", delimiter="|", distinct=True, default=""),
            ).values_list(*names),
            columns=names,
        ).rename(
            columns={
                "study_setting__value": "study_setting",
                "countries_": "countries",
                "states_": "states",
                "ecoregions_": "ecoregions",
            }
        )


class DesignManager(BaseManager):
    assessment_relation = "study__assessment"

    def get_queryset(self):
        return DesignQuerySet(self.model, using=self._db)


class CauseQuerySet(QuerySet):
    def published_only(self, published_only: bool):
        return self.filter(study__published=True) if published_only else self

    def flat_df(self) -> pd.DataFrame:
        names = [
            "id",
            "study_id",
            "name",
            "term__name",
            "biological_organization__value",
            "species",
            "level",
            "level_value",
            "level_units",
            "duration",
            "duration_value",
            "duration_units",
            "exposure",
            "exposure_value",
            "exposure_units",
            "as_reported",
            "comments",
            "created",
            "last_updated",
        ]
        return pd.DataFrame(data=self.values_list(*names), columns=names).rename(
            columns={
                "term__name": "term",
                "biological_organization": "biological_organization",
            }
        )


class CauseManager(BaseManager):
    assessment_relation = "study__assessment"

    def get_queryset(self):
        return CauseQuerySet(self.model, using=self._db)


class EffectQuerySet(QuerySet):
    def published_only(self, published_only: bool):
        return self.filter(study__published=True) if published_only else self

    def flat_df(self) -> pd.DataFrame:
        names = [
            "id",
            "study_id",
            "name",
            "term__name",
            "biological_organization__value",
            "species",
            "units",
            "as_reported",
            "comments",
            "created",
            "last_updated",
        ]
        return pd.DataFrame(data=self.values_list(*names), columns=names).rename(
            columns={
                "term__name": "term",
                "biological_organization": "biological_organization",
            }
        )


class EffectManager(BaseManager):
    assessment_relation = "study__assessment"

    def get_queryset(self):
        return EffectQuerySet(self.model, using=self._db)


class ResultQuerySet(QuerySet):
    def published_only(self, published_only: bool):
        return self.filter(design__study__published=True) if published_only else self

    def complete(self):
        return self.select_related(
            "design__study",
            "design__study_setting",
            "cause__term",
            "cause__biological_organization",
            "effect__term",
            "effect__biological_organization",
            "statistical_sig_type",
            "measure_type",
            "variability",
        ).prefetch_related(
            "design__countries",
            "design__states",
            "design__ecoregions",
            "design__habitats",
            "design__climates",
        )

    def flat_df(self) -> pd.DataFrame:
        names = [
            "id",
            "design_id",
            "name",
            "cause_id",
            "effect_id",
            "sort_order",
            "relationship_direction",
            "relationship_comment",
            "measure_type__value",
            "measure_value",
            "derived_value",
            "sample_size",
            "variability__value",
            "low_variability",
            "upper_variability",
            "modifying_factors",
            "modifying_factors_comment",
            "statistical_sig_type__value",
            "statistical_sig_value",
            "comments",
            "created",
            "last_updated",
        ]
        return pd.DataFrame(data=self.values_list(*names), columns=names).rename(
            columns={
                "measure_type__value": "measure_type",
                "variability__value": "variability",
                "statistical_sig_type__value": "statistical_sig_type",
            }
        )


class ResultManager(BaseManager):
    assessment_relation = "design__study__assessment"

    def get_queryset(self):
        return ResultQuerySet(self.model, using=self._db)
