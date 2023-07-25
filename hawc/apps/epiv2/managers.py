import pandas as pd
from django.contrib.postgres.aggregates import StringAgg
from django.db.models import (
    CharField,
    F,
    Func,
    Prefetch,
    QuerySet,
    Value,
)

from ..common.models import BaseManager, sql_display, to_display_array
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
                countries=StringAgg(
                    "designs__countries__name", delimiter="|", distinct=True, default=""
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
                design_source=StringAgg(
                    "designs__source_display", delimiter="|", distinct=True, default=""
                ),
                study_design=StringAgg(
                    "designs__study_design_display", delimiter="|", distinct=True, default=""
                ),
                outcome_system=StringAgg(
                    "designs__outcomes__system_display", delimiter="|", distinct=True, default=""
                ),
                outcome_effect=StringAgg(
                    "designs__outcomes__effect", delimiter="|", distinct=True, default=""
                ),
                outcome_endpoint=StringAgg(
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
