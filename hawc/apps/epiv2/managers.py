from typing import Type

import pandas as pd
from django.contrib.postgres.aggregates import StringAgg
from django.db.models import Choices, Prefetch, QuerySet

from ..common.models import BaseManager
from . import constants, models


def enum_dict(choice_enum: Type[Choices]) -> dict:
    return {k: v for k, v in choice_enum.choices}


def map_array(df: pd.DataFrame, key: str, choice_enum: Type[Choices]):
    mapped = {k: v for k, v in choice_enum.choices}
    df.loc[:, key] = df.apply(lambda row: "|".join(mapped[item] for item in row[key]), axis=1)


class DesignQuerySet(QuerySet):
    def complete(self):
        return self.select_related("study").prefetch_related(
            "countries",
            "exposures",
            "outcomes",
            Prefetch(
                "chemicals",
                queryset=models.Chemical.objects.select_related("dsstox"),
            ),
            "adjustment_factors",
            Prefetch(
                "exposure_levels",
                queryset=models.ExposureLevel.objects.select_related(
                    "chemical", "exposure_measurement"
                ),
            ),
            Prefetch(
                "data_extractions",
                queryset=models.DataExtraction.objects.select_related(
                    "factors", "outcome", "exposure_level"
                ),
            ),
        )

    def flat_df(self) -> pd.DataFrame:
        names = [
            "id",
            "study_id",
            "summary",
            "study_name",
            "study_design",
            "source",
            "age_profile",
            "age_description",
            "sex",
            "race",
            "participant_n",
            "years_enrolled",
            "years_followup",
            "countries_",
            "region",
            "criteria",
            "susceptibility",
            "comments",
            "created",
            "last_updated",
        ]
        qs = self.annotate(
            countries_=StringAgg("countries__name", delimiter="|", distinct=True),
        ).values_list(*names)
        df = (
            pd.DataFrame(
                data=qs,
                columns=names,
            )
            .rename(
                columns={
                    "countries_": "countries",
                }
            )
            .replace(
                {
                    "study_design": enum_dict(constants.StudyDesign),
                    "source": enum_dict(constants.Source),
                    "sex": enum_dict(constants.Sex),
                }
            )
        )
        map_array(df, "age_profile", constants.AgeProfile)
        return df


class DesignManager(BaseManager):
    assessment_relation = "study__assessment"

    def get_queryset(self):
        return DesignQuerySet(self.model, using=self._db)


class ChemicalQuerySet(QuerySet):
    def flat_df(self) -> pd.DataFrame:
        names = [
            "id",
            "design_id",
            "name",
            "dsstox__dtxsid",
            "created",
            "last_updated",
        ]
        qs = self.values_list(*names)
        df = pd.DataFrame(data=qs, columns=names).rename(
            columns={
                "dsstox__dtxsid": "dtxsid",
            }
        )
        return df


class ChemicalManager(BaseManager):
    assessment_relation = "studypopulation__study__assessment"

    def get_queryset(self):
        return ChemicalQuerySet(self.model, using=self._db)


class ExposureQuerySet(QuerySet):
    def flat_df(self) -> pd.DataFrame:
        names = [
            "id",
            "name",
            "design_id",
            "measurement_type",
            "biomonitoring_matrix",
            "biomonitoring_source",
            "measurement_timing",
            "exposure_route",
            "measurement_method",
            "comments",
            "created",
            "last_updated",
        ]
        qs = self.values_list(*names)
        df = (
            pd.DataFrame(data=qs, columns=names)
            .assign(measurement_type=lambda df: df.measurement_type.str.join(sep="|"))
            .replace(
                {
                    "biomonitoring_matrix": enum_dict(constants.BiomonitoringMatrix),
                    "biomonitoring_source": enum_dict(constants.BiomonitoringSource),
                    "exposure_route": enum_dict(constants.ExposureRoute),
                }
            )
        )
        return df


