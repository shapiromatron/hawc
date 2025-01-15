import pandas as pd
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import (
    CharField,
    F,
    Func,
    Prefetch,
    QuerySet,
    Value,
)

from ..common.models import BaseManager, sql_display, str_m2m, to_display_array
from . import constants, models


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


class DesignManager(BaseManager):
    assessment_relation = "study__assessment"

    def get_queryset(self):
        return DesignQuerySet(self.model, using=self._db)

    def study_df(self, study_qs: QuerySet) -> pd.DataFrame:
        """Returns a data frame, one row per design in study queryset.

        Args:
            study_qs (QuerySet): A study queryset of studies

        Returns:
            pd.DataFrame: A dataframe, one row per study design.
        """
        df1 = study_qs.flat_df()
        df2 = pd.DataFrame(
            data=study_qs.annotate(
                design_summary=str_m2m("designs__summary"),
                _designs__study_design=sql_display("designs__study_design", constants.StudyDesign),
                study_design=str_m2m("_designs__study_design"),
                countries=str_m2m("designs__countries__name"),
                _design_source=sql_display("designs__source", constants.Source),
                design_source=str_m2m("_design_source"),
                age_profile=Func(
                    F("designs__age_profile"),
                    Value("|"),
                    Value(""),
                    function="array_to_string",
                    output_field=CharField(max_length=256),
                ),
                _participant_n=ArrayAgg("designs__participant_n", distinct=True),
                participant_n=Func(
                    F("_participant_n"),
                    Value("|"),
                    Value(""),
                    function="array_to_string",
                    output_field=CharField(max_length=256),
                ),
                chemical_name=str_m2m("designs__chemicals__name"),
                exposure_name=str_m2m("designs__exposures__name"),
                _exposure_measurement_type=Func(
                    F("designs__exposures__measurement_type"),
                    Value("|"),
                    Value(""),
                    function="array_to_string",
                    output_field=CharField(max_length=256),
                ),
                exposure_measurement_type=str_m2m("_exposure_measurement_type"),
                _exposure_biomonitoring_matrix=sql_display(
                    "designs__exposures__biomonitoring_matrix",
                    constants.BiomonitoringMatrix,
                    default="",
                ),
                exposure_biomonitoring_matrix=str_m2m("_exposure_biomonitoring_matrix"),
                _exposure_route=sql_display(
                    "designs__exposures__exposure_route", constants.ExposureRoute
                ),
                exposure_route=str_m2m("_exposure_route"),
                _outcomes__system=sql_display(
                    "designs__outcomes__system", constants.HealthOutcomeSystem
                ),
                outcome_system=str_m2m("_outcomes__system"),
                outcome_effect=str_m2m("designs__outcomes__effect"),
                outcome_endpoint=str_m2m("designs__outcomes__endpoint"),
            ).values_list(
                "id",
                "design_summary",
                "study_design",
                "countries",
                "design_source",
                "age_profile",
                "participant_n",
                "chemical_name",
                "exposure_name",
                "exposure_measurement_type",
                "exposure_biomonitoring_matrix",
                "exposure_route",
                "outcome_system",
                "outcome_effect",
                "outcome_endpoint",
            ),
            columns=[
                "study_id",
                "design_summary",
                "study_design",
                "countries",
                "design_source",
                "age_profile",
                "participant_n",
                "chemical_name",
                "exposure_name",
                "exposure_measurement_type",
                "exposure_biomonitoring_matrix",
                "exposure_route",
                "outcome_system",
                "outcome_effect",
                "outcome_endpoint",
            ],
        )
        df3 = (
            df1.merge(df2, how="right", left_on="id", right_on="study_id")
            .drop(
                columns=[
                    "study_id",
                    "coi_reported",
                    "coi_details",
                    "funding_source",
                    "study_identifier",
                    "contact_author",
                    "ask_author",
                    "published",
                    "summary",
                ]
            )
            .dropna()
            .rename(columns={"id": "study_id"})
        )
        df3.loc[:, "age_profile"] = to_display_array(df3.age_profile, constants.AgeProfile)
        return df3


class ChemicalQuerySet(QuerySet):
    pass


class ChemicalManager(BaseManager):
    assessment_relation = "design__study__assessment"

    def get_queryset(self):
        return ChemicalQuerySet(self.model, using=self._db)


class ExposureQuerySet(QuerySet):
    pass


class ExposureManager(BaseManager):
    assessment_relation = "design__study__assessment"

    def get_queryset(self):
        return ExposureQuerySet(self.model, using=self._db)


class ExposureLevelQuerySet(QuerySet):
    pass


class ExposureLevelManager(BaseManager):
    assessment_relation = "design__study__assessment"

    def get_queryset(self):
        return ExposureLevelQuerySet(self.model, using=self._db)


class OutcomeQuerySet(QuerySet):
    pass


class OutcomeManager(BaseManager):
    assessment_relation = "design__study__assessment"

    def get_queryset(self):
        return OutcomeQuerySet(self.model, using=self._db)


class AdjustmentFactorQuerySet(QuerySet):
    pass


class AdjustmentFactorManager(BaseManager):
    assessment_relation = "design__study__assessment"

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


class DataExtractionManager(BaseManager):
    assessment_relation = "design__study__assessment"

    def get_queryset(self):
        return DataExtractionQuerySet(self.model, using=self._db)
