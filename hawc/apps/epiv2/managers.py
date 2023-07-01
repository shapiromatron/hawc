import pandas as pd
from django.contrib.postgres.aggregates import StringAgg
from django.db.models import (
    CharField,
    Choices,
    F,
    Func,
    Prefetch,
    QuerySet,
    Value,
)

from ..common.models import BaseManager, to_display_array, to_sql_display
from . import constants, models


def enum_dict(choice_enum: type[Choices]) -> dict:
    return {k: v for k, v in choice_enum.choices}


def map_array(df: pd.DataFrame, key: str, choice_enum: type[Choices]):
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
            countries_=StringAgg("countries__name", delimiter="|", distinct=True, default=""),
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

    def study_df(self, study_qs: QuerySet) -> pd.DataFrame:
        """Returns a data frame, one row per study in study queryset

        Args:
            study_qs (QuerySet): A study queryset of studies

        Returns:
            pd.DataFrame: _description_
        """
        study_df = study_qs.flat_df()
        qs = to_sql_display(study_qs, "designs__source", constants.Source)
        qs = to_sql_display(qs, "designs__study_design", constants.StudyDesign)
        qs = to_sql_display(qs, "designs__outcomes__system", constants.HealthOutcomeSystem)
        qs = qs.annotate(
            study_design=StringAgg(
                "designs__study_design_display", delimiter="|", distinct=True, default=""
            ),
            countries=StringAgg(
                "designs__countries__name", delimiter="|", distinct=True, default=""
            ),
            design_source=StringAgg(
                "designs__source_display", delimiter="|", distinct=True, default=""
            ),
            age_profile=Func(
                F("designs__age_profile"),
                Value("|"),
                Value(""),
                function="array_to_string",
                output_field=CharField(max_length=256),
            ),
            chemical_name=StringAgg(
                "designs__chemicals__name", delimiter="|", distinct=True, default=""
            ),
            exposure_name=StringAgg(
                "designs__exposures__name", delimiter="|", distinct=True, default=""
            ),
            outcome_systems=StringAgg(
                "designs__outcomes__system_display", delimiter="|", distinct=True, default=""
            ),
            outcome_effects=StringAgg(
                "designs__outcomes__effect", delimiter="|", distinct=True, default=""
            ),
            outcome_endpoints=StringAgg(
                "designs__outcomes__endpoint", delimiter="|", distinct=True, default=""
            ),
        ).values_list(
            "id",
            "study_design",
            "countries",
            "design_source",
            "age_profile",
            "chemical_name",
            "exposure_name",
            "outcome_systems",
            "outcome_effects",
            "outcome_endpoints",
        )
        df2 = pd.DataFrame(
            data=qs,
            columns=[
                "study_id",
                "study_design",
                "countries",
                "design_source",
                "age_profile",
                "chemical_name",
                "exposure_name",
                "outcome_systems",
                "outcome_effects",
                "outcome_endpoints",
            ],
        )
        df3 = (
            study_df.merge(df2, how="right", left_on="id", right_on="study_id")
            .drop(columns=["study_id"])
            .dropna()
        )
        df3.loc[:, "age_profile"] = to_display_array(df3.age_profile, constants.AgeProfile)
        return df3


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