class ExposureManager(BaseManager):
    assessment_relation = "studypopulation__study__assessment"

    def get_queryset(self):
        return ExposureQuerySet(self.model, using=self._db)


class ExposureLevelQuerySet(QuerySet):
    def flat_df(self) -> pd.DataFrame:
        names = [
            "id",
            "name",
            "design_id",
            "chemical_id",
            "exposure_measurement_id",
            "sub_population",
            "median",
            "mean",
            "variance",
            "variance_type",
            "units",
            "ci_lcl",
            "percentile_25",
            "percentile_75",
            "ci_ucl",
            "ci_type",
            "negligible_exposure",
            "data_location",
            "comments",
            "created",
            "last_updated",
        ]
        qs = self.values_list(*names)
        df = pd.DataFrame(data=qs, columns=names).replace(
            {
                "variance_type": enum_dict(constants.VarianceType),
                "ci_type": enum_dict(constants.ConfidenceIntervalType),
            }
        )
        return df


class ExposureLevelManager(BaseManager):
    assessment_relation = "studypopulation__study__assessment"

    def get_queryset(self):
        return ExposureLevelQuerySet(self.model, using=self._db)


class OutcomeQuerySet(QuerySet):
    def flat_df(self) -> pd.DataFrame:
        names = [
            "id",
            "design_id",
            "system",
            "effect",
            "effect_detail",
            "endpoint",
            "comments",
            "created",
            "last_updated",
        ]
        qs = self.values_list(*names)
        df = pd.DataFrame(data=qs, columns=names).replace(
            {
                "system": enum_dict(constants.HealthOutcomeSystem),
            }
        )
        return df


class OutcomeManager(BaseManager):
    assessment_relation = "studypopulation__study__assessment"

    def get_queryset(self):
        return OutcomeQuerySet(self.model, using=self._db)


class AdjustmentFactorQuerySet(QuerySet):
    def flat_df(self) -> pd.DataFrame:
        names = [
            "id",
            "design_id",
            "name",
            "description",
            "comments",
            "created",
            "last_updated",
        ]
        qs = self.values_list(*names)
        df = pd.DataFrame(data=qs, columns=names).replace(
            {
                "system": enum_dict(constants.HealthOutcomeSystem),
            }
        )
        return df


class AdjustmentFactorManager(BaseManager):
    assessment_relation = "studypopulation__study__assessment"

    def get_queryset(self):
        return AdjustmentFactorQuerySet(self.model, using=self._db)


class DataExtractionQuerySet(QuerySet):
    def published_only(self, published_only: bool):
        return self.filter(design__study__published=True) if published_only else self

    def complete(self):
        return self.select_related(
            "design__study",
            "exposure_level__chemical__dsstox",
            "exposure_level__exposure_measurement",
            "outcome",
            "factors",
        ).prefetch_related("design__countries")

    def flat_df(self) -> pd.DataFrame:
        names = [
            "id",
            "design_id",
            "outcome_id",
            "exposure_level_id",
            "sub_population",
            "outcome_measurement_timing",
            "effect_estimate_type",
            "effect_estimate",
            "ci_lcl",
            "ci_ucl",
            "ci_type",
            "units",
            "variance_type",
            "variance",
            "n",
            "p_value",
            "significant",
            "group",
            "exposure_rank",
            "exposure_transform",
            "outcome_transform",
            "factors_id",
            "confidence",
            "data_location",
            "effect_description",
            "statistical_method",
            "comments",
            "created",
            "last_updated",
        ]
        qs = models.DataExtraction.objects.values_list(*names)
        df = pd.DataFrame(data=qs, columns=names).replace(
            {
                "ci_type": enum_dict(constants.ConfidenceIntervalType),
                "variance_type": enum_dict(constants.VarianceType),
                "significant": enum_dict(constants.Significant),
            }
        )
        return df


class DataExtractionManager(BaseManager):
    assessment_relation = "design__study__assessment"

    def get_queryset(self):
        return DataExtractionQuerySet(self.model, using=self._db)
