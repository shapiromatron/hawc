import pandas as pd
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
        """Returns a data frame, one row per study in study queryset

        Args:
            study_qs (QuerySet): A study queryset of studies

        Returns:
            pd.DataFrame: _description_
        """
        df1 = study_qs.flat_df()
        df2 = pd.DataFrame(
            data=study_qs.annotate(
                designs__source_display=sql_display("designs__source", constants.Source),
                designs__study_design_display=sql_display(
                    "designs__study_design", constants.StudyDesign
                ),
                designs__outcomes__system_display=sql_display(
                    "designs__outcomes__system", constants.HealthOutcomeSystem
                ),
                countries=str_m2m("designs__countries__name"),
                age_profile=Func(
                    F("designs__age_profile"),
                    Value("|"),
                    Value(""),
                    function="array_to_string",
                    output_field=CharField(max_length=256),
                ),
                chemical_name=str_m2m("designs__chemicals__name"),
                exposure_name=str_m2m("designs__exposures__name"),
                design_source=str_m2m("designs__source_display"),
                study_design=str_m2m("designs__study_design_display"),
                outcome_system=str_m2m("designs__outcomes__system_display"),
                outcome_effect=str_m2m("designs__outcomes__effect"),
                outcome_endpoint=str_m2m("designs__outcomes__endpoint"),
            ).values_list(
                "id",
                "study_design",
                "countries",
                "design_source",
                "age_profile",
                "chemical_name",
                "exposure_name",
                "outcome_system",
                "outcome_effect",
                "outcome_endpoint",
            ),
            columns=[
                "study_id",
                "study_design",
                "countries",
                "design_source",
                "age_profile",
                "chemical_name",
                "exposure_name",
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
