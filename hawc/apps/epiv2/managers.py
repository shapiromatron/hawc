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
from ..study.managers import study_df_annotations, study_df_mapping
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

    def complete_df(self) -> pd.DataFrame:
        mapping = {
            # study
            **study_df_mapping("study-", "design__study__"),
            # design
            "design-pk": "design__pk",
            # "design-url": "design__get_absolute_url", #todo
            "design-summary": "design__summary",
            "design-study_name": "design__study_name",
            "design-study_design": sql_display("design__study_design", constants.StudyDesign),
            "design-source": sql_display("design__source", constants.Source),
            "design-age_profile": "design__age_profile",  # todo
            "design-age_description": "design__age_description",
            "design-sex": sql_display("design__sex", constants.Sex),
            "design-race": "design__race",
            "design-participant_n": "design__participant_n",
            "design-years_enrolled": "design__years_enrolled",
            "design-years_followup": "design__years_followup",
            "design-countries": "design__countries__name",
            "design-region": "design__region",
            "design-criteria": "design__criteria",
            "design-susceptibility": "design__susceptibility",
            "design-comments": "design__comments",
            "design-created": "design__created",
            "design-last_updated": "design__last_updated",
            # chemical
            "chemical-pk": "exposure_level__chemical__pk",
            "chemical-name": "exposure_level__chemical__name",
            "chemical-DTSXID": "exposure_level__chemical__dsstox__dtxsid",
            "chemical-created": "exposure_level__chemical__created",
            "chemical-last_updated": "exposure_level__chemical__last_updated",
            # exposure
            "exposure-pk": "exposure_level__exposure_measurement__pk",
            "exposure-name": "exposure_level__exposure_measurement__name",
            "exposure-measurement_type": "exposure_level__exposure_measurement__measurement_type",
            "exposure-biomonitoring_matrix": sql_display(
                "exposure_level__exposure_measurement__biomonitoring_matrix",  # todo fix default display
                constants.BiomonitoringMatrix,
            ),
            "exposure-biomonitoring_source": sql_display(
                "exposure_level__exposure_measurement__biomonitoring_source",  # todo fix default display
                constants.BiomonitoringSource,
            ),
            "exposure-measurement_timing": "exposure_level__exposure_measurement__measurement_timing",
            "exposure-exposure_route": sql_display(
                "exposure_level__exposure_measurement__exposure_route", constants.ExposureRoute
            ),
            "exposure-measurement_method": "exposure_level__exposure_measurement__measurement_method",
            "exposure-comments": "exposure_level__exposure_measurement__comments",
            "exposure-created": "exposure_level__exposure_measurement__created",
            "exposure-last_updated": "exposure_level__exposure_measurement__last_updated",
            # exposure level
            "exposure_level-pk": "exposure_level__pk",
            "exposure_level-name": "exposure_level__name",
            "exposure_level-sub_population": "exposure_level__sub_population",
            "exposure_level-median": "exposure_level__median",
            "exposure_level-mean": "exposure_level__mean",
            "exposure_level-variance": "exposure_level__variance",
            "exposure_level-variance_type": sql_display(
                "exposure_level__variance_type", constants.VarianceType
            ),
            "exposure_level-units": "exposure_level__units",
            "exposure_level-ci_lcl": "exposure_level__ci_lcl",
            "exposure_level-percentile_25": "exposure_level__percentile_25",
            "exposure_level-percentile_75": "exposure_level__percentile_75",
            "exposure_level-ci_ucl": "exposure_level__ci_ucl",
            "exposure_level-ci_type": sql_display(
                "exposure_level__ci_type", constants.ConfidenceIntervalType
            ),
            "exposure_level-negligible_exposure": "exposure_level__negligible_exposure",
            "exposure_level-data_location": "exposure_level__data_location",
            "exposure_level-comments": "exposure_level__comments",
            "exposure_level-created": "exposure_level__created",
            "exposure_level-last_updated": "exposure_level__last_updated",
            # outcome
            "outcome-pk": "outcome__pk",
            "outcome-system": sql_display("outcome__system", constants.HealthOutcomeSystem),
            "outcome-effect": "outcome__effect",
            "outcome-effect_detail": "outcome__effect_detail",
            "outcome-comments": "outcome__comments",
            "outcome-created": "outcome__created",
            "outcome-last_updated": "outcome__last_updated",
            # adj factor
            "adjustment_factor-pk": "factors__pk",
            "adjustment_factor-name": "factors__name",
            "adjustment_factor-description": "factors__description",
            "adjustment_factor-comments": "factors__comments",
            "adjustment_factor-created": "factors__created",
            "adjustment_factor-last_updated": "factors__last_updated",
            # data extraction
            "data_extraction-pk": "pk",
            "data_extraction-sub_population": "sub_population",
            "data_extraction-outcome_measurement_timing": "outcome_measurement_timing",
            "data_extraction-effect_estimate_type": "effect_estimate_type",
            "data_extraction-effect_estimate": "effect_estimate",
            "data_extraction-ci_lcl": "ci_lcl",
            "data_extraction-ci_ucl": "ci_ucl",
            "data_extraction-ci_type": sql_display("ci_type", constants.ConfidenceIntervalType),
            "data_extraction-units": "units",
            "data_extraction-variance_type": sql_display("variance_type", constants.VarianceType),
            "data_extraction-variance": "variance",
            "data_extraction-n": "n",
            "data_extraction-p_value": "p_value",
            "data_extraction-significant": sql_display("significant", constants.Significant),
            "data_extraction-group": "group",
            "data_extraction-exposure_rank": "exposure_rank",
            "data_extraction-exposure_transform": "exposure_transform",
            "data_extraction-outcome_transform": "outcome_transform",
            "data_extraction-confidence": "confidence",
            "data_extraction-data_location": "data_location",
            "data_extraction-effect_description": "effect_description",
            "data_extraction-statistical_method": "statistical_method",
            "data_extraction-comments": "comments",
            "data_extraction-created": "created",
            "data_extraction-last_updated": "last_updated",
        }
        qs = self.annotate(
            **study_df_annotations("design__study__"),
            design__countries__name=str_m2m("design__countries__name"),
            exposure_level__exposure_measurement__measurement_type=Func(
                F("exposure_level__exposure_measurement__measurement_type"),
                Value(", "),
                Value(""),
                function="array_to_string",
                output_field=CharField(max_length=256),
            ),
        ).values_list(*list(mapping.values()))
        return pd.DataFrame(data=qs, columns=list(mapping.keys()))


class DataExtractionManager(BaseManager):
    assessment_relation = "design__study__assessment"

    def get_queryset(self):
        return DataExtractionQuerySet(self.model, using=self._db)
